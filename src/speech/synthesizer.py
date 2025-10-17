"""
Text-to-speech synthesis using pyttsx3
Works offline with various TTS engines (eSpeak, etc.)
"""

import logging
from typing import Optional

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logging.warning("pyttsx3 not installed. Text-to-speech will not work.")

logger = logging.getLogger(__name__)


class SpeechSynthesizer:
    """
    Text-to-speech synthesizer using pyttsx3.
    
    pyttsx3 is an offline TTS library that works with various engines:
    - eSpeak (Linux) - GPL v3
    - SAPI5 (Windows)
    - NSSpeechSynthesizer (macOS)
    
    Features:
    - Offline operation
    - Cross-platform
    - Adjustable rate and volume
    - Multiple voices
    """
    
    def __init__(self, rate: int = 150, volume: float = 0.9, 
                 voice_id: Optional[str] = None):
        """
        Initialize the speech synthesizer.
        
        Args:
            rate: Speaking rate in words per minute (default: 150)
            volume: Volume level from 0.0 to 1.0 (default: 0.9)
            voice_id: Specific voice ID to use (None for default)
        """
        if not PYTTSX3_AVAILABLE:
            raise ImportError(
                "pyttsx3 is not installed. "
                "Install it with: pip install pyttsx3"
            )
            
        self.rate = rate
        self.volume = volume
        self.voice_id = voice_id
        self.engine: Optional[pyttsx3.Engine] = None
        
        self._initialize_engine()
        
    def _initialize_engine(self) -> None:
        """Initialize the TTS engine."""
        try:
            self.engine = pyttsx3.init()
            
            # Set properties
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            # Set voice if specified
            if self.voice_id:
                self.engine.setProperty('voice', self.voice_id)
            
            logger.info(f"Speech synthesizer initialized (rate: {self.rate}, "
                       f"volume: {self.volume})")
            
            # Log available voices
            voices = self.engine.getProperty('voices')
            logger.info(f"Available voices: {len(voices)}")
            for i, voice in enumerate(voices):
                logger.debug(f"  [{i}] {voice.name} ({voice.id})")
                
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            raise
            
    def speak(self, text: str, blocking: bool = True) -> bool:
        """
        Speak the given text.
        
        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete
            
        Returns:
            True if successful, False otherwise
        """
        if self.engine is None:
            logger.error("TTS engine not initialized")
            return False
            
        try:
            logger.info(f"Speaking: '{text}'")
            self.engine.say(text)
            
            if blocking:
                self.engine.runAndWait()
            else:
                # Start speaking in background
                self.engine.startLoop(False)
                self.engine.iterate()
                self.engine.endLoop()
                
            return True
            
        except Exception as e:
            logger.error(f"Error during speech synthesis: {e}")
            return False
            
    def save_to_file(self, text: str, filename: str) -> bool:
        """
        Save synthesized speech to an audio file.
        
        Args:
            text: Text to synthesize
            filename: Output filename (e.g., "output.wav")
            
        Returns:
            True if successful, False otherwise
        """
        if self.engine is None:
            logger.error("TTS engine not initialized")
            return False
            
        try:
            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()
            logger.info(f"Speech saved to: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving speech to file: {e}")
            return False
            
    def set_rate(self, rate: int) -> None:
        """Set speaking rate in words per minute."""
        if self.engine:
            self.rate = rate
            self.engine.setProperty('rate', rate)
            logger.debug(f"Speaking rate set to: {rate}")
            
    def set_volume(self, volume: float) -> None:
        """Set volume level (0.0 to 1.0)."""
        if self.engine:
            self.volume = max(0.0, min(1.0, volume))
            self.engine.setProperty('volume', self.volume)
            logger.debug(f"Volume set to: {self.volume}")
            
    def list_voices(self) -> None:
        """List all available voices."""
        if self.engine is None:
            logger.error("TTS engine not initialized")
            return
            
        voices = self.engine.getProperty('voices')
        logger.info(f"Available voices ({len(voices)}):")
        for i, voice in enumerate(voices):
            logger.info(f"  [{i}] {voice.name}")
            logger.info(f"      ID: {voice.id}")
            logger.info(f"      Languages: {voice.languages}")
            
    def stop(self) -> None:
        """Stop current speech."""
        if self.engine:
            self.engine.stop()
            logger.debug("Speech stopped")
            
    def close(self) -> None:
        """Clean up resources."""
        if self.engine:
            self.engine.stop()
            self.engine = None
        logger.info("Speech synthesizer closed")
        
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

