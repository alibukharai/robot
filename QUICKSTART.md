# 🚀 Quick Start Guide

Get your Digital Waiter Robot up and running in 5 steps!

---

## Step 1: Run Setup (10-15 minutes)

```bash
cd /home/amd/workspace/robot
chmod +x setup.sh
./setup.sh
```

The setup script will:
- ✅ Install system dependencies
- ✅ Configure ReSpeaker Mic Array
- ✅ Create Python virtual environment
- ✅ Install Python packages
- ✅ Download AI models (~200MB)
- ✅ Configure audio devices

---

## Step 2: Reboot (if needed)

If the setup script reports that ReSpeaker driver was installed, reboot:

```bash
sudo reboot
```

---

## Step 3: Test Setup

After reboot, verify everything works:

```bash
cd /home/amd/workspace/robot
source venv/bin/activate
python3 test_setup.py
```

This will test:
- Python packages
- Audio devices (microphone and speaker)
- AI models
- Configuration files
- Text-to-speech

---

## Step 4: Adjust Audio Levels

First, verify ReSpeaker is connected:

```bash
lsusb | grep "2886:0018"
# Should show: Seeed Technology Co., Ltd

arecord -l
# Look for "ReSpeaker" or "USB Audio Device"
```

Set microphone gain:

```bash
alsamixer
```

- Press **F6** → Select "ReSpeaker 4 Mic Array" or "USB Audio Device"
- Press **F4** → Show capture controls
- Use **arrow keys** to adjust capture volume (80-90% recommended)
- Press **ESC** to exit

Test microphone (replace hw:X,0 with your card number from `arecord -l`):

```bash
arecord -D hw:2,0 -f S16_LE -r 16000 -c 1 -d 3 test.wav
aplay test.wav
```

---

## Step 5: Run the Robot! 🎉

```bash
cd /home/amd/workspace/robot
source venv/bin/activate
python3 src/main.py
```

---

## Usage

1. **Wait for greeting**: "Welcome! Say 'Hey Jarvis' to start ordering."

2. **Say wake word**: "Hey Jarvis"

3. **Place order**: 
   - "I want a beef burger and coffee"
   - "Give me two spring rolls"
   - "I'll have the grilled chicken"

4. **Get suggestions**:
   - "What do you suggest?"
   - "What's popular?"

5. **Finish**: "That's all" or "I'm done"

---

## Troubleshooting

### Wake word not detected?
- Lower threshold in `config/settings.yaml`:
  ```yaml
  wake_word:
    threshold: 0.3  # Lower = more sensitive
  ```

### Can't hear robot speaking?
- Test: `espeak "Hello World"`
- Adjust volume in `config/settings.yaml`

### Speech recognition not working?
- Speak clearly and close to microphone
- Check logs: `tail -f logs/robot.log`

### ReSpeaker not detected?
```bash
aplay -l | grep seeed
```
If nothing shows, re-run driver installation:
```bash
cd /tmp/seeed-voicecard
sudo ./install.sh
sudo reboot
```

---

## Customization

### Change Menu
Edit `config/menu.yaml`:
```yaml
- name: "New Item"
  price: 12.99
  popular: true
```

### Change Wake Word
Edit `config/settings.yaml`:
```yaml
wake_word:
  model: "alexa"  # or "hey_mycroft"
```

### Adjust Speech Speed
Edit `config/settings.yaml`:
```yaml
tts:
  rate: 150  # Lower = slower, Higher = faster
```

---

## What's Next?

- 📖 Read full documentation: [README.md](README.md)
- ⚙️ Customize settings: `config/settings.yaml`
- 🍔 Edit menu: `config/menu.yaml`
- 📊 Check orders: `data/orders/`
- 📝 View logs: `logs/robot.log`

---

**Need help?** Check the [full README](README.md) or [troubleshooting section](README.md#-troubleshooting).

