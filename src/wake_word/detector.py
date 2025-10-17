"""
Wake word detector using OpenWakeWord
Offline, open-source (Apache 2.0), and optimized for Raspberry Pi
"""

import logging
import numpy as np
from typing import Optional
try:
    from openwakeword.model import Model
    OPENWAKEWORD_AVAILABLE = True
except ImportError:
    OPENWAKEWORD_AVAILABLE = False
    logging.warning("OpenWakeWord not installed. Wake word detection will not work.")

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """
    Wake word detector using OpenWakeWord.
    
    OpenWakeWord is an open-source wake word detection library (Apache 2.0 license)
    that runs entirely offline. It includes pre-trained models for common wake words.
    
    Features:
    - Offline operation
    - Pre-trained models (alexa, hey_jarvis, hey_mycroft, etc.)
    - Low resource usage (suitable for Raspberry Pi)
    - Apache 2.0 license (commercial-use friendly)
    """
    
    def __init__(self, model_name: str = "hey_jarvis", threshold: float = 0.5):
        """
        Initialize the wake word detector.
        
        Args:
            model_name: Wake word model to use (e.g., "hey_jarvis", "alexa", "hey_mycroft")
            threshold: Detection threshold (0.0-1.0, higher = more strict)
        """
        if not OPENWAKEWORD_AVAILABLE:
            raise ImportError(
                "OpenWakeWord is not installed. "
                "Install it with: pip install openwakeword"
            )
            
        self.model_name = model_name
        self.threshold = threshold
        self.model: Optional[Model] = None
        
        self._initialize_model()
        
    def _initialize_model(self) -> None:
        """Initialize the OpenWakeWord model."""
        try:
            # Initialize with specific model or all models
            if self.model_name:
                # OpenWakeWord will download the model if not present
                self.model = Model(
                    wakeword_models=[self.model_name],
                    inference_framework="onnx"  # Use ONNX for better Pi performance
                )
            else:
                # Load all available models
                self.model = Model(inference_framework="onnx")
                
            logger.info(f"Wake word detector initialized with model: {self.model_name}")
            logger.info(f"Available models: {list(self.model.models.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to initialize wake word model: {e}")
            raise
            
    def detect(self, audio_chunk: bytes) -> bool:
        """
        Detect wake word in audio chunk.
        
        Args:
            audio_chunk: Raw audio bytes (int16, mono, 16kHz)
            
        Returns:
            True if wake word detected, False otherwise
        """
        if self.model is None:
            logger.error("Model not initialized")
            return False
            
        try:
            # Convert bytes to numpy array (int16)
            audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
            
            # OpenWakeWord expects float32 normalized to [-1, 1]
            audio_float = audio_data.astype(np.float32) / 32768.0
            
            # Get predictions from model
            predictions = self.model.predict(audio_float)
            
            # Check if any model detected the wake word above threshold
            for model_name, score in predictions.items():
                if score >= self.threshold:
                    logger.info(f"Wake word detected: {model_name} (score: {score:.3f})")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error during wake word detection: {e}")
            return False
            
    def reset(self) -> None:
        """Reset the model state."""
        if self.model is not None:
            self.model.reset()
            logger.debug("Wake word detector reset")
            
    def close(self) -> None:
        """Clean up resources."""
        self.model = None
        logger.info("Wake word detector closed")
        
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

