#!/usr/bin/env python3
"""
Test script for wake word detection functionality
This helps diagnose issues with OpenWakeWord installation
"""

import sys
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test all required imports"""
    print("=== Testing Imports ===")
    
    tests = [
        ('numpy', 'NumPy'),
        ('openwakeword', 'OpenWakeWord'),
        ('pyaudio', 'PyAudio'),
        ('yaml', 'PyYAML'),
    ]
    
    for module, name in tests:
        try:
            __import__(module)
            print(f"✓ {name} imported successfully")
        except ImportError as e:
            print(f"✗ {name} import failed: {e}")
            return False
    
    return True

def test_openwakeword():
    """Test OpenWakeWord functionality"""
    print("\n=== Testing OpenWakeWord ===")
    
    try:
        from openwakeword.model import Model
        print("✓ OpenWakeWord Model class imported")
        
        # Initialize model
        print("Initializing OpenWakeWord model...")
        model = Model()
        print(f"✓ Model initialized successfully")
        print(f"Available models: {list(model.models.keys())}")
        
        # Test prediction with dummy data
        import numpy as np
        dummy_audio = np.zeros(1600, dtype=np.float32)  # 0.1 seconds at 16kHz
        predictions = model.predict(dummy_audio)
        print(f"✓ Prediction test successful: {predictions}")
        
        return True
        
    except Exception as e:
        print(f"✗ OpenWakeWord test failed: {e}")
        traceback.print_exc()
        return False

def test_wake_word_detector():
    """Test our custom WakeWordDetector class"""
    print("\n=== Testing WakeWordDetector ===")
    
    try:
        # Add current directory to path
        sys.path.insert(0, '.')
        
        from src.wake_word.detector import WakeWordDetector
        print("✓ WakeWordDetector class imported")
        
        # Initialize detector
        detector = WakeWordDetector(model_name='hey_jarvis', threshold=0.5)
        print("✓ WakeWordDetector initialized successfully")
        
        # Test detection with dummy audio
        import numpy as np
        dummy_audio = np.zeros(1600, dtype=np.int16)  # 0.1 seconds at 16kHz
        result = detector.detect(dummy_audio.tobytes())
        print(f"✓ Detection test completed. Result: {result}")
        
        detector.close()
        print("✓ WakeWordDetector closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ WakeWordDetector test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Digital Waiter Robot - Wake Word Test")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print()
    
    # Run tests
    success = True
    success &= test_imports()
    success &= test_openwakeword()
    success &= test_wake_word_detector()
    
    print("\n=== Test Results ===")
    if success:
        print("✓ All tests passed! Wake word detection should work.")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the correct virtual environment")
        print("2. Run the installation script: ./install_dependencies.sh")
        print("3. Check that all dependencies are installed: pip list")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())