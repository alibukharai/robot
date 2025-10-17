# 🏗️ Architecture Overview

This document describes the architecture of the Digital Waiter Robot system.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Digital Waiter Robot                     │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┴─────────────────┐
            │                                   │
            ▼                                   ▼
    ┌───────────────┐                  ┌──────────────┐
    │  Hardware     │                  │   Software   │
    │  Layer        │                  │   Layer      │
    └───────────────┘                  └──────────────┘
```

---

## Hardware Layer

```
┌─────────────────────────────────────────────────────────────┐
│                      Raspberry Pi 5 (8GB)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input:                           Output:                    │
│  ┌──────────────────────┐        ┌──────────────────────┐  │
│  │ ReSpeaker Mic Array  │        │   Speaker            │  │
│  │ - 6 microphones      │        │   (3.5mm / USB)      │  │
│  │ - 16kHz sample rate  │        │                      │  │
│  │ - Voice detection    │        │                      │  │
│  └──────────────────────┘        └──────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Software Architecture

### Layer Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    Application Layer                          │
│                      (src/main.py)                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  • Orchestration                                       │  │
│  │  • State management                                    │  │
│  │  • Event loop                                          │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                              │
      ┌───────────────────────┼───────────────────────┐
      │                       │                       │
      ▼                       ▼                       ▼
┌──────────┐          ┌──────────┐          ┌──────────┐
│  Audio   │          │ Speech   │          │ Business │
│  Layer   │          │ Layer    │          │ Logic    │
└──────────┘          └──────────┘          └──────────┘
```

### Module Breakdown

#### 1. Audio Layer (`src/audio/`)

**Purpose**: Handle audio I/O with ReSpeaker

```python
┌─────────────────────────────────────────────┐
│              Audio Layer                     │
├─────────────────────────────────────────────┤
│                                              │
│  microphone.py                               │
│  ┌──────────────────────────────────────┐   │
│  │ • Stream management                  │   │
│  │ • Voice Activity Detection (VAD)     │   │
│  │ • Recording with silence detection   │   │
│  │ • Device auto-detection              │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  speaker.py                                  │
│  ┌──────────────────────────────────────┐   │
│  │ • Audio playback                     │   │
│  │ • Volume control                     │   │
│  └──────────────────────────────────────┘   │
│                                              │
└─────────────────────────────────────────────┘
```

#### 2. Wake Word Layer (`src/wake_word/`)

**Purpose**: Detect activation phrase

```python
┌─────────────────────────────────────────────┐
│           Wake Word Layer                    │
├─────────────────────────────────────────────┤
│                                              │
│  detector.py                                 │
│  ┌──────────────────────────────────────┐   │
│  │ Library: OpenWakeWord                │   │
│  │ License: Apache 2.0                  │   │
│  │                                      │   │
│  │ Features:                            │   │
│  │ • Offline detection                  │   │
│  │ • Multiple wake words                │   │
│  │ • Adjustable threshold               │   │
│  │ • Low latency (<100ms)               │   │
│  └──────────────────────────────────────┘   │
│                                              │
└─────────────────────────────────────────────┘
```

#### 3. Speech Layer (`src/speech/`)

**Purpose**: Speech recognition and synthesis

```python
┌─────────────────────────────────────────────┐
│            Speech Layer                      │
├─────────────────────────────────────────────┤
│                                              │
│  recognizer.py (ASR)                         │
│  ┌──────────────────────────────────────┐   │
│  │ Library: Vosk                        │   │
│  │ License: Apache 2.0                  │   │
│  │                                      │   │
│  │ Features:                            │   │
│  │ • Offline recognition                │   │
│  │ • Multiple languages                 │   │
│  │ • Real-time streaming                │   │
│  │ • High accuracy                      │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  synthesizer.py (TTS)                        │
│  ┌──────────────────────────────────────┐   │
│  │ Library: pyttsx3 + eSpeak            │   │
│  │ License: MPL 2.0 / GPL v3            │   │
│  │                                      │   │
│  │ Features:                            │   │
│  │ • Offline synthesis                  │   │
│  │ • Adjustable rate/volume             │   │
│  │ • Multiple voices                    │   │
│  └──────────────────────────────────────┘   │
│                                              │
└─────────────────────────────────────────────┘
```

#### 4. Business Logic Layer

```python
┌─────────────────────────────────────────────┐
│         Business Logic Layer                 │
├─────────────────────────────────────────────┤
│                                              │
│  intent/ - Intent Recognition                │
│  ┌──────────────────────────────────────┐   │
│  │ • Rule-based NLU                     │   │
│  │ • Pattern matching                   │   │
│  │ • Entity extraction                  │   │
│  │ • Intent types:                      │   │
│  │   - ORDER                            │   │
│  │   - SUGGEST                          │   │
│  │   - CONFIRM                          │   │
│  │   - CANCEL                           │   │
│  │   - INFO                             │   │
│  │   - DONE                             │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  menu/ - Menu Management                     │
│  ┌──────────────────────────────────────┐   │
│  │ • YAML-based menu                    │   │
│  │ • Search by name                     │   │
│  │ • Filter by category                 │   │
│  │ • Popular item suggestions           │   │
│  │ • Fuzzy matching                     │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  order/ - Order Management                   │
│  ┌──────────────────────────────────────┐   │
│  │ • Order tracking                     │   │
│  │ • Item add/remove                    │   │
│  │ • Price calculation                  │   │
│  │ • Order persistence (JSON/YAML)      │   │
│  │ • Order history                      │   │
│  └──────────────────────────────────────┘   │
│                                              │
└─────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Listening Mode (Wake Word Detection)

```
Microphone → Audio Stream → OpenWakeWord → Detection
                                   │
                                   │ (Wake word detected)
                                   ▼
                              Switch to Order Mode
```

### 2. Order Mode (Full Pipeline)

```
1. CAPTURE
   Microphone → Audio Recording
                     │
                     ▼
2. RECOGNIZE
   Vosk ASR → Text Transcription
                     │
                     ▼
3. UNDERSTAND
   Intent Processor → Intent + Entities
                           │
                           ▼
4. LOOKUP
   Menu Manager → Find Items
                       │
                       ▼
5. TRACK
   Order Manager → Add to Order
                       │
                       ▼
6. RESPOND
   TTS → Speech Output → Speaker
```

---

## State Machine

```
┌─────────────┐
│   STARTUP   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  LISTENING  │◄──────┐
│ (Wake Word) │       │
└──────┬──────┘       │
       │              │
       │ Wake word    │
       │ detected     │
       ▼              │
┌─────────────┐       │
│  RECORDING  │       │
│   (Audio)   │       │
└──────┬──────┘       │
       │              │
       ▼              │
┌─────────────┐       │
│ RECOGNIZING │       │
│  (Vosk ASR) │       │
└──────┬──────┘       │
       │              │
       ▼              │
┌─────────────┐       │
│ PROCESSING  │       │
│  (Intent)   │       │
└──────┬──────┘       │
       │              │
       ▼              │
┌─────────────┐       │
│ RESPONDING  │       │
│    (TTS)    │       │
└──────┬──────┘       │
       │              │
       └──────────────┘
```

---

## Configuration Management

```
config/
├── settings.yaml
│   ├── Audio settings
│   ├── Wake word config
│   ├── ASR config
│   ├── TTS config
│   ├── Menu config
│   └── Order config
│
└── menu.yaml
    ├── Restaurant info
    └── Categories
        └── Items
            ├── Name
            ├── Description
            ├── Price
            ├── Popular flag
            └── Dietary tags
```

---

## Performance Characteristics

### Latency

| Component | Latency | Notes |
|-----------|---------|-------|
| Wake Word Detection | <100ms | Real-time processing |
| Audio Recording | 1-3s | Based on speech length |
| Speech Recognition | 1-2s | Depends on utterance length |
| Intent Processing | <10ms | Rule-based, very fast |
| Menu Lookup | <5ms | In-memory search |
| TTS Generation | 1-2s | eSpeak synthesis |

**Total round-trip**: ~3-5 seconds from user speech to robot response

### Resource Usage

| Resource | Usage | Peak |
|----------|-------|------|
| RAM | 500-800 MB | 1 GB |
| CPU | 20-40% | 60% |
| Storage | 500 MB | 1 GB |
| Network | 0 (offline) | 0 |

---

## Extensibility

### Adding New Intents

1. Add patterns to `src/intent/processor.py`:
```python
Intent.NEW_INTENT: [
    r'\bpattern1\b',
    r'\bpattern2\b',
]
```

2. Add handler in `src/main.py`:
```python
def _handle_new_intent(self, entities):
    # Handle the new intent
    pass
```

### Adding New Wake Words

Change in `config/settings.yaml`:
```yaml
wake_word:
  model: "your_wake_word"
```

Available models: `hey_jarvis`, `alexa`, `hey_mycroft`

### Multi-Language Support

1. Download language-specific Vosk model
2. Update `config/settings.yaml`:
```yaml
asr:
  model_path: "models/vosk-model-small-es-0.42"  # Spanish
```

### Custom Menu Items

Edit `config/menu.yaml`:
```yaml
categories:
  - name: "New Category"
    items:
      - name: "New Item"
        price: 9.99
```

---

## Security & Privacy

✅ **100% Offline Operation**
- No data sent to cloud
- No internet required
- All processing on-device

✅ **Data Privacy**
- Audio not stored (unless debugging)
- Orders saved locally only
- No user tracking

✅ **Open Source**
- Full source code available
- Auditable components
- No proprietary dependencies

---

## License Compliance

All components use permissive licenses suitable for commercial use:

| Component | License | Commercial OK |
|-----------|---------|---------------|
| OpenWakeWord | Apache 2.0 | ✅ Yes |
| Vosk | Apache 2.0 | ✅ Yes |
| pyttsx3 | MPL 2.0 | ✅ Yes |
| eSpeak | GPL v3 | ✅ Yes* |
| PyAudio | MIT | ✅ Yes |
| PyYAML | MIT | ✅ Yes |
| NumPy | BSD 3-Clause | ✅ Yes |

*GPL only affects eSpeak binary, not your application code

---

## Future Enhancements

### Planned Features
- [ ] Advanced VAD for better noise handling
- [ ] Multi-language support
- [ ] Visual feedback (LCD display)
- [ ] Mobile app integration
- [ ] Payment processing
- [ ] Kitchen display system integration
- [ ] Analytics dashboard
- [ ] Voice customization
- [ ] Dietary preference learning

### Possible Integrations
- [ ] POS systems
- [ ] Restaurant management software
- [ ] Inventory systems
- [ ] Customer loyalty programs
- [ ] Delivery services

---

## Testing Strategy

```
Unit Tests
    │
    ├── Audio layer tests
    ├── Wake word tests
    ├── Speech recognition tests
    ├── Intent recognition tests
    ├── Menu manager tests
    └── Order manager tests

Integration Tests
    │
    ├── End-to-end order flow
    ├── Wake word → Order → Save
    └── Error handling

Hardware Tests
    │
    ├── Microphone functionality
    ├── Speaker output
    └── ReSpeaker driver
```

Run tests: `python3 test_setup.py`

---

## Maintenance

### Regular Tasks
- Check logs: `tail -f logs/robot.log`
- Clear old orders: `rm data/orders/*.json`
- Update models: Download new Vosk models
- System updates: `sudo apt-get update && sudo apt-get upgrade`

### Monitoring
- CPU/RAM usage: `htop`
- Audio levels: `alsamixer`
- Disk space: `df -h`
- System logs: `journalctl -xe`

---

## Debugging

Enable debug logging in `config/settings.yaml`:
```yaml
logging:
  level: "DEBUG"
```

Check component status:
```bash
# Audio devices
aplay -l
arecord -l

# ReSpeaker status
dmesg | grep seeed

# Python packages
pip list

# Test individual components
python3 test_setup.py
```

---

For more information, see [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md).

