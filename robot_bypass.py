#!/usr/bin/env python3
"""
Digital Waiter Robot - Bypass Mode
Runs without wake word detection for testing
"""

import sys
import signal
import logging
import yaml
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.audio.microphone import Microphone
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
        logging.FileHandler('logs/robot_bypass.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DigitalWaiterRobotBypass:
    """
    Digital Waiter Robot - Bypass Mode
    
    All functionality except wake word detection.
    Perfect for testing when wake word detection isn't working.
    """
    
    def __init__(self, config_file: str = "config/settings.yaml"):
        """Initialize the robot in bypass mode."""
        self.config_file = config_file
        self.config = self._load_config()
        self.running = False
        
        # Initialize components (skip wake word detector)
        self.microphone = None
        self.speech_recognizer = None
        self.speech_synthesizer = None
        self.menu_manager = None
        self.intent_processor = None
        self.order_manager = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Digital Waiter Robot (Bypass Mode) initialized")
        
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
        """Initialize all robot components except wake word detector."""
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
            
            logger.info("All components initialized successfully (bypass mode)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            return False
            
    def speak(self, text: str) -> None:
        """Speak text through TTS."""
        if self.speech_synthesizer:
            logger.info(f"Robot: {text}")
            self.speech_synthesizer.speak(text)
        else:
            logger.warning("TTS not initialized")
            print(f"Robot: {text}")
            
    def listen_for_order(self) -> str:
        """Listen for customer order speech."""
        if not self.microphone or not self.speech_recognizer:
            logger.error("Microphone or ASR not initialized")
            return None
            
        logger.info("Listening for order...")
        print("🎤 Listening... Speak your order now!")
        
        try:
            # Record audio until silence
            audio_config = self.config.get('audio', {})
            audio_data = self.microphone.record_until_silence(
                silence_threshold=audio_config.get('silence_threshold', 500),
                silence_duration=audio_config.get('silence_duration', 1.5),
                max_duration=audio_config.get('max_recording_duration', 10)
            )
            
            if audio_data is None:
                logger.warning("No audio recorded")
                return None
                
            # Recognize speech
            text = self.speech_recognizer.recognize(audio_data)
            if text:
                logger.info(f"Recognized: {text}")
                print(f"You said: '{text}'")
            return text
            
        except Exception as e:
            logger.error(f"Error during speech recognition: {e}")
            return None
            
    def process_order(self, text: str) -> bool:
        """Process customer order text."""
        if not text:
            return False
            
        # Get all menu item names for matching
        menu_items = [item['name'] for item in self.menu_manager.get_all_items()]
        
        # Process intent
        result = self.intent_processor.process(text, menu_items)
        intent = result['intent']
        entities = result['entities']
        
        logger.info(f"Intent: {intent.value}, Entities: {entities}")
        print(f"🧠 Intent: {intent.value}")
        print(f"📝 Entities: {entities}")
        
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
                response = f"Added {quantity} {menu_item['name']} to your order. That's ${price_total:.2f}."
                self.speak(response)
                print(f"✅ {response}")
            else:
                response = f"Sorry, I couldn't find {item_name} on our menu. Would you like to hear our suggestions?"
                self.speak(response)
                print(f"❌ {response}")
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
        print(f"💡 {suggestion_text}")
        return True
        
    def _handle_confirm_intent(self) -> bool:
        """Handle CONFIRM intent."""
        response = "Great! Your order is confirmed."
        self.speak(response)
        print(f"✅ {response}")
        return True
        
    def _handle_cancel_intent(self) -> bool:
        """Handle CANCEL intent."""
        response = "No problem. What would you like instead?"
        self.speak(response)
        print(f"🔄 {response}")
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
                response = f"{menu_item['name']}: {description}. It costs ${price:.2f}."
                self.speak(response)
                print(f"ℹ️  {response}")
            else:
                response = f"Sorry, I don't have information about {item_name}."
                self.speak(response)
                print(f"❓ {response}")
                
        return True
        
    def _handle_done_intent(self) -> bool:
        """Handle DONE intent."""
        order = self.order_manager.get_current_order()
        
        if not order or not order.items:
            response = "You haven't ordered anything yet."
            self.speak(response)
            print(f"📋 {response}")
            return False
            
        # Provide order summary
        summary = f"Your order: "
        items_list = []
        for item in order.items:
            items_list.append(f"{item.quantity} {item.name}")
        summary += ", ".join(items_list)
        summary += f". Total: ${order.total_price():.2f}"
        
        self.speak(summary)
        print(f"📋 {summary}")
        self.speak("Shall I confirm your order?")
        
        return True
        
    def run_interactive(self):
        """Run the robot in interactive mode."""
        print("🤖 Digital Waiter Robot - Bypass Mode")
        print("=" * 50)
        print("Wake word detection is disabled.")
        print("Press ENTER when you want to place an order.")
        print("Type 'quit' or press Ctrl+C to exit.")
        print("=" * 50)
        
        # Initialize components
        if not self.initialize_components():
            logger.error("Failed to initialize. Exiting.")
            return
            
        # Start microphone stream
        self.microphone.start_stream()
        self.running = True
        
        # Greet customer
        greeting = self.config.get('restaurant', {}).get(
            'greeting',
            "Welcome to Robot Cafe! I'm your digital waiter."
        )
        self.speak(greeting)
        
        # Start new order
        self.order_manager.start_new_order()
        
        try:
            while self.running:
                # Wait for user input
                user_input = input("\n👋 Press ENTER to start ordering (or 'quit' to exit): ").strip().lower()
                
                if user_input in ['quit', 'exit', 'q']:
                    break
                
                # Listen for order
                self.speak("I'm listening. What would you like to order?")
                text = self.listen_for_order()
                
                if text:
                    # Process the order
                    success = self.process_order(text)
                    
                    if success:
                        self.speak("Anything else?")
                    else:
                        self.speak("Let me know if you'd like to try again.")
                else:
                    self.speak("I didn't catch that. Please try again.")
                    
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
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
        if self.speech_recognizer:
            self.speech_recognizer.close()
        if self.speech_synthesizer:
            self.speech_synthesizer.close()
            
        logger.info("Robot stopped")

def main():
    """Main entry point for bypass mode."""
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data/orders").mkdir(parents=True, exist_ok=True)
    Path("models").mkdir(exist_ok=True)
    
    # Create and run robot
    robot = DigitalWaiterRobotBypass()
    robot.run_interactive()

if __name__ == "__main__":
    main()