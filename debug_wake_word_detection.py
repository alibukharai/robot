#!/usr/bin/env python3
"""
Wake Word Detection Debug Tool
This script helps debug why wake word detection isn't working despite good audio
"""

import sys
import time
import numpy as np
import logging

# Add current directory to path
sys.path.insert(0, '.')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_wake_word_with_debug():
    """Test wake word detection with detailed debugging"""
    try:
        from src.audio.microphone import Microphone
        from src.wake_word.detector import WakeWordDetector
        
        print("=== Wake Word Detection Debug ===")
        
        # Initialize components with debug settings
        mic = Microphone(sample_rate=16000, channels=1, chunk_size=1024)
        
        # Test different thresholds
        thresholds = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        for threshold in thresholds:
            print(f"\n🎯 Testing with threshold: {threshold}")
            print(f"   (Lower = more sensitive, Higher = more strict)")
            
            detector = WakeWordDetector(model_name='hey_jarvis', threshold=threshold)
            mic.start_stream()
            
            print(f"   Say 'Hey Jarvis' clearly and loudly...")
            print(f"   Listening for 15 seconds...")
            
            start_time = time.time()
            max_score = 0.0
            detection_count = 0
            audio_chunks = 0
            
            try:
                while time.time() - start_time < 15:
                    audio_chunk = mic.read_chunk()
                    if audio_chunk is not None:
                        audio_chunks += 1
                        
                        # Calculate audio level
                        audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
                        rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
                        
                        # Test detection
                        detected = detector.detect(audio_chunk)
                        
                        # Get prediction scores for all models
                        audio_float = audio_data.astype(np.float32) / 32768.0
                        predictions = detector.model.predict(audio_float)
                        
                        # Track scores
                        hey_jarvis_score = predictions.get('hey_jarvis', 0.0)
                        max_score = max(max_score, hey_jarvis_score)
                        
                        if detected:
                            detection_count += 1
                            print(f"\n   🎉 DETECTED! Score: {hey_jarvis_score:.3f} (threshold: {threshold})")
                        
                        # Show real-time feedback every 50 chunks
                        if audio_chunks % 50 == 0:
                            level_bar = "█" * min(int(rms / 1000), 20)
                            score_bar = "█" * min(int(hey_jarvis_score * 100), 20)
                            print(f"\r   Audio: {rms:4.0f} |{level_bar:<20}| Score: {hey_jarvis_score:.3f} |{score_bar:<20}|", end="", flush=True)
                    
                    time.sleep(0.05)
                    
            except KeyboardInterrupt:
                print("\n   Stopped by user")
                
            mic.stop_stream()
            detector.close()
            
            print(f"\n   📊 Results for threshold {threshold}:")
            print(f"      Detections: {detection_count}")
            print(f"      Max score: {max_score:.3f}")
            print(f"      Audio chunks: {audio_chunks}")
            
            if detection_count > 0:
                print(f"      ✅ Wake word detected with threshold {threshold}!")
                break
            elif max_score > 0.1:
                print(f"      ⚠️  Getting close - max score was {max_score:.3f}")
            else:
                print(f"      ❌ No detection - very low scores")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in wake word test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_all_wake_word_models():
    """Test all available wake word models to see which works best"""
    try:
        from src.audio.microphone import Microphone
        from src.wake_word.detector import WakeWordDetector
        
        print("\n=== Testing All Wake Word Models ===")
        
        # Get available models
        detector = WakeWordDetector(model_name='hey_jarvis', threshold=0.3)
        available_models = list(detector.model.models.keys())
        detector.close()
        
        print(f"Available models: {available_models}")
        
        mic = Microphone(sample_rate=16000, channels=1, chunk_size=1024)
        
        for model_name in available_models:
            print(f"\n🎯 Testing model: {model_name}")
            
            if model_name == 'hey_jarvis':
                print("   Say: 'Hey Jarvis'")
            elif model_name == 'alexa':
                print("   Say: 'Alexa'")
            elif model_name == 'hey_mycroft':
                print("   Say: 'Hey Mycroft'")
            elif 'timer' in model_name:
                print("   Say: 'Set timer' or 'Timer'")
            elif model_name == 'weather':
                print("   Say: 'Weather'")
            else:
                print(f"   Say: '{model_name}'")
            
            detector = WakeWordDetector(model_name=model_name, threshold=0.3)
            mic.start_stream()
            
            start_time = time.time()
            max_score = 0.0
            detections = 0
            
            try:
                while time.time() - start_time < 10:  # 10 seconds per model
                    audio_chunk = mic.read_chunk()
                    if audio_chunk is not None:
                        detected = detector.detect(audio_chunk)
                        
                        # Get score for this model
                        audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
                        audio_float = audio_data.astype(np.float32) / 32768.0
                        predictions = detector.model.predict(audio_float)
                        score = predictions.get(model_name, 0.0)
                        max_score = max(max_score, score)
                        
                        if detected:
                            detections += 1
                            print(f"\n   🎉 {model_name.upper()} DETECTED! Score: {score:.3f}")
                    
                    time.sleep(0.05)
                    
            except KeyboardInterrupt:
                print(f"\n   Skipping {model_name}")
                
            mic.stop_stream()
            detector.close()
            
            print(f"   Results: {detections} detections, max score: {max_score:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing models: {e}")
        return False

def test_pronunciation_variations():
    """Test different pronunciations of 'Hey Jarvis'"""
    try:
        from src.audio.microphone import Microphone
        from src.wake_word.detector import WakeWordDetector
        
        print("\n=== Testing Pronunciation Variations ===")
        print("Try these different ways to say 'Hey Jarvis':")
        print("1. 'Hey JAR-vis' (emphasize JAR)")
        print("2. 'HEY Jarvis' (emphasize HEY)")
        print("3. 'Hey Jar-VIS' (emphasize VIS)")
        print("4. Speak slower: 'Hey... Jarvis'")
        print("5. Speak faster: 'HeyJarvis'")
        print("6. Different accent/tone")
        
        mic = Microphone(sample_rate=16000, channels=1, chunk_size=1024)
        detector = WakeWordDetector(model_name='hey_jarvis', threshold=0.2)  # Very sensitive
        
        mic.start_stream()
        
        print("\nListening for 30 seconds... Try all variations!")
        start_time = time.time()
        best_score = 0.0
        total_detections = 0
        
        try:
            while time.time() - start_time < 30:
                audio_chunk = mic.read_chunk()
                if audio_chunk is not None:
                    detected = detector.detect(audio_chunk)
                    
                    # Get score
                    audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
                    audio_float = audio_data.astype(np.float32) / 32768.0
                    predictions = detector.model.predict(audio_float)
                    score = predictions.get('hey_jarvis', 0.0)
                    best_score = max(best_score, score)
                    
                    if detected:
                        total_detections += 1
                        print(f"\n🎉 DETECTED! Score: {score:.3f} - Keep using this pronunciation!")
                    elif score > 0.1:
                        print(f"\n📈 Close! Score: {score:.3f} - Try speaking clearer")
                
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\nStopped by user")
            
        mic.stop_stream()
        detector.close()
        
        print(f"\n📊 Final Results:")
        print(f"   Total detections: {total_detections}")
        print(f"   Best score achieved: {best_score:.3f}")
        
        if total_detections > 0:
            print("   ✅ Success! Use the pronunciation that worked best.")
        elif best_score > 0.15:
            print("   ⚠️  Close! Try lowering the threshold in config/settings.yaml")
        else:
            print("   ❌ Very low scores. There may be a deeper issue.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing pronunciations: {e}")
        return False

def main():
    """Main debug function"""
    print("🐛 Wake Word Detection Debug Tool")
    print("=" * 50)
    
    while True:
        print("\nChoose a debug test:")
        print("1. Test different sensitivity thresholds")
        print("2. Test all available wake word models")
        print("3. Test pronunciation variations")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            test_wake_word_with_debug()
        elif choice == '2':
            test_all_wake_word_models()
        elif choice == '3':
            test_pronunciation_variations()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please enter 1-4.")
    
    print("\n🔧 Troubleshooting Summary:")
    print("- If no detections: Lower threshold in config/settings.yaml")
    print("- If low scores: Try different pronunciations or models")
    print("- If audio issues: Check microphone positioning")
    print("- If still problems: The model may need retraining")

if __name__ == "__main__":
    main()