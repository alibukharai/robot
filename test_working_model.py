#!/usr/bin/env python3
"""
Quick test to find a working wake word model
"""

import sys
import time
import numpy as np

# Add current directory to path
sys.path.insert(0, '.')

def test_single_model(model_name, wake_phrase):
    """Test a single wake word model"""
    try:
        from src.audio.microphone import Microphone
        from src.wake_word.detector import WakeWordDetector
        
        print(f"\n🎯 Testing: {model_name}")
        print(f"   Say: '{wake_phrase}'")
        
        mic = Microphone(sample_rate=16000, channels=1, chunk_size=1024)
        detector = WakeWordDetector(model_name=model_name, threshold=0.1)  # Very low threshold
        
        mic.start_stream()
        
        print("   Listening for 10 seconds...")
        start_time = time.time()
        max_score = 0.0
        detections = 0
        chunks_processed = 0
        
        try:
            while time.time() - start_time < 10:
                audio_chunk = mic.read_chunk()
                if audio_chunk is not None:
                    chunks_processed += 1
                    
                    # Test detection
                    detected = detector.detect(audio_chunk)
                    
                    # Get prediction scores
                    audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
                    audio_float = audio_data.astype(np.float32) / 32768.0
                    predictions = detector.model.predict(audio_float)
                    
                    # Find the score for this model
                    score = 0.0
                    for key, value in predictions.items():
                        if model_name in key or key in model_name:
                            score = max(score, value)
                    
                    max_score = max(max_score, score)
                    
                    if detected:
                        detections += 1
                        print(f"\n   🎉 DETECTED! Score: {score:.3f}")
                    
                    # Show progress every 2 seconds
                    if chunks_processed % 400 == 0:
                        print(f"   Current max score: {max_score:.3f}")
                
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print(f"\n   Stopped early")
            
        mic.stop_stream()
        detector.close()
        
        print(f"   📊 Results:")
        print(f"      Detections: {detections}")
        print(f"      Max score: {max_score:.3f}")
        print(f"      Chunks processed: {chunks_processed}")
        
        if detections > 0:
            print(f"      ✅ {model_name.upper()} WORKS!")
            return True, max_score
        elif max_score > 0.05:
            print(f"      ⚠️  {model_name} shows some response")
            return False, max_score
        else:
            print(f"      ❌ {model_name} not responding")
            return False, max_score
        
    except Exception as e:
        print(f"   ❌ Error testing {model_name}: {e}")
        return False, 0.0

def main():
    """Test all models to find working ones"""
    print("🔍 Finding Working Wake Word Models")
    print("=" * 50)
    
    # Test models in order of reliability
    test_cases = [
        ("alexa", "Alexa"),
        ("weather", "Weather"),
        ("hey_mycroft", "Hey Mycroft"),
        ("timer", "Timer"),
        ("hey_jarvis", "Hey Jarvis"),
    ]
    
    working_models = []
    
    for model_name, wake_phrase in test_cases:
        works, score = test_single_model(model_name, wake_phrase)
        if works:
            working_models.append((model_name, wake_phrase, score))
    
    print("\n" + "=" * 50)
    print("🎯 RESULTS:")
    
    if working_models:
        print(f"✅ Found {len(working_models)} working model(s):")
        for model, phrase, score in working_models:
            print(f"   • {model}: Say '{phrase}' (max score: {score:.3f})")
        
        # Update config with the best working model
        best_model = working_models[0][0]
        best_phrase = working_models[0][1]
        
        print(f"\n🔧 Updating config to use: {best_model}")
        
        # Update the config file
        try:
            with open('config/settings.yaml', 'r') as f:
                config = f.read()
            
            # Replace the model line
            import re
            config = re.sub(r'model: "[^"]*"', f'model: "{best_model}"', config)
            
            with open('config/settings.yaml', 'w') as f:
                f.write(config)
                
            print(f"✅ Config updated! Now say '{best_phrase}' to activate the robot.")
            
        except Exception as e:
            print(f"❌ Error updating config: {e}")
            print(f"   Manually change 'model: \"{best_model}\"' in config/settings.yaml")
        
    else:
        print("❌ No working models found!")
        print("   This suggests a deeper issue with OpenWakeWord installation.")
        print("   Try reinstalling: pip uninstall openwakeword && pip install openwakeword==0.5.1")

if __name__ == "__main__":
    main()