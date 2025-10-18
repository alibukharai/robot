#!/usr/bin/env python3
"""
Complete OpenWakeWord Fix
This script addresses all known issues with OpenWakeWord wake word detection
"""

import sys
import subprocess
import time
import numpy as np

def fix_numpy_compatibility():
    """Fix NumPy compatibility issues"""
    print("=== Fixing NumPy Compatibility ===")
    
    try:
        import numpy
        print(f"Current NumPy version: {numpy.__version__}")
        
        if numpy.__version__.startswith('2.'):
            print("❌ NumPy 2.x detected - this causes issues with OpenWakeWord")
            print("Downgrading to NumPy 1.x...")
            
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "numpy<2.0,>=1.21.0"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ NumPy downgraded successfully")
                return True
            else:
                print(f"❌ Failed to downgrade NumPy: {result.stderr}")
                return False
        else:
            print("✅ NumPy version is compatible")
            return True
            
    except Exception as e:
        print(f"❌ Error checking NumPy: {e}")
        return False

def reinstall_openwakeword():
    """Reinstall OpenWakeWord with proper dependencies"""
    print("\n=== Reinstalling OpenWakeWord ===")
    
    try:
        # Uninstall current version
        print("Uninstalling current OpenWakeWord...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "openwakeword"], 
                      capture_output=True)
        
        # Install specific working version
        print("Installing OpenWakeWord 0.5.1...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "openwakeword==0.5.1"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ OpenWakeWord reinstalled successfully")
            return True
        else:
            print(f"❌ Failed to reinstall: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error reinstalling OpenWakeWord: {e}")
        return False

def test_model_loading():
    """Test if models load correctly"""
    print("\n=== Testing Model Loading ===")
    
    try:
        from openwakeword.model import Model
        
        # Test basic model loading
        print("Loading OpenWakeWord models...")
        model = Model()
        
        available_models = list(model.models.keys())
        print(f"✅ Models loaded: {available_models}")
        
        # Test prediction with dummy data
        print("Testing prediction...")
        dummy_audio = np.zeros(1600, dtype=np.float32)
        predictions = model.predict(dummy_audio)
        
        print(f"✅ Prediction test successful")
        print(f"   Sample predictions: {dict(list(predictions.items())[:3])}")
        
        return True, available_models
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False, []

def test_audio_processing():
    """Test audio processing pipeline"""
    print("\n=== Testing Audio Processing ===")
    
    try:
        # Test audio conversion
        print("Testing audio format conversion...")
        
        # Create test audio data
        sample_rate = 16000
        duration = 0.1  # 100ms
        samples = int(sample_rate * duration)
        
        # Generate sine wave test signal
        frequency = 440  # A4 note
        t = np.linspace(0, duration, samples, False)
        audio_signal = np.sin(2 * np.pi * frequency * t)
        
        # Convert to int16 (microphone format)
        audio_int16 = (audio_signal * 32767).astype(np.int16)
        audio_bytes = audio_int16.tobytes()
        
        # Convert back to float32 (model format)
        audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
        audio_float = audio_data.astype(np.float32) / 32768.0
        
        print(f"✅ Audio conversion successful")
        print(f"   Input samples: {len(audio_int16)}")
        print(f"   Output samples: {len(audio_float)}")
        print(f"   Audio range: {audio_float.min():.3f} to {audio_float.max():.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Audio processing failed: {e}")
        return False

def test_wake_word_detection_raw():
    """Test wake word detection with raw audio processing"""
    print("\n=== Testing Raw Wake Word Detection ===")
    
    try:
        from openwakeword.model import Model
        import pyaudio
        
        # Initialize model
        model = Model()
        available_models = list(model.models.keys())
        print(f"Testing models: {available_models}")
        
        # Initialize audio
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        pa = pyaudio.PyAudio()
        
        # Find ReSpeaker device
        respeaker_index = None
        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            if 'respeaker' in info['name'].lower():
                respeaker_index = i
                print(f"✅ Found ReSpeaker: {info['name']}")
                break
        
        # Open audio stream
        stream = pa.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=respeaker_index,
            frames_per_buffer=CHUNK
        )
        
        print("🎤 Raw wake word test - say 'Alexa' or 'Weather'")
        print("   This bypasses our custom classes to test the core functionality")
        print("   Listening for 15 seconds...")
        
        start_time = time.time()
        max_scores = {model: 0.0 for model in available_models}
        detections = {model: 0 for model in available_models}
        
        try:
            while time.time() - start_time < 15:
                # Read audio
                data = stream.read(CHUNK, exception_on_overflow=False)
                
                # Convert to model format
                audio_data = np.frombuffer(data, dtype=np.int16)
                audio_float = audio_data.astype(np.float32) / 32768.0
                
                # Get predictions
                predictions = model.predict(audio_float)
                
                # Check each model
                for model_name, score in predictions.items():
                    if model_name in available_models:
                        max_scores[model_name] = max(max_scores[model_name], score)
                        
                        if score > 0.3:  # Detection threshold
                            detections[model_name] += 1
                            print(f"\n🎉 {model_name.upper()} detected! Score: {score:.3f}")
                
                # Show progress
                if int(time.time() - start_time) % 3 == 0:
                    best_score = max(max_scores.values())
                    print(f"\rBest score so far: {best_score:.3f}", end="", flush=True)
                
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\nStopped by user")
            
        stream.stop_stream()
        stream.close()
        pa.terminate()
        
        print(f"\n📊 Raw Detection Results:")
        working_models = []
        for model_name in available_models:
            detections_count = detections[model_name]
            max_score = max_scores[model_name]
            print(f"   {model_name}: {detections_count} detections, max score: {max_score:.3f}")
            
            if detections_count > 0:
                working_models.append(model_name)
        
        if working_models:
            print(f"✅ Working models found: {working_models}")
            return True, working_models
        else:
            print("❌ No models detected any wake words")
            return False, []
        
    except Exception as e:
        print(f"❌ Raw detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, []

def create_bypass_mode():
    """Create a bypass mode that skips wake word detection"""
    print("\n=== Creating Bypass Mode ===")
    
    try:
        # Create a simple bypass script
        bypass_script = '''#!/usr/bin/env python3
"""
Digital Waiter Robot - Bypass Mode
Runs without wake word detection for testing
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.audio.microphone import Microphone
from src.speech.recognizer import SpeechRecognizer
from src.speech.synthesizer import SpeechSynthesizer
from src.menu.manager import MenuManager
from src.intent.processor import IntentProcessor
from src.order.manager import OrderManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run robot without wake word detection"""
    print("🤖 Digital Waiter Robot - Bypass Mode")
    print("   Wake word detection is disabled")
    print("   Press ENTER to start listening for orders")
    print("   Press Ctrl+C to exit")
    
    try:
        # Initialize components (skip wake word detector)
        mic = Microphone(sample_rate=16000, channels=1, chunk_size=1024)
        recognizer = SpeechRecognizer(model_path="models/vosk-model-small-en-us-0.15")
        synthesizer = SpeechSynthesizer(rate=150, volume=0.9)
        menu_manager = MenuManager(menu_file="config/menu.yaml")
        intent_processor = IntentProcessor()
        order_manager = OrderManager(save_directory="data/orders")
        
        print("✅ All components initialized (except wake word)")
        
        mic.start_stream()
        synthesizer.speak("Welcome! I'm your digital waiter. Press ENTER when you want to order.")
        
        while True:
            input("\\nPress ENTER to start listening for your order...")
            
            print("🎤 Listening for your order... (speak now)")
            synthesizer.speak("I'm listening. What would you like to order?")
            
            # Record audio until silence
            audio_data = mic.record_until_silence(
                silence_threshold=500,
                silence_duration=1.5,
                max_duration=10
            )
            
            if audio_data:
                # Recognize speech
                text = recognizer.recognize(audio_data)
                if text:
                    print(f"You said: {text}")
                    synthesizer.speak(f"I heard: {text}")
                    
                    # Process order (simplified)
                    menu_items = [item['name'] for item in menu_manager.get_all_items()]
                    result = intent_processor.process(text, menu_items)
                    
                    print(f"Intent: {result['intent']}")
                    print(f"Entities: {result['entities']}")
                    
                    synthesizer.speak("Thank you for your order!")
                else:
                    print("No speech recognized")
                    synthesizer.speak("I didn't catch that. Please try again.")
            else:
                print("No audio recorded")
                synthesizer.speak("I didn't hear anything. Please try again.")
    
    except KeyboardInterrupt:
        print("\\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'mic' in locals():
            mic.close()

if __name__ == "__main__":
    main()
'''
        
        with open('robot_bypass.py', 'w') as f:
            f.write(bypass_script)
        
        import os
        os.chmod('robot_bypass.py', 0o755)
        
        print("✅ Bypass mode created: robot_bypass.py")
        print("   Run with: python3 robot_bypass.py")
        return True
        
    except Exception as e:
        print(f"❌ Error creating bypass mode: {e}")
        return False

def main():
    """Main fix function"""
    print("🔧 Complete OpenWakeWord Fix Tool")
    print("=" * 50)
    
    success_count = 0
    total_steps = 5
    
    # Step 1: Fix NumPy compatibility
    if fix_numpy_compatibility():
        success_count += 1
    
    # Step 2: Reinstall OpenWakeWord
    if reinstall_openwakeword():
        success_count += 1
    
    # Step 3: Test model loading
    models_work, available_models = test_model_loading()
    if models_work:
        success_count += 1
    
    # Step 4: Test audio processing
    if test_audio_processing():
        success_count += 1
    
    # Step 5: Test raw wake word detection
    if models_work:
        detection_works, working_models = test_wake_word_detection_raw()
        if detection_works:
            success_count += 1
            
            # Update config with working model
            if working_models:
                best_model = working_models[0]
                print(f"\\n🔧 Updating config to use: {best_model}")
                
                try:
                    with open('config/settings.yaml', 'r') as f:
                        config = f.read()
                    
                    import re
                    config = re.sub(r'model: "[^"]*"', f'model: "{best_model}"', config)
                    config = re.sub(r'threshold: [0-9.]+', 'threshold: 0.2', config)
                    
                    with open('config/settings.yaml', 'w') as f:
                        f.write(config)
                        
                    print(f"✅ Config updated to use {best_model} with threshold 0.2")
                    
                except Exception as e:
                    print(f"❌ Error updating config: {e}")
    
    # Create bypass mode regardless
    if create_bypass_mode():
        print("\\n✅ Bypass mode available as fallback")
    
    print(f"\\n" + "=" * 50)
    print(f"🎯 Fix Results: {success_count}/{total_steps} steps successful")
    
    if success_count >= 4:
        print("✅ OpenWakeWord should now work!")
        print("   Run: python3 src/main.py")
    elif success_count >= 2:
        print("⚠️  Partial success - try the bypass mode:")
        print("   Run: python3 robot_bypass.py")
    else:
        print("❌ Major issues detected. Try:")
        print("   1. Fresh virtual environment")
        print("   2. Different OpenWakeWord version")
        print("   3. Use bypass mode: python3 robot_bypass.py")

if __name__ == "__main__":
    main()