# Changes Made for ReSpeaker Mic Array v2.0

This document summarizes the adjustments made to the codebase based on the official [ReSpeaker Mic Array v2.0 documentation](https://wiki.seeedstudio.com/ReSpeaker_Mic_Array_v2.0/).

---

## Summary of Key Findings

After reviewing the official documentation, several important specifications were confirmed:

### Hardware Specifications (from official docs)
- **4 digital MEMS microphones** (not 6 or 7)
- **XVF-3000 chipset** from XMOS (not XVSM-2000)
- **USB Audio Class 1.0 (UAC 1.0)** - works as USB sound card
- **Max sample rate: 16kHz** (not higher)
- **6-channel firmware** (factory default):
  - Channel 0: Processed audio for ASR ✅ (what we use)
  - Channels 1-4: Raw microphone data
  - Channel 5: Merged playback

### Connection Method
- **Primary mode: USB** (plug-and-play, no drivers needed)
- Optional mode: HAT via GPIO (requires seeed-voicecard driver)
- **Our implementation uses USB mode** for simplicity and cross-platform compatibility

---

## Code Changes Made

### 1. **Updated `src/audio/microphone.py`**

#### Changes:
```python
# Added comprehensive documentation about ReSpeaker v2.0 specs
"""
ReSpeaker Mic Array v2.0 specifications:
- 4 digital MEMS microphones
- XVF-3000 chipset with on-board speech algorithms
- USB Audio Class 1.0 (UAC 1.0) - works as USB sound card
- 6-channel firmware (default):
  * Channel 0: Processed audio for ASR (recommended)
  * Channels 1-4: Raw microphone data
  * Channel 5: Merged playback
- Max sample rate: 16kHz
"""
```

#### Improved USB Device Detection:
```python
def _find_device_index(self) -> Optional[int]:
    """
    Find the device index for ReSpeaker USB device.
    
    The ReSpeaker Mic Array v2.0 appears as a USB audio device.
    We search for common identifiers: "ReSpeaker", "XMOS", "USB PnP".
    """
    # Auto-detect ReSpeaker if no specific name given
    if self.device_name is None:
        respeaker_keywords = ["respeaker", "xmos", "usb pnp audio"]
        
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            device_name = info.get('name', '').lower()
            
            # Check if input device
            if info.get('maxInputChannels', 0) == 0:
                continue
            
            # Look for ReSpeaker identifiers
            for keyword in respeaker_keywords:
                if keyword in device_name:
                    logger.info(f"Auto-detected ReSpeaker: {info.get('name')}")
                    return i
```

**Why:** The ReSpeaker v2.0 appears with different names depending on the system:
- "ReSpeaker 4 Mic Array"
- "XMOS XVF3000"
- "USB PnP Audio Device"

Auto-detection handles all these cases.

---

### 2. **Updated `config/settings.yaml`**

#### Before:
```yaml
audio:
  sample_rate: 16000
  channels: 1
  chunk_size: 1024
  device_name: "seeed-2mic-voicecard"  # Incorrect for USB mode
```

#### After:
```yaml
audio:
  # ReSpeaker Mic Array v2.0 settings
  # The ReSpeaker v2.0 is a USB device with 6 channels (factory firmware)
  # Channel 0: Processed audio for ASR (recommended)
  # Max sample rate: 16kHz
  sample_rate: 16000
  channels: 1  # Use 1 channel (channel 0 - processed audio for ASR)
  chunk_size: 1024
  device_name: null  # null = auto-detect ReSpeaker, or specify keyword
```

**Why:** 
- `device_name: null` enables auto-detection of USB device
- Documentation clarifies the 6-channel firmware structure
- Confirms 16kHz max sample rate

---

### 3. **Updated `setup.sh`**

#### Major Changes:

**USB Detection:**
```bash
# Check for ReSpeaker via USB VID:PID
if lsusb | grep -q "2886:0018"; then
    echo "ReSpeaker Mic Array v2.0 detected via USB"
fi
```

**Optional Driver Installation:**
```bash
# Made seeed-voicecard driver optional
echo "The ReSpeaker works as a USB device without special drivers."
echo "However, you can optionally install the seeed-voicecard driver."
read -p "Install seeed-voicecard driver? (y/N) "
```

**Why:**
- According to documentation, USB Audio Class 1.0 works without drivers
- seeed-voicecard driver only needed for HAT mode (GPIO connection)
- Simplified setup for most users

---

### 4. **Created `docs/RESPEAKER_SETUP.md`**

**New comprehensive guide covering:**
- Hardware specifications (from official docs)
- Firmware versions (1-channel vs 6-channel)
- Connection modes (USB vs HAT)
- Setup instructions
- Audio level adjustment
- LED control
- Advanced features (DOA, VAD)
- Troubleshooting
- FAQ

**References:** Direct links to official Seeed Studio documentation.

---

### 5. **Created `test_respeaker.py`**

**New diagnostic tool that tests:**
1. USB connection (`lsusb`)
2. Audio device detection (`arecord -l`)
3. PyAudio detection
4. Actual audio capture with level analysis
5. Robot microphone class integration

**Usage:**
```bash
python3 test_respeaker.py
```

**Why:** Helps users quickly diagnose ReSpeaker connection and audio issues.

---

### 6. **Updated Documentation**

#### `README.md`:
- Hardware requirements now specify 4-mic USB array
- Updated XVF-3000 chipset information
- Clarified USB connection mode
- Updated troubleshooting for USB devices
- Added reference to detailed ReSpeaker guide

#### `QUICKSTART.md`:
- Updated device detection commands
- Corrected alsamixer instructions for USB device
- Added USB verification steps

#### `ARCHITECTURE.md`:
- Updated hardware layer diagram
- Clarified USB Audio Class 1.0 support
- Updated audio pipeline documentation

---

## Technical Specifications Confirmed

| Specification | Value | Source |
|--------------|-------|--------|
| Microphones | 4 | Official docs |
| Chipset | XVF-3000 (XMOS) | Official docs |
| Channels | 6 (factory firmware) | Official docs |
| Channel for ASR | Channel 0 (processed) | Official docs |
| Max Sample Rate | 16kHz | Official docs |
| USB Standard | UAC 1.0 | Official docs |
| USB VID:PID | 2886:0018 | Official docs |
| LEDs | 12 programmable RGB | Official docs |

---

## What Was NOT Changed

### These remained correct:
1. ✅ **Sample rate: 16kHz** - Already correct, matches max spec
2. ✅ **Mono audio (1 channel)** - Correct for using channel 0
3. ✅ **Vosk ASR integration** - Works well with 16kHz audio
4. ✅ **OpenWakeWord** - Compatible with processed audio from channel 0
5. ✅ **Overall architecture** - No changes needed

---

## Benefits of USB Mode

Based on official documentation:

### Advantages:
1. **Plug-and-play** - No kernel driver installation
2. **Cross-platform** - Works on Linux, Windows, macOS
3. **No GPIO conflicts** - USB doesn't use GPIO pins
4. **Easier setup** - No need to reboot for driver loading
5. **Stable** - Standard USB Audio Class implementation

### On-chip Processing:
The XVF-3000 chipset provides these algorithms in hardware:
- ✅ Voice Activity Detection (VAD)
- ✅ Direction of Arrival (DOA)
- ✅ Beamforming
- ✅ Noise Suppression
- ✅ De-reverberation
- ✅ Acoustic Echo Cancellation (AEC)

**Channel 0 provides pre-processed audio** with these algorithms applied, resulting in better ASR performance.

---

## Testing Recommendations

### 1. Verify USB Connection
```bash
lsusb | grep "2886:0018"
```

### 2. Check Audio Devices
```bash
arecord -l | grep -i "respeaker\|xmos\|usb"
```

### 3. Run Diagnostic Tool
```bash
python3 test_respeaker.py
```

### 4. Test Audio Capture
```bash
arecord -D hw:2,0 -f S16_LE -r 16000 -c 1 -d 3 test.wav
aplay test.wav
```

### 5. Run Full Setup Test
```bash
source venv/bin/activate
python3 test_setup.py
```

---

## References

All changes are based on the official documentation:

- **Primary Source:** [ReSpeaker Mic Array v2.0 Wiki](https://wiki.seeedstudio.com/ReSpeaker_Mic_Array_v2.0/)
- **GitHub Repo:** https://github.com/respeaker/usb_4_mic_array
- **Datasheet:** XVF-3000 Product Brief

---

## Conclusion

The codebase has been updated to properly support the **ReSpeaker Mic Array v2.0** as a **USB Audio Class 1.0 device**, leveraging its:

✅ 4-microphone array  
✅ XVF-3000 chipset with on-board speech processing  
✅ 6-channel firmware (using channel 0 for ASR)  
✅ 16kHz maximum sample rate  
✅ Plug-and-play USB connectivity  

The changes ensure optimal performance by using the pre-processed audio from channel 0, which includes beamforming, noise suppression, and acoustic echo cancellation provided by the XVF-3000 chipset.

**All functionality remains backward compatible** while adding better auto-detection and more flexible device configuration.

