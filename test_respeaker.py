#!/usr/bin/env python3
"""
ReSpeaker Mic Array v2.0 - Test and Diagnostic Tool
Tests USB connection, audio capture, and provides device information
"""

import sys
import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def check_usb_connection():
    """Check if ReSpeaker is connected via USB."""
    print("\n" + "="*60)
    print("1. Checking USB Connection")
    print("="*60)
    
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        output = result.stdout
        
        # Check for ReSpeaker specific VID:PID
        if '2886:0018' in output:
            print("✅ ReSpeaker Mic Array v2.0 detected!")
            for line in output.split('\n'):
                if '2886:0018' in line:
                    print(f"   {line}")
            return True
        # Check for XMOS chipset
        elif 'xmos' in output.lower() or 'XVF3000' in output:
            print("✅ XMOS device detected (likely ReSpeaker)")
            for line in output.split('\n'):
                if 'xmos' in line.lower() or 'XVF3000' in line:
                    print(f"   {line}")
            return True
        else:
            print("❌ ReSpeaker not detected via USB")
            print("\nAll USB devices:")
            print(output)
            return False
            
    except Exception as e:
        print(f"❌ Error checking USB: {e}")
        return False


def check_audio_devices():
    """Check if ReSpeaker appears as audio device."""
    print("\n" + "="*60)
    print("2. Checking Audio Devices")
    print("="*60)
    
    try:
        # Check capture devices
        print("\n📥 Audio Input Devices:")
        result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
        output = result.stdout
        
        found = False
        respeaker_keywords = ['respeaker', 'xmos', 'usb audio', 'usb pnp']
        
        for line in output.split('\n'):
            if any(keyword in line.lower() for keyword in respeaker_keywords):
                print(f"   ✅ {line}")
                found = True
            elif 'card' in line.lower():
                print(f"   {line}")
        
        if not found:
            print("   ⚠️  ReSpeaker not found in audio input devices")
            
        # Check playback devices
        print("\n📤 Audio Output Devices:")
        result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
        output = result.stdout
        
        for line in output.split('\n'):
            if any(keyword in line.lower() for keyword in respeaker_keywords):
                print(f"   ✅ {line}")
            elif 'card' in line.lower():
                print(f"   {line}")
                
        return found
        
    except Exception as e:
        print(f"❌ Error checking audio devices: {e}")
        return False


def test_pyaudio_detection():
    """Test if PyAudio can detect ReSpeaker."""
    print("\n" + "="*60)
    print("3. Testing PyAudio Detection")
    print("="*60)
    
    try:
        import pyaudio
        
        audio = pyaudio.PyAudio()
        
        print("\n🎤 Input Devices:")
        respeaker_index = None
        
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            
            # Only show input devices
            if info.get('maxInputChannels', 0) > 0:
                name = info.get('name', '')
                channels = info.get('maxInputChannels', 0)
                rate = int(info.get('defaultSampleRate', 0))
                
                # Check if this is ReSpeaker
                is_respeaker = any(keyword in name.lower() 
                                  for keyword in ['respeaker', 'xmos', 'usb pnp'])
                
                if is_respeaker:
                    print(f"   ✅ [{i}] {name}")
                    print(f"       Channels: {channels}, Sample Rate: {rate} Hz")
                    respeaker_index = i
                else:
                    print(f"   [ {i}] {name}")
                    print(f"       Channels: {channels}, Sample Rate: {rate} Hz")
        
        audio.terminate()
        
        if respeaker_index is not None:
            print(f"\n✅ ReSpeaker detected at index {respeaker_index}")
            return True, respeaker_index
        else:
            print("\n⚠️  ReSpeaker not auto-detected via PyAudio")
            return False, None
            
    except ImportError:
        print("❌ PyAudio not installed")
        print("   Install with: pip install pyaudio")
        return False, None
    except Exception as e:
        print(f"❌ Error testing PyAudio: {e}")
        return False, None


def test_audio_capture(device_index=None):
    """Test actual audio capture from ReSpeaker."""
    print("\n" + "="*60)
    print("4. Testing Audio Capture")
    print("="*60)
    
    try:
        import pyaudio
        import numpy as np
        
        audio = pyaudio.PyAudio()
        
        # Open stream
        print("\n🎙️  Opening audio stream...")
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,  # Mono, channel 0
            rate=16000,  # Max rate for ReSpeaker
            input=True,
            input_device_index=device_index,
            frames_per_buffer=1024
        )
        
        print("✅ Stream opened successfully")
        print("\n📊 Capturing 2 seconds of audio for analysis...")
        print("   (Make some noise to test!)")
        
        # Capture audio
        frames = []
        for i in range(int(16000 / 1024 * 2)):  # 2 seconds
            data = stream.read(1024, exception_on_overflow=False)
            frames.append(data)
            
            # Calculate amplitude
            audio_data = np.frombuffer(data, dtype=np.int16)
            amplitude = np.abs(audio_data).mean()
            
            # Show visual indicator
            bars = int(amplitude / 100)
            print(f"   {'█' * bars} {amplitude:.0f}", end='\r')
        
        print("\n\n✅ Audio capture successful!")
        
        # Analyze captured audio
        all_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        avg_amplitude = np.abs(all_data).mean()
        max_amplitude = np.abs(all_data).max()
        
        print("\n📈 Audio Statistics:")
        print(f"   Average amplitude: {avg_amplitude:.2f}")
        print(f"   Maximum amplitude: {max_amplitude:.2f}")
        
        if avg_amplitude < 10:
            print("   ⚠️  Very low audio level - check microphone gain")
        elif avg_amplitude < 100:
            print("   ⚠️  Low audio level - consider increasing gain")
        elif avg_amplitude < 1000:
            print("   ✅ Good audio level")
        else:
            print("   ⚠️  High audio level - may cause distortion")
        
        # Clean up
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        return True
        
    except ImportError:
        print("❌ Required libraries not installed")
        print("   Install with: pip install pyaudio numpy")
        return False
    except Exception as e:
        print(f"❌ Error during audio capture: {e}")
        return False


def test_with_robot_code():
    """Test using the actual robot microphone class."""
    print("\n" + "="*60)
    print("5. Testing Robot Microphone Class")
    print("="*60)
    
    try:
        from src.audio.microphone import Microphone
        
        print("\n🤖 Creating Microphone instance...")
        mic = Microphone()  # Auto-detect
        
        print("✅ Microphone class initialized")
        
        print("\n📋 Listing all audio devices:")
        mic.list_devices()
        
        print("\n🎙️  Testing audio capture...")
        mic.start_stream()
        
        print("✅ Stream started")
        print("📊 Reading 10 audio chunks...")
        
        for i in range(10):
            chunk = mic.read_chunk()
            if chunk:
                print(f"   ✅ Chunk {i+1}/10 received ({len(chunk)} bytes)")
            else:
                print(f"   ❌ Chunk {i+1}/10 failed")
        
        mic.stop_stream()
        mic.close()
        
        print("\n✅ Robot microphone class works correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import robot code: {e}")
        print("   Make sure you're in the robot directory")
        return False
    except Exception as e:
        print(f"❌ Error testing robot code: {e}")
        return False


def print_recommendations():
    """Print recommendations based on test results."""
    print("\n" + "="*60)
    print("Recommendations")
    print("="*60)
    
    print("""
✅ If all tests passed:
   - Your ReSpeaker is working correctly
   - You can run: python3 src/main.py
   
⚠️  If audio level is low:
   - Run: alsamixer
   - Press F6, select ReSpeaker
   - Press F4 for capture controls
   - Increase volume to 80-90%
   
⚠️  If device not detected:
   - Check USB cable connection
   - Try different USB port (USB 3.0 recommended)
   - Run: dmesg | tail -20
   - See: docs/RESPEAKER_SETUP.md
   
📚 More Information:
   - ReSpeaker Setup Guide: docs/RESPEAKER_SETUP.md
   - Main README: README.md
   - Quick Start: QUICKSTART.md
    """)


def main():
    """Run all tests."""
    print("="*60)
    print("ReSpeaker Mic Array v2.0 - Diagnostic Tool")
    print("="*60)
    
    # Run tests
    usb_ok = check_usb_connection()
    audio_ok = check_audio_devices()
    pyaudio_ok, device_index = test_pyaudio_detection()
    
    if usb_ok and audio_ok and pyaudio_ok:
        capture_ok = test_audio_capture(device_index)
        robot_ok = test_with_robot_code()
    else:
        print("\n⚠️  Skipping audio tests due to detection failures")
        capture_ok = False
        robot_ok = False
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"  USB Connection:      {'✅ PASS' if usb_ok else '❌ FAIL'}")
    print(f"  Audio Devices:       {'✅ PASS' if audio_ok else '❌ FAIL'}")
    print(f"  PyAudio Detection:   {'✅ PASS' if pyaudio_ok else '❌ FAIL'}")
    print(f"  Audio Capture:       {'✅ PASS' if capture_ok else '❌ FAIL'}")
    print(f"  Robot Code:          {'✅ PASS' if robot_ok else '❌ FAIL'}")
    
    print_recommendations()
    
    # Exit code
    if all([usb_ok, audio_ok, pyaudio_ok, capture_ok, robot_ok]):
        print("\n🎉 All tests passed! ReSpeaker is ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the recommendations above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

