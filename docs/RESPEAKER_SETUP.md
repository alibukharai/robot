# ReSpeaker Mic Array v2.0 - Detailed Setup Guide

This guide provides detailed information about the ReSpeaker Mic Array v2.0 specifically for this project.

## Hardware Overview

According to the [official documentation](https://wiki.seeedstudio.com/ReSpeaker_Mic_Array_v2.0/), the ReSpeaker Mic Array v2.0 has:

- **4 digital MEMS microphones** (ST MP34DT01TR-M)
- **XVF-3000 chipset** from XMOS
- **USB Audio Class 1.0 (UAC 1.0)** - works as USB sound card
- **12 programmable RGB LEDs**
- **3.5mm audio jack** for output
- **Max sample rate: 16kHz**

### Chipset Features (XVF-3000)

The on-chip DSP algorithms include:
- **VAD** (Voice Activity Detection)
- **DOA** (Direction of Arrival)
- **Beamforming**
- **Noise Suppression**
- **De-reverberation**
- **Acoustic Echo Cancellation (AEC)**

---

## Firmware Versions

The ReSpeaker has **two firmware versions**:

### 1. **1-Channel Firmware**
- **1 channel**: Processed audio for ASR
- Best for simple speech recognition applications
- Lower bandwidth usage

### 2. **6-Channel Firmware** (Factory Default) ⭐
- **Channel 0**: Processed audio for ASR (recommended for our robot)
- **Channels 1-4**: Raw microphone data
- **Channel 5**: Merged playback
- Best for advanced applications that need raw mic data

**Our robot uses Channel 0 from the 6-channel firmware**, which provides:
- Pre-processed audio optimized for ASR
- On-chip noise suppression and beamforming
- Better performance in noisy environments

---

## Connection Modes

The ReSpeaker Mic Array v2.0 can work in two modes:

### Mode 1: USB Mode (Recommended) ✅

**How it works:**
- Simply plug into Raspberry Pi USB port
- Appears as USB audio device (UAC 1.0)
- **No special drivers required**
- Works on Linux, Windows, macOS out of the box

**Advantages:**
- Easy setup
- Cross-platform
- No kernel modules needed
- Plug-and-play

**Device identification:**
- USB VID:PID: `2886:0018`
- Device name variations:
  - "ReSpeaker 4 Mic Array"
  - "XMOS XVF3000"
  - "USB PnP Audio Device"

### Mode 2: HAT Mode (Optional)

**How it works:**
- Connects to Raspberry Pi GPIO pins
- Requires `seeed-voicecard` kernel driver
- Appears as ALSA sound card

**Advantages:**
- Direct GPIO connection
- May provide lower latency
- Additional GPIO control features

**Our code supports both modes**, but USB mode is recommended for simplicity.

---

## Setup for This Project

### Step 1: Physical Connection

1. **USB Mode** (Recommended):
   ```bash
   # Simply plug ReSpeaker into Raspberry Pi USB 3.0 port
   # No additional wiring needed
   ```

2. **HAT Mode** (Alternative):
   - Mount ReSpeaker on GPIO pins
   - Ensure proper alignment with 40-pin header

### Step 2: Verify Connection

Check if the device is detected:

```bash
# Check USB devices
lsusb | grep "2886:0018"
# Should show: "Bus XXX Device XXX: ID 2886:0018 Seeed Technology Co., Ltd"

# Or check for XMOS
lsusb | grep -i xmos

# Check audio devices
aplay -l
arecord -l
```

### Step 3: Test Audio Capture

Record a 5-second test:

```bash
# Find the device card number
arecord -l
# Look for "ReSpeaker" or "USB Audio"

# Record test (replace hw:X,0 with your card number)
arecord -D hw:2,0 -f S16_LE -r 16000 -c 1 -d 5 test.wav

# Play back
aplay test.wav
```

### Step 4: Adjust Microphone Gain

```bash
alsamixer
```

1. Press **F6** → Select "ReSpeaker" or "USB Audio Device"
2. Press **F4** to show capture controls
3. Use **arrow keys** to adjust:
   - **Capture volume**: 80-90% recommended
   - Too high → distortion
   - Too low → poor recognition
4. Press **ESC** to exit

---

## Firmware Management

### Check Current Firmware

You can query the device to see which firmware is loaded:

```bash
# Using the provided Python tool
cd usb_4_mic_array
python tuning.py FIRMWAREVERSION
```

### Update Firmware (Optional)

If you need to switch firmware versions:

```bash
# Download the usb_4_mic_array tools
git clone https://github.com/respeaker/usb_4_mic_array.git
cd usb_4_mic_array

# Install dependencies
sudo pip install pyusb click

# Flash 6-channel firmware (default)
sudo python dfu.py --download 6_channels_firmware.bin

# Or flash 1-channel firmware
sudo python dfu.py --download 1_channel_firmware.bin
```

**For this project, the 6-channel firmware is recommended** (usually pre-installed).

---

## LED Control

The ReSpeaker has 12 RGB LEDs that can be controlled programmatically.

### Basic LED Commands

```bash
git clone https://github.com/respeaker/usb_4_mic_array.git
cd usb_4_mic_array

# Turn on all LEDs (color: red=255, green=0, blue=0)
python tuning.py SETLED 255 0 0

# Turn off all LEDs
python tuning.py SETLED 0 0 0

# Blue LEDs
python tuning.py SETLED 0 0 255
```

### Potential Enhancement

You could integrate LED feedback into the robot:
- **Blue** = Listening for wake word
- **Green** = Processing order
- **Red** = Error
- **Yellow** = Speaking

---

## Advanced Features

### Direction of Arrival (DOA)

The XVF-3000 can detect which direction sound is coming from:

```bash
cd usb_4_mic_array
python tuning.py DOAANGLE
# Returns: 0-359 degrees
```

### Voice Activity Detection (VAD)

Check if speech is currently detected:

```bash
python tuning.py VOICEACTIVITY
# Returns: 0 (no voice) or 1 (voice detected)
```

### Speech Detection

Higher-level speech detection:

```bash
python tuning.py SPEECHDETECTED
# Returns: 0 (no speech) or 1 (speech detected)
```

---

## Troubleshooting

### Device Not Detected

**Problem:** `lsusb` doesn't show ReSpeaker

**Solutions:**
1. Check USB cable connection
2. Try different USB port (use USB 3.0 blue ports)
3. Check power:
   ```bash
   dmesg | tail -20
   # Look for USB device enumeration
   ```
4. Try rebooting with device connected

### Low Audio Quality

**Problem:** Poor recognition, noisy audio

**Solutions:**
1. Adjust microphone gain (see above)
2. Reduce ambient noise
3. Speak closer to device (optimal: 0.5-2 meters)
4. Check that 6-channel firmware is loaded
5. Verify sample rate is 16kHz:
   ```bash
   arecord -D hw:2,0 --dump-hw-params
   ```

### Audio Cutting Out

**Problem:** Audio dropouts or buffer underruns

**Solutions:**
1. Increase `chunk_size` in `config/settings.yaml`:
   ```yaml
   audio:
     chunk_size: 2048  # Increase from 1024
   ```
2. Check USB power:
   ```bash
   # Monitor USB device
   watch -n 0.5 'lsusb | grep 2886'
   ```
3. Use powered USB hub if needed

### Permission Errors

**Problem:** "Permission denied" when accessing device

**Solution:**
```bash
# Add user to audio group
sudo usermod -a -G audio $USER

# Logout and login again, or:
newgrp audio
```

### Channel Selection

**Problem:** Need to use different channel

**Solution:** Modify `config/settings.yaml`:
```yaml
audio:
  channels: 6  # Read all 6 channels
```

Then in code, select specific channel from the multi-channel stream.

---

## Performance Optimization

### Best Practices

1. **Use 16kHz sample rate** (max for device)
2. **Use channel 0** for ASR (pre-processed audio)
3. **Position device centrally** for best coverage
4. **Keep away from speakers** to avoid feedback
5. **Adjust gain properly** (80-90% recommended)

### Latency Measurements

Based on testing with Raspberry Pi 5:

| Stage | Latency |
|-------|---------|
| USB audio capture | ~10-20ms |
| Wake word detection | <100ms |
| Speech recognition | 1-2s |
| Total (wake → result) | ~1.5-2.5s |

---

## Integration with Our Robot

### Auto-Detection

The `Microphone` class auto-detects ReSpeaker by searching for:
- "respeaker" in device name
- "xmos" in device name
- "usb pnp audio" in device name

### Manual Specification

To manually specify device:

```yaml
# config/settings.yaml
audio:
  device_name: "ReSpeaker"  # or "XMOS" or "USB Audio"
```

### Channel Configuration

Our robot uses:
- **1 channel** (mono)
- **Channel 0** (processed audio from 6-channel firmware)
- **16kHz sample rate**

This configuration provides:
- Pre-processed audio with noise suppression
- Beamformed audio (focused on voice direction)
- Acoustic echo cancellation
- Optimal performance for wake word + ASR

---

## Additional Resources

- **Official Wiki**: https://wiki.seeedstudio.com/ReSpeaker_Mic_Array_v2.0/
- **GitHub Repo**: https://github.com/respeaker/usb_4_mic_array
- **Firmware Tools**: https://github.com/respeaker/usb_4_mic_array/tree/master/firmware
- **Datasheet**: XVF-3000 Product Brief (see Resources)

---

## FAQ

**Q: Do I need to install seeed-voicecard driver?**  
A: No, for USB mode. The device works as a standard USB audio device. The driver is only needed for HAT mode (GPIO connection).

**Q: Can I use this on Windows/Mac?**  
A: Yes! USB Audio Class 1.0 is supported by all major operating systems. However, this robot code is designed for Linux/Raspberry Pi.

**Q: Which firmware should I use?**  
A: The **6-channel firmware** (factory default) is recommended. It provides processed audio on channel 0 while keeping raw data accessible.

**Q: Can I use multiple ReSpeaker devices?**  
A: Yes, but you'll need to specify device indices to differentiate them.

**Q: What's the maximum distance for voice capture?**  
A: Optimal: 0.5-2 meters. Maximum: up to 5 meters in quiet environments with the beamforming and noise suppression enabled.

---

For more questions, check the [main troubleshooting guide](../README.md#troubleshooting) or the [official Seeed Studio wiki](https://wiki.seeedstudio.com/ReSpeaker_Mic_Array_v2.0/).

