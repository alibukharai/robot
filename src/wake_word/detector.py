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
            logger.info("Initializing OpenWakeWord model...")
            
            # Try different initialization methods for compatibility
            try:
                # Method 1: Default initialization (recommended)
                self.model = Model()
                logger.info("✓ Model initialized using default method")
            except Exception as e1:
                logger.warning(f"Default initialization failed: {e1}")
                try:
                    # Method 2: Specify inference framework explicitly
                    self.model = Model(inference_framework='onnx')
                    logger.info("✓ Model initialized using ONNX framework")
                except Exception as e2:
                    logger.warning(f"ONNX initialization failed: {e2}")
                    # Method 3: Try TensorFlow Lite if available
                    try:
                        self.model = Model(inference_framework='tflite')
                        logger.info("✓ Model initialized using TensorFlow Lite framework")
                    except Exception as e3:
                        logger.error(f"All initialization methods failed:")
                        logger.error(f"  Default: {e1}")
                        logger.error(f"  ONNX: {e2}")
                        logger.error(f"  TFLite: {e3}")
                        raise e1  # Raise the original error
                
            logger.info(f"Wake word detector initialized with target model: {self.model_name}")
            logger.info(f"Available models: {list(self.model.models.keys())}")
            
            # Verify the requested model is available
            if self.model_name and self.model_name not in self.model.models:
                available_models = list(self.model.models.keys())
                logger.warning(f"Model '{self.model_name}' not found. Available models: {available_models}")
                # Use the first available model as fallback
                if available_models:
                    old_model = self.model_name
                    self.model_name = available_models[0]
                    logger.info(f"Using fallback model: {self.model_name} (requested: {old_model})")
                else:
                    raise RuntimeError("No wake word models are available")
            
            logger.info(f"✓ Wake word detector ready with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize wake word model: {e}")
            logger.error("Troubleshooting tips:")
            logger.error("1. Ensure OpenWakeWord is properly installed: pip install openwakeword")
            logger.error("2. Check internet connection (models may need to be downloaded)")
            logger.error("3. Try running: python -c 'from openwakeword.model import Model; Model()'")
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
            
            # Check if the specific model detected the wake word above threshold
            # If model_name is specified, only check that model, otherwise check all
            models_to_check = [self.model_name] if self.model_name in predictions else predictions.keys()
            
            for model_name in models_to_check:
                if model_name in predictions:
                    score = predictions[model_name]
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

