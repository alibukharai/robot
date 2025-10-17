# 🤖 Digital Waiter Robot

A voice-activated service robot for restaurants using **Raspberry Pi 5** and **ReSpeaker Mic Array v2.0**.

This system is built entirely with **offline**, **open-source**, and **commercially-friendly** libraries — no cloud services, no license fees, no subscriptions.

---

## 📋 Features

- ✅ **Wake Word Detection** - Activate with "Hey Jarvis" (offline, Apache 2.0)
- ✅ **Speech Recognition** - Understand customer orders (offline, Apache 2.0)
- ✅ **Intent Recognition** - Parse order intents and extract menu items
- ✅ **Menu Management** - Flexible YAML-based menu system
- ✅ **Order Tracking** - Track and save customer orders
- ✅ **Text-to-Speech** - Natural voice responses (offline)
- ✅ **Commercial-Use Ready** - All libraries are free for commercial deployment

---

## 🧰 Hardware Requirements

- **Raspberry Pi 5** (8GB recommended)
- **ReSpeaker Mic Array v2.0** (4-mic USB array with XVF-3000 chipset)
  - USB Audio Class 1.0 (UAC 1.0) - works as USB sound card
  - 6-channel firmware with processed audio for ASR
  - On-chip speech algorithms (VAD, beamforming, noise suppression, AEC)
- **MicroSD card** (32GB+ recommended)
- **Speaker** (connected via 3.5mm jack to ReSpeaker or Pi USB)
- **Power supply** for Raspberry Pi 5

**Note:** The ReSpeaker connects via **USB** and works without special drivers. See [docs/RESPEAKER_SETUP.md](docs/RESPEAKER_SETUP.md) for details.

---

## 📦 Software Stack

All components use permissive open-source licenses suitable for commercial use:

| Component | Library | License | Purpose |
|-----------|---------|---------|---------|
| Wake Word | OpenWakeWord | Apache 2.0 | Offline wake word detection |
| ASR | Vosk | Apache 2.0 | Offline speech recognition |
| TTS | pyttsx3 + eSpeak | MPL 2.0 / GPL v3 | Text-to-speech synthesis |
| Audio I/O | PyAudio | MIT | Microphone and speaker interface |
| Intent | Custom | N/A | Rule-based NLU |

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
cd ~/workspace
git clone <your-repo-url> robot
cd robot
```

### 2. Run Setup Script

The setup script will:
- Install system dependencies
- Set up ReSpeaker drivers
- Create Python virtual environment
- Install Python packages
- Download speech recognition models
- Configure audio devices

```bash
chmod +x setup.sh
./setup.sh
```

**Note:** You may need to reboot after installing ReSpeaker drivers:
```bash
sudo reboot
```

### 3. Verify Installation

After reboot, check that the ReSpeaker is detected:

```bash
arecord -l
```

You should see output containing `seeed-2mic-voicecard` or similar.

### 4. Run the Robot

```bash
source venv/bin/activate
python3 src/main.py
```

---

## 🎯 How to Use

1. **Start the robot** - Run `python3 src/main.py`

2. **Wait for greeting** - The robot will say "Welcome! Say 'Hey Jarvis' to start ordering."

3. **Say wake word** - Say "Hey Jarvis" to activate listening mode

4. **Place your order** - Say what you want, e.g.:
   - "I want a beef burger and a coffee"
   - "Give me two spring rolls"
   - "I'll have the grilled salmon"

5. **Get suggestions** - Ask:
   - "What do you suggest?"
   - "What's popular?"

6. **Finish ordering** - Say:
   - "That's all"
   - "I'm done"

7. **Order is saved** - Your order is automatically saved to `data/orders/`

---

## ⚙️ Configuration

### Main Settings: `config/settings.yaml`

Key configuration options:

```yaml
audio:
  sample_rate: 16000  # Audio sample rate
  device_name: "seeed-2mic-voicecard"  # ReSpeaker device

wake_word:
  model: "hey_jarvis"  # Wake word model
  threshold: 0.5  # Detection sensitivity (0-1)

asr:
  model_path: "models/vosk-model-small-en-us-0.15"

tts:
  rate: 150  # Speaking speed (words per minute)
  volume: 0.9  # Volume (0-1)
```

### Menu: `config/menu.yaml`

Customize your restaurant menu:

```yaml
categories:
  - name: "Main Courses"
    items:
      - name: "Beef Burger"
        description: "Angus beef burger with cheese"
        price: 12.99
        popular: true
```

Add/remove items, adjust prices, mark popular items, etc.

---

## 📁 Project Structure

```
robot/
├── config/               # Configuration files
│   ├── settings.yaml    # Robot settings
│   └── menu.yaml        # Restaurant menu
├── src/                 # Source code
│   ├── main.py         # Main application
│   ├── audio/          # Audio I/O handling
│   ├── wake_word/      # Wake word detection
│   ├── speech/         # ASR and TTS
│   ├── intent/         # Intent recognition
│   ├── menu/           # Menu management
│   └── order/          # Order tracking
├── models/              # AI models
├── data/                # Runtime data
│   └── orders/         # Saved orders
├── logs/               # Application logs
├── requirements.txt    # Python dependencies
├── setup.sh           # Setup script
└── README.md          # This file
```

---

## 🔧 Troubleshooting

### ReSpeaker Not Detected

The ReSpeaker v2.0 is a **USB device** and should work without special drivers.

1. **Check USB connection:**
   ```bash
   lsusb | grep "2886:0018"
   # Should show: Seeed Technology Co., Ltd
   ```

2. **Check audio devices:**
   ```bash
   arecord -l
   # Look for "ReSpeaker" or "USB Audio"
   ```

3. **Try different USB port** (use USB 3.0 blue ports on Pi 5)

4. **Check device detection:**
   ```bash
   dmesg | grep -i "usb\|audio"
   ```

5. **If still not working**, see detailed guide: [docs/RESPEAKER_SETUP.md](docs/RESPEAKER_SETUP.md)

### Low Microphone Volume

Adjust volume with ALSA mixer:
```bash
alsamixer
```
- Press F6 to select sound card (choose ReSpeaker)
- Adjust capture volume with arrow keys
- Press ESC to exit

### Wake Word Not Detecting

1. Increase microphone gain (see above)
2. Lower wake word threshold in `config/settings.yaml`:
   ```yaml
   wake_word:
     threshold: 0.3  # Lower = more sensitive
   ```
3. Check microphone test:
   ```bash
   arecord -D plughw:2,0 -f S16_LE -r 16000 -d 5 test.wav
   aplay test.wav
   ```

### Speech Recognition Not Working

1. Verify Vosk model exists:
   ```bash
   ls models/vosk-model-small-en-us-0.15/
   ```
2. Test recording and recognition separately
3. Speak clearly and close to microphone
4. Check `logs/robot.log` for errors

### TTS Not Speaking

1. Test speaker:
   ```bash
   espeak "Hello World"
   ```
2. Adjust volume in `config/settings.yaml`
3. Check audio output device:
   ```bash
   aplay -l
   ```

---

## 🧪 Testing Individual Components

### Test Microphone

```bash
source venv/bin/activate
python3 << EOF
from src.audio.microphone import Microphone
# Auto-detect ReSpeaker
mic = Microphone()
mic.list_devices()
EOF
```

Or test USB audio directly:
```bash
# Find ReSpeaker card number
arecord -l

# Record 5-second test (replace hw:2,0 with your card number)
arecord -D hw:2,0 -f S16_LE -r 16000 -c 1 -d 5 test.wav
aplay test.wav
```

### Test Wake Word

```bash
python3 << EOF
from src.wake_word.detector import WakeWordDetector
detector = WakeWordDetector(model_name="hey_jarvis")
print("Wake word detector ready")
EOF
```

### Test Speech Recognition

```bash
python3 << EOF
from src.speech.recognizer import SpeechRecognizer
recognizer = SpeechRecognizer(model_path="models/vosk-model-small-en-us-0.15")
print("Speech recognizer ready")
EOF
```

### Test TTS

```bash
python3 << EOF
from src.speech.synthesizer import SpeechSynthesizer
tts = SpeechSynthesizer()
tts.speak("Hello, I am your digital waiter!")
EOF
```

---

## 📊 Performance Notes

### Raspberry Pi 5 Performance

- **Wake Word Detection**: Real-time, < 100ms latency
- **Speech Recognition**: 1-2 seconds for typical sentence
- **Intent Processing**: Instant (< 10ms)
- **TTS Generation**: 1-2 seconds for typical response

### Resource Usage

- **RAM**: ~500-800 MB (with all models loaded)
- **CPU**: 20-40% during active processing
- **Storage**: ~500 MB (models + dependencies)

### Optimization Tips

1. **Use smaller Vosk model** for faster ASR (already using "small" model)
2. **Adjust chunk size** in audio config for lower latency
3. **Disable wake word** if using push-to-talk button
4. **Pre-load models** at startup (already done)

---

## 🔐 License Information

This project uses only commercially-friendly open-source libraries:

- **OpenWakeWord**: Apache 2.0 ✅
- **Vosk**: Apache 2.0 ✅
- **pyttsx3**: MPL 2.0 ✅
- **PyAudio**: MIT ✅
- **PyYAML**: MIT ✅
- **NumPy**: BSD 3-Clause ✅

**All components are free for commercial use without restrictions.**

---

## 🛠️ Development

### Adding New Menu Items

Edit `config/menu.yaml`:

```yaml
- name: "New Item"
  description: "Item description"
  price: 9.99
  popular: false
  dietary: ["vegetarian"]
```

### Customizing Wake Word

OpenWakeWord supports multiple models. Change in `config/settings.yaml`:

```yaml
wake_word:
  model: "alexa"  # Options: hey_jarvis, alexa, hey_mycroft
```

### Extending Intent Recognition

Edit `src/intent/processor.py` to add new intent patterns.

### Logging

Logs are saved to `logs/robot.log`. Adjust log level in `config/settings.yaml`:

```yaml
logging:
  level: "DEBUG"  # DEBUG, INFO, WARNING, ERROR
```

---

## 📝 Example Interactions

### Basic Order

```
Customer: "Hey Jarvis"
Robot: "Yes, I'm listening! What would you like to order?"
Customer: "I want a beef burger and a coffee"
Robot: "Added 1 Beef Burger to your order. That's $12.99. Added 1 Coffee to your order. That's $2.99. Anything else?"
Customer: "That's all"
Robot: "Your order: 1 Beef Burger, 1 Coffee. Total: $15.98. Shall I confirm your order?"
```

### Getting Suggestions

```
Customer: "Hey Jarvis"
Robot: "Yes, I'm listening! What would you like to order?"
Customer: "What do you suggest?"
Robot: "Our popular items are: Grilled Chicken for $14.99, Beef Burger for $12.99, Margherita Pizza for $13.49."
Customer: "I'll have the grilled chicken"
Robot: "Added 1 Grilled Chicken to your order. That's $14.99. Anything else?"
```

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Better intent recognition (ML-based)
- [ ] Multi-language support
- [ ] Visual display interface
- [ ] Integration with POS systems
- [ ] Voice activity detection (VAD) improvements
- [ ] More wake word options

---

## 📞 Support

For issues and questions:

1. Check `logs/robot.log` for error messages
2. Review the Troubleshooting section above
3. Test individual components (see Testing section)
4. Check ReSpeaker documentation: https://wiki.seeedstudio.com/ReSpeaker_Mic_Array_v2.0/

---

## 🎓 Technical Details

### Audio Pipeline

```
Microphone (16kHz mono)
    ↓
Wake Word Detector (OpenWakeWord)
    ↓ (trigger)
Speech Recognizer (Vosk)
    ↓
Intent Processor (rule-based)
    ↓
Menu Manager → Order Manager
    ↓
TTS Synthesizer (pyttsx3)
    ↓
Speaker
```

### Data Flow

1. **Audio Capture**: ReSpeaker → PyAudio → 16kHz PCM
2. **Wake Word**: 1280-byte chunks → OpenWakeWord → Detection
3. **ASR**: Variable-length audio → Vosk → Text
4. **Intent**: Text → Regex patterns → Intent + Entities
5. **Menu Lookup**: Entity names → Fuzzy match → Menu items
6. **Order**: Menu items → Order manager → JSON/YAML file
7. **Response**: Text → pyttsx3 → eSpeak → Audio output

---

## ✨ Future Enhancements

- 🔊 Better noise cancellation
- 🌐 Multi-language support (Vosk supports 20+ languages)
- 📱 Mobile app integration
- 🖥️ Web dashboard for order management
- 🤖 Integration with robot chassis/movement
- 📊 Analytics and reporting
- 💳 Payment processing integration

---

## 📄 License

This project is released under the MIT License. See LICENSE file for details.

All dependencies maintain their respective open-source licenses as listed above.

---

**Built with ❤️ for the future of restaurant automation**

