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
            # Initialize the model (loads all available models by default)
            logger.info("Loading OpenWakeWord models...")
            self.model = Model()
            
            available_models = list(self.model.models.keys())
            logger.info(f"Available wake word models: {available_models}")
            
            # Verify the requested model is available
            if self.model_name and self.model_name not in self.model.models:
                logger.warning(f"Requested model '{self.model_name}' not found.")
                
                # Try common model name variations
                model_variations = [
                    self.model_name,
                    self.model_name.lower(),
                    self.model_name.replace('_', ' '),
                    self.model_name.replace(' ', '_'),
                ]
                
                found_model = None
                for variation in model_variations:
                    for available_model in available_models:
                        if variation.lower() in available_model.lower():
                            found_model = available_model
                            break
                    if found_model:
                        break
                
                if found_model:
                    self.model_name = found_model
                    logger.info(f"Using similar model: {self.model_name}")
                elif available_models:
                    # Use the first available model as fallback
                    self.model_name = available_models[0]
                    logger.info(f"Using fallback model: {self.model_name}")
                else:
                    raise RuntimeError("No wake word models available")
            
            logger.info(f"Wake word detector initialized with model: {self.model_name}")
            logger.info(f"Detection threshold: {self.threshold}")
            
        except Exception as e:
            logger.error(f"Failed to initialize wake word model: {e}")
            logger.error("Try installing models with: pip install --upgrade openwakeword")
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
            
        if not audio_chunk or len(audio_chunk) == 0:
            logger.debug("Empty audio chunk provided")
            return False
            
        try:
            # Convert bytes to numpy array (int16)
            audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
            
            # Check if we have enough data
            if len(audio_data) == 0:
                logger.debug("No audio data after conversion")
                return False
            
            # OpenWakeWord expects float32 normalized to [-1, 1]
            audio_float = audio_data.astype(np.float32) / 32768.0
            
            # Ensure we have the right shape
            if audio_float.ndim != 1:
                logger.error(f"Expected 1D audio, got shape: {audio_float.shape}")
                return False
            
            # Get predictions from model
            predictions = self.model.predict(audio_float)
            
            if not predictions:
                logger.debug("No predictions returned from model")
                return False
            
            # Check predictions
            max_score = 0.0
            best_model = None
            
            # If we have a specific model name, prioritize it
            if self.model_name and self.model_name in predictions:
                score = predictions[self.model_name]
                if score >= self.threshold:
                    logger.info(f"Wake word detected: {self.model_name} (score: {score:.3f})")
                    return True
                max_score = max(max_score, score)
                best_model = self.model_name
            else:
                # Check all available models
                for model_name, score in predictions.items():
                    if score > max_score:
                        max_score = score
                        best_model = model_name
                    
                    if score >= self.threshold:
                        logger.info(f"Wake word detected: {model_name} (score: {score:.3f})")
                        return True
            
            # Log the best score for debugging
            if max_score > 0.1:  # Only log if there's some detection
                logger.debug(f"Best detection: {best_model} (score: {max_score:.3f}, threshold: {self.threshold})")
                    
            return False
            
        except ValueError as e:
            logger.error(f"Audio data conversion error: {e}")
            logger.debug(f"Audio chunk length: {len(audio_chunk)} bytes")
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

