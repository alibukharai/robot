"""
Offline speech recognition using Vosk
Apache 2.0 licensed, suitable for commercial use
"""

import json
import logging
from typing import Optional
import wave
import tempfile
import os

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logging.warning("Vosk not installed. Speech recognition will not work.")

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    """
    Offline speech recognizer using Vosk.
    
    Vosk is an open-source speech recognition toolkit (Apache 2.0 license)
    that runs entirely offline. It supports multiple languages and works
    well on low-resource devices like Raspberry Pi.
    
    Features:
    - Offline operation
    - Multiple language support
    - Low resource usage
    - Apache 2.0 license (commercial-use friendly)
    """
    
    def __init__(self, model_path: str, sample_rate: int = 16000):
        """
        Initialize the speech recognizer.
        
        Args:
            model_path: Path to Vosk model directory
            sample_rate: Audio sample rate in Hz
        """
        if not VOSK_AVAILABLE:
            raise ImportError(
                "Vosk is not installed. "
                "Install it with: pip install vosk"
            )
            
        self.model_path = model_path
        self.sample_rate = sample_rate
        self.model: Optional[Model] = None
        self.recognizer: Optional[KaldiRecognizer] = None
        
        self._initialize_model()
        
    def _initialize_model(self) -> None:
        """Initialize the Vosk model."""
        try:
            if not os.path.exists(self.model_path):
                logger.error(f"Model path does not exist: {self.model_path}")
                logger.info("Please download a Vosk model from: "
                          "https://alphacephei.com/vosk/models")
                raise FileNotFoundError(f"Model not found: {self.model_path}")
                
            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            
            # Enable alternatives and confidence scores
            self.recognizer.SetWords(True)
            
            logger.info(f"Speech recognizer initialized with model: {self.model_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize speech recognizer: {e}")
            raise
            
    def recognize(self, audio_data: bytes) -> Optional[str]:
        """
        Recognize speech from audio data.
        
        Args:
            audio_data: Raw audio bytes (int16, mono, 16kHz)
            
        Returns:
            Recognized text, or None if recognition failed
        """
        if self.recognizer is None:
            logger.error("Recognizer not initialized")
            return None
            
        try:
            # Process audio data
            if self.recognizer.AcceptWaveform(audio_data):
                # Complete recognition result
                result = json.loads(self.recognizer.Result())
                text = result.get('text', '').strip()
            else:
                # Partial recognition result
                result = json.loads(self.recognizer.PartialResult())
                text = result.get('partial', '').strip()
                
                # If no partial text, try to get final result
                if not text:
                    final_result = json.loads(self.recognizer.FinalResult())
                    text = final_result.get('text', '').strip()
            
            if text:
                logger.info(f"Recognized: '{text}'")
                return text
            else:
                logger.debug("No speech recognized")
                return None
                
        except Exception as e:
            logger.error(f"Error during speech recognition: {e}")
            return None
            
    def recognize_from_file(self, wav_file: str) -> Optional[str]:
        """
        Recognize speech from a WAV file.
        
        Args:
            wav_file: Path to WAV file
            
        Returns:
            Recognized text, or None if recognition failed
        """
        if self.model is None:
            logger.error("Model not initialized")
            return None
            
        try:
            with wave.open(wav_file, "rb") as wf:
                # Verify file format
                if wf.getnchannels() != 1:
                    logger.error("Audio file must be mono")
                    return None
                if wf.getsampwidth() != 2:
                    logger.error("Audio file must be 16-bit")
                    return None
                if wf.getframerate() != self.sample_rate:
                    logger.warning(f"Audio sample rate {wf.getframerate()} "
                                 f"doesn't match expected {self.sample_rate}")
                    
                # Create new recognizer for this file
                rec = KaldiRecognizer(self.model, wf.getframerate())
                rec.SetWords(True)
                
                # Process audio in chunks
                results = []
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        if result.get('text'):
                            results.append(result['text'])
                            
                # Get final result
                final_result = json.loads(rec.FinalResult())
                if final_result.get('text'):
                    results.append(final_result['text'])
                    
                # Combine all results
                text = ' '.join(results).strip()
                
                if text:
                    logger.info(f"Recognized from file: '{text}'")
                    return text
                else:
                    logger.debug("No speech recognized from file")
                    return None
                    
        except FileNotFoundError:
            logger.error(f"WAV file not found: {wav_file}")
            return None
        except Exception as e:
            logger.error(f"Error recognizing from file: {e}")
            return None
            
    def reset(self) -> None:
        """Reset the recognizer state."""
        if self.model is not None:
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            self.recognizer.SetWords(True)
            logger.debug("Speech recognizer reset")
            
    def close(self) -> None:
        """Clean up resources."""
        self.recognizer = None
        self.model = None
        logger.info("Speech recognizer closed")
        
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

