#!/usr/bin/env python3
"""
Audio Hardware Diagnostic Tool
This script helps diagnose ReSpeaker microphone issues
"""

import sys
import subprocess
import time
import numpy as np

def check_audio_devices():
    """Check available audio devices"""
    print("=== Audio Devices Diagnostic ===")
    
    try:
        import pyaudio
        
        # Initialize PyAudio
        pa = pyaudio.PyAudio()
        
        print(f"PyAudio version: {pyaudio.__version__}")
        print(f"Available audio devices: {pa.get_device_count()}")
        print()
        
        # List all audio devices
        respeaker_devices = []
        for i in range(pa.get_device_count()):
            try:
                info = pa.get_device_info_by_index(i)
                print(f"Device {i}: {info['name']}")
                print(f"  Channels: {info['maxInputChannels']} in, {info['maxOutputChannels']} out")
                print(f"  Sample Rate: {info['defaultSampleRate']} Hz")
                print(f"  Host API: {pa.get_host_api_info_by_index(info['hostApi'])['name']}")
                
                # Check if it's a ReSpeaker device
                if 'respeaker' in info['name'].lower() or 'xmos' in info['name'].lower():
                    respeaker_devices.append((i, info))
                    print("  *** RESPEAKER DEVICE DETECTED ***")
                
                print()
                
            except Exception as e:
                print(f"  Error getting info for device {i}: {e}")
        
        pa.terminate()
        
        if respeaker_devices:
            print(f"✓ Found {len(respeaker_devices)} ReSpeaker device(s)")
            return respeaker_devices
        else:
            print("❌ No ReSpeaker devices found!")
            return []
            
    except Exception as e:
        print(f"❌ Error checking audio devices: {e}")
        return []

def check_alsa_devices():
    """Check ALSA audio devices"""
    print("=== ALSA Devices ===")
    
    try:
        # List ALSA capture devices
        result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            print("ALSA capture devices:")
            print(result.stdout)
        else:
            print("❌ Error listing ALSA devices:", result.stderr)
            
        # List ALSA playback devices  
        result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            print("ALSA playback devices:")
            print(result.stdout)
        else:
            print("❌ Error listing ALSA playback devices:", result.stderr)
            
    except FileNotFoundError:
        print("❌ ALSA tools not found. Install with: sudo apt-get install alsa-utils")
    except Exception as e:
        print(f"❌ Error checking ALSA: {e}")

def test_microphone_recording(device_index=None):
    """Test recording from microphone"""
    print("=== Microphone Recording Test ===")
    
    try:
        import pyaudio
        
        # Audio parameters
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        pa = pyaudio.PyAudio()
        
        # Try to open the audio stream
        if device_index is not None:
            print(f"Testing device {device_index}...")
            device_info = pa.get_device_info_by_index(device_index)
            print(f"Device: {device_info['name']}")
        else:
            print("Testing default input device...")
            
        try:
            stream = pa.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=CHUNK
            )
            
            print("✓ Audio stream opened successfully")
            print("Recording for 5 seconds... Speak into the microphone!")
            print("Press Ctrl+C to stop early")
            
            max_level = 0
            total_samples = 0
            
            try:
                for i in range(int(RATE / CHUNK * 5)):  # 5 seconds
                    try:
                        data = stream.read(CHUNK, exception_on_overflow=False)
                        
                        # Convert to numpy array and calculate level
                        audio_data = np.frombuffer(data, dtype=np.int16)
                        rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
                        max_level = max(max_level, rms)
                        total_samples += len(audio_data)
                        
                        # Visual level indicator
                        level_bars = "█" * min(int(rms / 500), 50)
                        print(f"\rLevel: {rms:6.0f} |{level_bars:<50}| Max: {max_level:6.0f}", end="", flush=True)
                        
                    except Exception as e:
                        print(f"\n❌ Error reading audio: {e}")
                        break
                        
            except KeyboardInterrupt:
                print("\n⏹️  Recording stopped by user")
                
            print(f"\n\n📊 Recording Results:")
            print(f"   Total samples: {total_samples}")
            print(f"   Maximum level: {max_level:.0f}")
            
            if max_level > 1000:
                print("✅ Good audio levels detected!")
            elif max_level > 100:
                print("⚠️  Low audio levels - try speaking louder")
            else:
                print("❌ No audio detected - microphone may not be working")
                
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"❌ Error opening audio stream: {e}")
            
        pa.terminate()
        
    except Exception as e:
        print(f"❌ Error in microphone test: {e}")

def test_respeaker_leds():
    """Test ReSpeaker LED indicators (if available)"""
    print("=== ReSpeaker LED Test ===")
    
    try:
        # Try to control ReSpeaker LEDs to verify hardware connection
        import subprocess
        
        # Check if ReSpeaker control tools are available
        result = subprocess.run(['which', 'respeaker_control'], capture_output=True)
        if result.returncode == 0:
            print("✓ ReSpeaker control tools found")
            
            # Try to control LEDs
            subprocess.run(['respeaker_control', '--led_ring', '0xff0000'], timeout=5)
            time.sleep(1)
            subprocess.run(['respeaker_control', '--led_ring', '0x000000'], timeout=5)
            print("✓ LED test completed")
        else:
            print("⚠️  ReSpeaker control tools not found")
            print("   Install with: pip install respeaker")
            
    except Exception as e:
        print(f"⚠️  LED test failed: {e}")

def check_usb_devices():
    """Check USB devices for ReSpeaker"""
    print("=== USB Devices ===")
    
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            respeaker_found = False
            
            for line in lines:
                if line.strip():
                    print(line)
                    if 'xmos' in line.lower() or 'respeaker' in line.lower():
                        print("  *** RESPEAKER USB DEVICE DETECTED ***")
                        respeaker_found = True
                        
            if not respeaker_found:
                print("\n❌ No ReSpeaker USB device found!")
                print("   Check USB connection and power")
        else:
            print("❌ Error listing USB devices")
            
    except Exception as e:
        print(f"❌ Error checking USB: {e}")

def main():
    """Main diagnostic function"""
    print("🎤 ReSpeaker Audio Diagnostic Tool")
    print("=" * 50)
    
    # Check USB devices first
    check_usb_devices()
    print()
    
    # Check ALSA devices
    check_alsa_devices()
    print()
    
    # Check PyAudio devices
    respeaker_devices = check_audio_devices()
    print()
    
    # Test ReSpeaker LEDs
    test_respeaker_leds()
    print()
    
    # Test microphone recording
    if respeaker_devices:
        print("Testing ReSpeaker devices:")
        for device_index, device_info in respeaker_devices:
            print(f"\nTesting device {device_index}: {device_info['name']}")
            test_microphone_recording(device_index)
    else:
        print("No ReSpeaker devices found. Testing default input:")
        test_microphone_recording()
    
    print("\n" + "=" * 50)
    print("🔧 Troubleshooting Tips:")
    print("1. Check USB connection - unplug and reconnect ReSpeaker")
    print("2. Check power - some ReSpeakers need external power")
    print("3. Check drivers - run: sudo apt-get install linux-modules-extra-$(uname -r)")
    print("4. Reboot the system after connecting ReSpeaker")
    print("5. Try different USB ports")

if __name__ == "__main__":
    main()