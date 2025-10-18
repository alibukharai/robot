#!/usr/bin/env python3
"""
Test the speech recognition fix
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, '.')

def test_fixed_speech_recognition():
    """Test the fixed speech recognition"""
    try:
        from src.audio.microphone import Microphone
        from src.speech.recognizer import SpeechRecognizer
        
        print("🎤 Testing Fixed Speech Recognition")
        print("=" * 40)
        
        # Initialize components
        mic = Microphone(sample_rate=16000, channels=1, chunk_size=1024)
        recognizer = SpeechRecognizer(
            model_path="models/vosk-model-small-en-us-0.15",
            sample_rate=16000
        )
        
        print("✅ Components initialized")
        print("\nSpeak clearly into the microphone...")
        print("Try: 'I want a cheeseburger' or 'Hello test'")
        
        mic.start_stream()
        
        for i in range(3):
            print(f"\n--- Test {i+1}/3 ---")
            input("Press ENTER then speak...")
            
            # Record audio
            audio_data = mic.record_until_silence(
                silence_threshold=400,
                silence_duration=1.0,
                max_duration=5.0
            )
            
            if audio_data:
                print(f"Recorded {len(audio_data)} bytes")
                
                # Test recognition with fixed method
                result = recognizer.recognize(audio_data)
                
                if result and result.strip():
                    print(f"🎉 SUCCESS: '{result}'")
                else:
                    print("❌ No speech recognized")
            else:
                print("❌ No audio recorded")
        
        mic.close()
        recognizer.close()
        
        print("\n✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_speech_recognition()