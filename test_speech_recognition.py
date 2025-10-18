#!/usr/bin/env python3
"""
Speech Recognition Diagnostic Tool
Tests if Vosk speech recognition is working properly
"""

import sys
import os
import time
import json
import numpy as np
from pathlib import Path

# Add current directory to path
sys.path.insert(0, '.')

def check_vosk_model():
    """Check if Vosk model exists and is valid"""
    print("=== Checking Vosk Model ===")
    
    model_path = "models/vosk-model-small-en-us-0.15"
    model_dir = Path(model_path)
    
    print(f"Looking for model at: {model_dir.absolute()}")
    
    if not model_dir.exists():
        print("❌ Vosk model directory not found!")
        print("   The speech recognition model is missing.")
        print("   Download it with:")
        print("   wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
        print("   unzip vosk-model-small-en-us-0.15.zip -d models/")
        return False
    
    # Check required files
    required_files = [
        "am/final.mdl",
        "graph/HCLr.fst", 
        "graph/Gr.fst",
        "ivector/final.ie"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = model_dir / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Model files missing: {missing_files}")
        print("   The model appears to be corrupted or incomplete.")
        return False
    
    print("✅ Vosk model files found and appear complete")
    return True

def test_vosk_import():
    """Test if Vosk can be imported and initialized"""
    print("\n=== Testing Vosk Import ===")
    
    try:
        import vosk
        print(f"✅ Vosk imported successfully")
        print(f"   Vosk version: {vosk.__version__ if hasattr(vosk, '__version__') else 'Unknown'}")
        
        # Test model loading
        model_path = "models/vosk-model-small-en-us-0.15"
        if not Path(model_path).exists():
            print("❌ Cannot test model loading - model directory missing")
            return False
        
        print("Testing model loading...")
        model = vosk.Model(model_path)
        print("✅ Vosk model loaded successfully")
        
        # Test recognizer creation
        rec = vosk.KaldiRecognizer(model, 16000)
        print("✅ Vosk recognizer created successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import Vosk: {e}")
        print("   Install with: pip install vosk")
        return False
    except Exception as e:
        print(f"❌ Error testing Vosk: {e}")
        return False

def test_speech_recognizer():
    """Test our custom SpeechRecognizer class"""
    print("\n=== Testing SpeechRecognizer Class ===")
    
    try:
        from src.speech.recognizer import SpeechRecognizer
        
        print("Creating SpeechRecognizer...")
        recognizer = SpeechRecognizer(
            model_path="models/vosk-model-small-en-us-0.15",
            sample_rate=16000
        )
        print("✅ SpeechRecognizer created successfully")
        
        # Test with dummy audio (silence)
        print("Testing with silent audio...")
        silent_audio = np.zeros(16000, dtype=np.int16)  # 1 second of silence
        result = recognizer.recognize(silent_audio.tobytes())
        print(f"Silent audio result: '{result}'")
        
        # Test with generated speech-like audio
        print("Testing with generated audio...")
        # Generate a simple tone that might trigger some recognition
        sample_rate = 16000
        duration = 2.0
        frequency = 300  # Low frequency like speech
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        # Create a modulated signal that resembles speech patterns
        speech_like = np.sin(2 * np.pi * frequency * t) * np.sin(2 * np.pi * 10 * t)
        speech_like = (speech_like * 16000).astype(np.int16)
        
        result = recognizer.recognize(speech_like.tobytes())
        print(f"Generated audio result: '{result}'")
        
        recognizer.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing SpeechRecognizer: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_live_speech_recognition():
    """Test speech recognition with live microphone input"""
    print("\n=== Testing Live Speech Recognition ===")
    
    try:
        from src.audio.microphone import Microphone
        from src.speech.recognizer import SpeechRecognizer
        
        # Initialize components
        mic = Microphone(sample_rate=16000, channels=1, chunk_size=1024)
        recognizer = SpeechRecognizer(
            model_path="models/vosk-model-small-en-us-0.15",
            sample_rate=16000
        )
        
        print("✅ Components initialized")
        print("\n🎤 Live Speech Recognition Test")
        print("Say something clearly into the microphone...")
        print("Try simple words like: 'hello', 'test', 'one two three'")
        print("Press Ctrl+C to stop")
        
        mic.start_stream()
        
        for i in range(3):  # Try 3 times
            print(f"\n--- Test {i+1}/3 ---")
            print("Speak now...")
            
            try:
                # Record for a fixed duration
                audio_data = mic.record_until_silence(
                    silence_threshold=300,  # Lower threshold
                    silence_duration=1.0,   # Shorter silence
                    max_duration=5.0        # Shorter max duration
                )
                
                if audio_data:
                    print(f"Recorded {len(audio_data)} bytes of audio")
                    
                    # Test recognition
                    result = recognizer.recognize(audio_data)
                    
                    if result and result.strip():
                        print(f"✅ Recognized: '{result}'")
                    else:
                        print("❌ No speech recognized (empty result)")
                        
                    # Also test with raw Vosk for comparison
                    print("Testing with raw Vosk...")
                    import vosk
                    import json
                    
                    model = vosk.Model("models/vosk-model-small-en-us-0.15")
                    rec = vosk.KaldiRecognizer(model, 16000)
                    
                    # Convert audio data to the right format
                    audio_np = np.frombuffer(audio_data, dtype=np.int16)
                    
                    if rec.AcceptWaveform(audio_data):
                        result_dict = json.loads(rec.Result())
                        raw_result = result_dict.get('text', '')
                        print(f"Raw Vosk result: '{raw_result}'")
                    else:
                        partial_dict = json.loads(rec.PartialResult())
                        partial_result = partial_dict.get('partial', '')
                        print(f"Partial Vosk result: '{partial_result}'")
                        
                else:
                    print("❌ No audio recorded")
                    
            except KeyboardInterrupt:
                print("\nStopped by user")
                break
            except Exception as e:
                print(f"❌ Error during test: {e}")
        
        mic.close()
        recognizer.close()
        return True
        
    except Exception as e:
        print(f"❌ Error in live test: {e}")
        import traceback
        traceback.print_exc()
        return False

def download_vosk_model():
    """Download the Vosk model if missing"""
    print("\n=== Downloading Vosk Model ===")
    
    model_path = Path("models/vosk-model-small-en-us-0.15")
    if model_path.exists():
        print("✅ Model already exists")
        return True
    
    try:
        import subprocess
        import urllib.request
        
        print("Downloading Vosk model (this may take a few minutes)...")
        
        # Create models directory
        Path("models").mkdir(exist_ok=True)
        
        # Download model
        url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        zip_file = "models/vosk-model-small-en-us-0.15.zip"
        
        print(f"Downloading from: {url}")
        urllib.request.urlretrieve(url, zip_file)
        print("✅ Download completed")
        
        # Extract model
        print("Extracting model...")
        import zipfile
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall("models/")
        
        # Clean up zip file
        os.remove(zip_file)
        
        print("✅ Model extracted successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("🎤 Speech Recognition Diagnostic Tool")
    print("=" * 50)
    
    # Check if model exists
    if not check_vosk_model():
        print("\n🔧 Attempting to download model...")
        if not download_vosk_model():
            print("❌ Failed to download model. Please download manually:")
            print("   wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
            print("   unzip vosk-model-small-en-us-0.15.zip -d models/")
            return
    
    # Test Vosk import
    if not test_vosk_import():
        print("❌ Vosk import failed. Cannot proceed with tests.")
        return
    
    # Test our speech recognizer
    if not test_speech_recognizer():
        print("❌ SpeechRecognizer class failed. Check implementation.")
        return
    
    # Test live recognition
    print("\n" + "=" * 50)
    choice = input("Do you want to test live speech recognition? (y/N): ").strip().lower()
    if choice in ['y', 'yes']:
        test_live_speech_recognition()
    
    print("\n" + "=" * 50)
    print("🔧 Troubleshooting Summary:")
    print("- If model missing: Run this script to download it")
    print("- If no recognition: Speak louder and clearer")
    print("- If partial recognition: Lower silence threshold in config")
    print("- If still issues: Try different Vosk model")

if __name__ == "__main__":
    main()