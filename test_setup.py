#!/usr/bin/env python3
"""
Test script to verify Digital Waiter Robot setup
Run this after setup.sh to check that all components are working
"""

import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test results
results = {
    'passed': [],
    'failed': [],
    'warnings': []
}


def test_imports():
    """Test that all required packages can be imported."""
    logger.info("Testing Python package imports...")
    
    packages = [
        ('pyaudio', 'PyAudio'),
        ('openwakeword', 'OpenWakeWord'),
        ('vosk', 'Vosk'),
        ('pyttsx3', 'pyttsx3'),
        ('yaml', 'PyYAML'),
        ('numpy', 'NumPy')
    ]
    
    for module, name in packages:
        try:
            __import__(module)
            logger.info(f"  ✓ {name}")
            results['passed'].append(f"Import {name}")
        except ImportError as e:
            logger.error(f"  ✗ {name}: {e}")
            results['failed'].append(f"Import {name}")


def test_audio_devices():
    """Test audio device detection."""
    logger.info("Testing audio devices...")
    
    try:
        import pyaudio
        audio = pyaudio.PyAudio()
        
        # Check for input devices
        input_devices = []
        output_devices = []
        
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info.get('maxInputChannels', 0) > 0:
                input_devices.append(info.get('name'))
            if info.get('maxOutputChannels', 0) > 0:
                output_devices.append(info.get('name'))
        
        logger.info(f"  Found {len(input_devices)} input device(s)")
        logger.info(f"  Found {len(output_devices)} output device(s)")
        
        # Check for ReSpeaker
        respeaker_found = any('seeed' in name.lower() for name in input_devices)
        
        if respeaker_found:
            logger.info("  ✓ ReSpeaker device detected")
            results['passed'].append("ReSpeaker detection")
        else:
            logger.warning("  ⚠ ReSpeaker device not found")
            results['warnings'].append("ReSpeaker not detected (may need reboot)")
        
        if input_devices and output_devices:
            results['passed'].append("Audio devices available")
        else:
            results['failed'].append("No audio devices found")
        
        audio.terminate()
        
    except Exception as e:
        logger.error(f"  ✗ Audio device test failed: {e}")
        results['failed'].append("Audio device test")


def test_models():
    """Test that required models are present."""
    logger.info("Testing AI models...")
    
    # Check Vosk model
    vosk_model = Path("models/vosk-model-small-en-us-0.15")
    if vosk_model.exists() and vosk_model.is_dir():
        logger.info("  ✓ Vosk model found")
        results['passed'].append("Vosk model")
    else:
        logger.error("  ✗ Vosk model not found")
        results['failed'].append("Vosk model missing")
    
    # OpenWakeWord models (downloaded on first use)
    logger.info("  ℹ OpenWakeWord models will be downloaded on first use")
    results['passed'].append("OpenWakeWord ready")


def test_config_files():
    """Test that configuration files exist."""
    logger.info("Testing configuration files...")
    
    configs = [
        'config/settings.yaml',
        'config/menu.yaml'
    ]
    
    for config_file in configs:
        path = Path(config_file)
        if path.exists():
            logger.info(f"  ✓ {config_file}")
            results['passed'].append(f"Config: {config_file}")
        else:
            logger.error(f"  ✗ {config_file} not found")
            results['failed'].append(f"Config: {config_file}")


def test_directories():
    """Test that required directories exist."""
    logger.info("Testing directory structure...")
    
    dirs = [
        'logs',
        'data/orders',
        'models',
        'src'
    ]
    
    for directory in dirs:
        path = Path(directory)
        if path.exists() and path.is_dir():
            logger.info(f"  ✓ {directory}/")
            results['passed'].append(f"Directory: {directory}")
        else:
            logger.error(f"  ✗ {directory}/ not found")
            results['failed'].append(f"Directory: {directory}")


def test_tts():
    """Test text-to-speech."""
    logger.info("Testing text-to-speech...")
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        # Get available voices
        voices = engine.getProperty('voices')
        logger.info(f"  Found {len(voices)} TTS voice(s)")
        
        # Try to speak (non-blocking)
        logger.info("  Testing TTS (you should hear 'Test successful')...")
        engine.say("Test successful")
        engine.runAndWait()
        
        logger.info("  ✓ TTS working")
        results['passed'].append("Text-to-speech")
        
    except Exception as e:
        logger.error(f"  ✗ TTS test failed: {e}")
        results['failed'].append("Text-to-speech")


def test_microphone():
    """Test microphone recording."""
    logger.info("Testing microphone...")
    
    try:
        from src.audio.microphone import Microphone
        
        # Try to create microphone instance
        mic = Microphone(device_name="seeed-2mic-voicecard")
        logger.info(f"  Microphone initialized")
        
        # Try to start stream
        mic.start_stream()
        logger.info("  Audio stream started")
        
        # Read a few chunks
        for _ in range(5):
            chunk = mic.read_chunk()
            if chunk is None:
                raise Exception("Failed to read audio chunk")
        
        mic.stop_stream()
        mic.close()
        
        logger.info("  ✓ Microphone working")
        results['passed'].append("Microphone recording")
        
    except Exception as e:
        logger.error(f"  ✗ Microphone test failed: {e}")
        results['failed'].append("Microphone recording")


def print_summary():
    """Print test summary."""
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    print(f"\n✓ Passed: {len(results['passed'])}")
    for item in results['passed']:
        print(f"  • {item}")
    
    if results['warnings']:
        print(f"\n⚠ Warnings: {len(results['warnings'])}")
        for item in results['warnings']:
            print(f"  • {item}")
    
    if results['failed']:
        print(f"\n✗ Failed: {len(results['failed'])}")
        for item in results['failed']:
            print(f"  • {item}")
    
    print("\n" + "=" * 50)
    
    if results['failed']:
        print("\n❌ Some tests failed. Please check the setup.")
        print("Run setup.sh again or see README.md for troubleshooting.")
        return 1
    elif results['warnings']:
        print("\n⚠️  Setup complete with warnings.")
        print("The robot should work, but check warnings above.")
        return 0
    else:
        print("\n✅ All tests passed! Robot is ready to use.")
        print("\nTo start the robot:")
        print("  python3 src/main.py")
        return 0


def main():
    """Run all tests."""
    print("=" * 50)
    print("Digital Waiter Robot - Setup Test")
    print("=" * 50)
    print()
    
    # Run tests
    test_imports()
    print()
    
    test_config_files()
    print()
    
    test_directories()
    print()
    
    test_models()
    print()
    
    test_audio_devices()
    print()
    
    test_tts()
    print()
    
    test_microphone()
    print()
    
    # Print summary
    exit_code = print_summary()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

