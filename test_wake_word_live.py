#!/usr/bin/env python3
"""
Live Wake Word Detection Test
This script helps you test and debug wake word detection in real-time
"""

import sys
import time
import logging
import numpy as np
from pathlib import Path

# Add current directory to path
sys.path.insert(0, '.')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_microphone():
    """Test microphone input and show audio levels"""
    try:
        from src.audio.microphone import Microphone
        
        print("=== Testing Microphone ===")
        
        # Initialize microphone with same settings as main app
        mic = Microphone(
            sample_rate=16000,
            channels=1,
            chunk_size=1024,
            device_name=None  # Auto-detect ReSpeaker
        )
        
        print(f"✓ Microphone initialized")
        print(f"  Device: {mic.device_info['name'] if hasattr(mic, 'device_info') else 'Unknown'}")
        print(f"  Sample rate: {mic.sample_rate}Hz")
        print(f"  Channels: {mic.channels}")
        
        # Start audio stream
        mic.start_stream()
        print("✓ Audio stream started")
        
        print("\n=== Audio Level Monitor ===")
        print("Speak into the microphone to see audio levels...")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            while True:
                # Read audio chunk
                audio_chunk = mic.read_chunk()
                if audio_chunk is not None:
                    # Convert to numpy array and calculate RMS level
                    audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
                    rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
                    
                    # Create visual level indicator
                    level_bars = int(rms / 1000)  # Scale for display
                    level_display = "█" * min(level_bars, 50)
                    
                    # Print level with timestamp
                    print(f"\rAudio Level: {rms:6.0f} |{level_display:<50}|", end="", flush=True)
                
                time.sleep(0.1)  # Update 10 times per second
                
        except KeyboardInterrupt:
            print("\n\nStopping audio monitor...")
            
        mic.close()
        print("✓ Microphone closed")
        return True
        
    except Exception as e:
        print(f"✗ Microphone test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wake_word_detection():
    """Test wake word detection with visual feedback"""
    try:
        from src.audio.microphone import Microphone
        from src.wake_word.detector import WakeWordDetector
        
        print("\n=== Testing Wake Word Detection ===")
        
        # Initialize components
        mic = Microphone(sample_rate=16000, channels=1, chunk_size=1024)
        detector = WakeWordDetector(model_name='hey_jarvis', threshold=0.3)  # Lower threshold for testing
        
        print(f"✓ Components initialized")
        print(f"  Wake word: hey_jarvis")
        print(f"  Threshold: 0.3 (lowered for testing)")
        print(f"  Available models: {list(detector.model.models.keys())}")
        
        # Start audio stream
        mic.start_stream()
        
        print("\n=== Wake Word Detection Test ===")
        print("Say 'Hey Jarvis' clearly into the microphone...")
        print("You should see detection scores and audio levels below.")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            chunk_count = 0
            while True:
                # Read audio chunk
                audio_chunk = mic.read_chunk()
                if audio_chunk is not None:
                    chunk_count += 1
                    
                    # Calculate audio level
                    audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
                    rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
                    
                    # Test wake word detection
                    detected = detector.detect(audio_chunk)
                    
                    # Get prediction scores for debugging
                    audio_float = audio_data.astype(np.float32) / 32768.0
                    predictions = detector.model.predict(audio_float)
                    hey_jarvis_score = predictions.get('hey_jarvis', 0.0)
                    
                    # Create visual indicators
                    level_bars = "█" * min(int(rms / 1000), 30)
                    score_bars = "█" * min(int(hey_jarvis_score * 100), 30)
                    
                    # Print status
                    status = "🎯 DETECTED!" if detected else "   listening..."
                    print(f"\r{status} | Audio: {rms:4.0f} |{level_bars:<30}| Score: {hey_jarvis_score:.3f} |{score_bars:<30}|", end="", flush=True)
                    
                    if detected:
                        print(f"\n🎉 Wake word detected! Score: {hey_jarvis_score:.3f}")
                        print("   Continuing to listen...")
                
                time.sleep(0.05)  # Update 20 times per second
                
        except KeyboardInterrupt:
            print("\n\nStopping wake word test...")
            
        mic.close()
        detector.close()
        print("✓ Test completed")
        return True
        
    except Exception as e:
        print(f"✗ Wake word test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_thresholds():
    """Test wake word detection with different thresholds"""
    try:
        from src.audio.microphone import Microphone
        from src.wake_word.detector import WakeWordDetector
        
        print("\n=== Testing Different Thresholds ===")
        print("This will test wake word detection with various sensitivity levels")
        print()
        
        thresholds = [0.1, 0.3, 0.5, 0.7, 0.9]
        
        for threshold in thresholds:
            print(f"\nTesting with threshold: {threshold}")
            print(f"Say 'Hey Jarvis' (lower threshold = more sensitive)")
            
            # Initialize components
            mic = Microphone(sample_rate=16000, channels=1, chunk_size=1024)
            detector = WakeWordDetector(model_name='hey_jarvis', threshold=threshold)
            mic.start_stream()
            
            print("Listening for 10 seconds...")
            start_time = time.time()
            detections = 0
            
            try:
                while time.time() - start_time < 10:
                    audio_chunk = mic.read_chunk()
                    if audio_chunk is not None:
                        if detector.detect(audio_chunk):
                            detections += 1
                            print(f"  ✓ Detection #{detections} at threshold {threshold}")
                    
                    time.sleep(0.05)
                    
            except KeyboardInterrupt:
                break
                
            mic.close()
            detector.close()
            print(f"  Result: {detections} detections in 10 seconds")
        
        return True
        
    except Exception as e:
        print(f"✗ Threshold test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== Wake Word Detection Diagnostic Tool ===")
    print()
    
    while True:
        print("\nChoose a test:")
        print("1. Test microphone and audio levels")
        print("2. Test wake word detection (live)")
        print("3. Test different sensitivity thresholds")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            test_microphone()
        elif choice == '2':
            test_wake_word_detection()
        elif choice == '3':
            test_different_thresholds()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please enter 1-4.")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()