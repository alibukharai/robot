"""
Main application for Digital Waiter Robot
Orchestrates all components: wake word, ASR, intent, menu, order, TTS
"""

import sys
import logging
import yaml
import signal
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.audio.microphone import Microphone
from src.wake_word.detector import WakeWordDetector
from src.speech.recognizer import SpeechRecognizer
from src.speech.synthesizer import SpeechSynthesizer
from src.menu.manager import MenuManager
from src.intent.processor import IntentProcessor, Intent
from src.order.manager import OrderManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/robot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DigitalWaiterRobot:
    """
    Digital Waiter Robot main application.
    
    Orchestrates all components to provide voice-activated restaurant service.
    
    Features:
    - Wake word detection
    - Speech recognition
    - Intent understanding
    - Menu management
    - Order tracking
    - Text-to-speech responses
    """
    
    def __init__(self, config_file: str = "config/settings.yaml"):
        """
        Initialize the robot.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.running = False
        
        # Initialize components
        self.microphone: Optional[Microphone] = None
        self.wake_word_detector: Optional[WakeWordDetector] = None
        self.speech_recognizer: Optional[SpeechRecognizer] = None
        self.speech_synthesizer: Optional[SpeechSynthesizer] = None
        self.menu_manager: Optional[MenuManager] = None
        self.intent_processor: Optional[IntentProcessor] = None
        self.order_manager: Optional[OrderManager] = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Digital Waiter Robot initialized")
        
    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from: {self.config_file}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
            
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("Shutdown signal received")
        self.stop()
        sys.exit(0)
        
    def initialize_components(self) -> bool:
        """
        Initialize all robot components.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Audio configuration
            audio_config = self.config.get('audio', {})
            
            # Initialize microphone
            logger.info("Initializing microphone...")
            self.microphone = Microphone(
                sample_rate=audio_config.get('sample_rate', 16000),
                channels=audio_config.get('channels', 1),
                chunk_size=audio_config.get('chunk_size', 1024),
                device_name=audio_config.get('device_name')
            )
            
            # Initialize wake word detector
            if self.config.get('wake_word', {}).get('enabled', True):
                logger.info("Initializing wake word detector...")
                wake_config = self.config.get('wake_word', {})
                self.wake_word_detector = WakeWordDetector(
                    model_name=wake_config.get('model', 'hey_jarvis'),
                    threshold=wake_config.get('threshold', 0.5)
                )
            
            # Initialize speech recognizer
            logger.info("Initializing speech recognizer...")
            asr_config = self.config.get('asr', {})
            self.speech_recognizer = SpeechRecognizer(
                model_path=asr_config.get('model_path', 'models/vosk-model-small-en-us-0.15'),
                sample_rate=audio_config.get('sample_rate', 16000)
            )
            
            # Initialize speech synthesizer
            logger.info("Initializing speech synthesizer...")
            tts_config = self.config.get('tts', {})
            self.speech_synthesizer = SpeechSynthesizer(
                rate=tts_config.get('rate', 150),
                volume=tts_config.get('volume', 0.9),
                voice_id=tts_config.get('voice')
            )
            
            # Initialize menu manager
            logger.info("Initializing menu manager...")
            menu_config = self.config.get('menu', {})
            self.menu_manager = MenuManager(
                menu_file=menu_config.get('file', 'config/menu.yaml')
            )
            
            # Initialize intent processor
            logger.info("Initializing intent processor...")
            self.intent_processor = IntentProcessor()
            
            # Initialize order manager
            logger.info("Initializing order manager...")
            order_config = self.config.get('orders', {})
            self.order_manager = OrderManager(
                save_directory=order_config.get('save_directory', 'data/orders'),
                file_format=order_config.get('file_format', 'json')
            )
            
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            return False
            
    def speak(self, text: str) -> None:
        """
        Speak text through TTS.
        
        Args:
            text: Text to speak
        """
        if self.speech_synthesizer:
            logger.info(f"Robot: {text}")
            self.speech_synthesizer.speak(text)
        else:
            logger.warning("TTS not initialized")
            
    def listen_for_wake_word(self) -> bool:
        """
        Listen for wake word.
        
        Returns:
            True if wake word detected
        """
        if not self.wake_word_detector or not self.microphone:
            return True  # Skip wake word if not configured
            
        logger.info("Listening for wake word...")
        
        try:
            while self.running:
                # Read audio chunk
                audio_chunk = self.microphone.read_chunk()
                if audio_chunk is None:
                    continue
                    
                # Check for wake word
                if self.wake_word_detector.detect(audio_chunk):
                    logger.info("Wake word detected!")
                    return True
                    
        except Exception as e:
            logger.error(f"Error during wake word detection: {e}")
            return False
            
        return False
        
    def listen_for_order(self) -> Optional[str]:
        """
        Listen for customer order speech.
        
        Returns:
            Recognized text, or None if failed
        """
        if not self.microphone or not self.speech_recognizer:
            logger.error("Microphone or ASR not initialized")
            return None
            
        logger.info("Listening for order...")
        self.speak("I'm listening. What would you like to order?")
        
        try:
            # Record audio until silence
            audio_config = self.config.get('audio', {})
            
            logger.debug(f"Recording with settings: "
                        f"silence_threshold={audio_config.get('silence_threshold', 500)}, "
                        f"silence_duration={audio_config.get('silence_duration', 1.5)}s, "
                        f"max_duration={audio_config.get('max_recording_duration', 10)}s")
            
            audio_data = self.microphone.record_until_silence(
                silence_threshold=audio_config.get('silence_threshold', 500),
                silence_duration=audio_config.get('silence_duration', 1.5),
                max_duration=audio_config.get('max_recording_duration', 10)
            )
            
            if audio_data is None:
                logger.warning("No audio recorded - possible microphone issue")
                self.speak("I couldn't hear anything. Please try speaking closer to the microphone.")
                return None
                
            logger.info(f"Recorded {len(audio_data)} bytes of audio data")
            
            # Save audio for debugging if enabled
            if logger.level <= logging.DEBUG:
                debug_file = self.speech_recognizer.save_audio_for_debug(audio_data)
                logger.debug(f"Debug audio saved to: {debug_file}")
                
            # Recognize speech
            text = self.speech_recognizer.recognize(audio_data)
            
            if text:
                logger.info(f"Successfully recognized: '{text}'")
            else:
                logger.warning("Speech recognition returned no text")
                self.speak("I couldn't understand what you said. Please try again.")
                
            return text
            
        except Exception as e:
            logger.error(f"Error during speech recognition: {e}")
            logger.debug(f"Error details: ", exc_info=True)
            self.speak("Sorry, I encountered an error while listening. Please try again.")
            return None
            
    def process_order(self, text: str) -> bool:
        """
        Process customer order text.
        
        Args:
            text: Recognized speech text
            
        Returns:
            True if order processed successfully
        """
        if not text:
            return False
            
        # Get all menu item names for matching
        menu_items = [item['name'] for item in self.menu_manager.get_all_items()]
        
        # Process intent
        result = self.intent_processor.process(text, menu_items)
        intent = result['intent']
        entities = result['entities']
        
        logger.info(f"Intent: {intent.value}, Entities: {entities}")
        
        # Handle different intents
        if intent == Intent.ORDER:
            return self._handle_order_intent(entities)
        elif intent == Intent.SUGGEST:
            return self._handle_suggest_intent()
        elif intent == Intent.CONFIRM:
            return self._handle_confirm_intent()
        elif intent == Intent.CANCEL:
            return self._handle_cancel_intent()
        elif intent == Intent.INFO:
            return self._handle_info_intent(entities)
        elif intent == Intent.DONE:
            return self._handle_done_intent()
        else:
            self.speak("I'm sorry, I didn't understand. Can you repeat that?")
            return False
            
    def _handle_order_intent(self, entities: dict) -> bool:
        """Handle ORDER intent."""
        items = entities.get('items', [])
        quantity = entities.get('quantity', 1)
        
        if not items:
            self.speak("I didn't catch which item you'd like. Can you repeat?")
            return False
            
        # Process each item
        for item_name in items:
            # Search for item in menu
            menu_item = self.menu_manager.search_item(item_name)
            
            if menu_item:
                # Add to order
                self.order_manager.add_item(
                    item_name=menu_item['name'],
                    quantity=quantity,
                    price=menu_item.get('price', 0.0),
                    category=menu_item.get('category', ''),
                    modifiers=entities.get('modifiers', [])
                )
                
                price_total = menu_item['price'] * quantity
                self.speak(f"Added {quantity} {menu_item['name']} to your order. "
                         f"That's ${price_total:.2f}.")
            else:
                self.speak(f"Sorry, I couldn't find {item_name} on our menu. "
                         f"Would you like to hear our suggestions?")
                return False
                
        return True
        
    def _handle_suggest_intent(self) -> bool:
        """Handle SUGGEST intent."""
        popular_items = self.menu_manager.get_popular_items(max_items=3)
        
        if not popular_items:
            self.speak("Let me tell you about our menu.")
            return True
            
        suggestions = []
        for item in popular_items:
            suggestions.append(f"{item['name']} for ${item['price']:.2f}")
            
        suggestion_text = "Our popular items are: " + ", ".join(suggestions)
        self.speak(suggestion_text)
        return True
        
    def _handle_confirm_intent(self) -> bool:
        """Handle CONFIRM intent."""
        self.speak("Great! Your order is confirmed.")
        return True
        
    def _handle_cancel_intent(self) -> bool:
        """Handle CANCEL intent."""
        self.speak("No problem. What would you like instead?")
        return True
        
    def _handle_info_intent(self, entities: dict) -> bool:
        """Handle INFO intent."""
        items = entities.get('items', [])
        
        if not items:
            self.speak("Which item would you like to know about?")
            return False
            
        for item_name in items:
            menu_item = self.menu_manager.search_item(item_name)
            if menu_item:
                description = menu_item.get('description', 'No description available')
                price = menu_item.get('price', 0.0)
                self.speak(f"{menu_item['name']}: {description}. It costs ${price:.2f}.")
            else:
                self.speak(f"Sorry, I don't have information about {item_name}.")
                
        return True
        
    def _handle_done_intent(self) -> bool:
        """Handle DONE intent."""
        order = self.order_manager.get_current_order()
        
        if not order or not order.items:
            self.speak("You haven't ordered anything yet.")
            return False
            
        # Provide order summary
        summary = f"Your order: "
        items_list = []
        for item in order.items:
            items_list.append(f"{item.quantity} {item.name}")
        summary += ", ".join(items_list)
        summary += f". Total: ${order.total_price():.2f}"
        
        self.speak(summary)
        self.speak("Shall I confirm your order?")
        
        return True
        
    def run(self) -> None:
        """Run the main robot loop with enhanced error handling."""
        logger.info("Starting Digital Waiter Robot...")
        
        # Initialize components
        if not self.initialize_components():
            logger.error("Failed to initialize. Exiting.")
            return
            
        try:
            # Start microphone stream
            logger.info("Starting microphone stream...")
            self.microphone.start_stream()
            self.running = True
            
            # Greet customer
            greeting = self.config.get('restaurant', {}).get(
                'greeting',
                "Welcome! Say 'Hey Jarvis' to start ordering."
            )
            self.speak(greeting)
            
            # Start new order
            self.order_manager.start_new_order()
            
            # Main loop with error recovery
            consecutive_errors = 0
            max_consecutive_errors = 5
            
            while self.running:
                try:
                    # Listen for wake word
                    if self.wake_word_detector:
                        logger.debug("Listening for wake word...")
                        if not self.listen_for_wake_word():
                            continue
                        logger.info("Wake word detected, proceeding to order listening")
                        self.speak("Yes, I'm listening!")
                    
                    # Listen for order
                    text = self.listen_for_order()
                    
                    if text:
                        # Process the order
                        logger.info(f"Processing order text: '{text}'")
                        success = self.process_order(text)
                        
                        if success:
                            # Ask if they want anything else
                            self.speak("Anything else?")
                            consecutive_errors = 0  # Reset error counter
                        else:
                            self.speak("I had trouble processing that order. Please try again.")
                    else:
                        self.speak("I didn't catch that. Please speak clearly and try again.")
                        
                except Exception as e:
                    consecutive_errors += 1
                    logger.error(f"Error in main loop (#{consecutive_errors}): {e}")
                    logger.debug("Main loop error details:", exc_info=True)
                    
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error(f"Too many consecutive errors ({consecutive_errors}). Stopping.")
                        self.speak("I'm experiencing technical difficulties. Please restart the system.")
                        break
                    
                    # Try to recover
                    self.speak("Sorry, I encountered an error. Let me try again.")
                    
                    # Wait a bit before retrying
                    import time
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error in robot main loop: {e}")
            logger.debug("Fatal error details:", exc_info=True)
        finally:
            logger.info("Shutting down robot...")
            self.stop()
            
    def stop(self) -> None:
        """Stop the robot and clean up resources."""
        logger.info("Stopping robot...")
        self.running = False
        
        # Save current order if exists
        if self.order_manager and self.order_manager.get_current_order():
            order = self.order_manager.get_current_order()
            if order.items:
                saved_path = self.order_manager.save_order()
                if saved_path:
                    logger.info(f"Final order saved to: {saved_path}")
                    self.speak("Thank you! Your order has been saved.")
        
        # Clean up components
        if self.microphone:
            self.microphone.close()
        if self.wake_word_detector:
            self.wake_word_detector.close()
        if self.speech_recognizer:
            self.speech_recognizer.close()
        if self.speech_synthesizer:
            self.speech_synthesizer.close()
            
        logger.info("Robot stopped")


def main():
    """Main entry point."""
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data/orders").mkdir(parents=True, exist_ok=True)
    Path("models").mkdir(exist_ok=True)
    
    # Create and run robot
    robot = DigitalWaiterRobot()
    robot.run()


if __name__ == "__main__":
    main()

