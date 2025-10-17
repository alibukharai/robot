#!/bin/bash

###########################################
# Digital Waiter Robot - Setup Script
# For Raspberry Pi 5 with ReSpeaker Mic Array v2.0
###########################################

set -e  # Exit on error

echo "=========================================="
echo "Digital Waiter Robot - Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo -e "${YELLOW}Warning: Not running on Raspberry Pi${NC}"
else
    MODEL=$(cat /proc/device-tree/model)
    echo "Detected: $MODEL"
fi

echo ""
echo "Step 1: Installing system dependencies..."
echo "=========================================="

# Update package list
sudo apt-get update

# Install audio libraries
echo "Installing audio libraries..."
sudo apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    alsa-utils \
    libasound2-dev

# Install eSpeak for TTS
echo "Installing eSpeak TTS engine..."
sudo apt-get install -y espeak espeak-ng

# Install other system dependencies
echo "Installing other dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    git \
    wget

echo ""
echo "Step 2: Setting up ReSpeaker Mic Array v2.0..."
echo "=========================================="

# ReSpeaker Mic Array v2.0 uses USB Audio Class 1.0 (UAC 1.0)
# It works as a USB sound card without special drivers on most systems
echo "ReSpeaker Mic Array v2.0 uses USB Audio Class 1.0"
echo "Checking if device is connected..."

if lsusb | grep -q "2886:0018"; then
    echo -e "${GREEN}ReSpeaker Mic Array v2.0 detected via USB${NC}"
else
    echo -e "${YELLOW}Warning: ReSpeaker not detected. Please ensure it's connected via USB.${NC}"
    echo "Looking for XMOS device..."
    if lsusb | grep -qi "xmos"; then
        echo -e "${GREEN}XMOS-based device detected (likely ReSpeaker)${NC}"
    fi
fi

# Optional: Install seeed-voicecard driver for additional features
# Note: Basic USB audio functionality works without this driver
echo ""
echo "The ReSpeaker works as a USB device without special drivers."
echo "However, you can optionally install the seeed-voicecard driver for advanced features."
read -p "Install seeed-voicecard driver? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if aplay -l | grep -q "seeed"; then
        echo -e "${GREEN}ReSpeaker driver already installed${NC}"
    else
        echo "Installing ReSpeaker driver..."
        
        # Clone and install ReSpeaker driver
        cd /tmp
        if [ -d "seeed-voicecard" ]; then
            rm -rf seeed-voicecard
        fi
        
        git clone https://github.com/respeaker/seeed-voicecard.git
        cd seeed-voicecard
        sudo ./install.sh
        
        echo -e "${YELLOW}Note: System reboot required for ReSpeaker driver${NC}"
    fi
else
    echo "Skipping seeed-voicecard driver installation (USB mode will be used)"
fi

echo ""
echo "Step 3: Creating Python virtual environment..."
echo "=========================================="

cd "$(dirname "$0")"

if [ -d "venv" ]; then
    echo "Virtual environment already exists"
else
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate

echo ""
echo "Step 4: Installing Python dependencies..."
echo "=========================================="

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo ""
echo "Step 5: Downloading Vosk speech recognition model..."
echo "=========================================="

VOSK_MODEL="vosk-model-small-en-us-0.15"
VOSK_MODEL_URL="https://alphacephei.com/vosk/models/${VOSK_MODEL}.zip"

if [ -d "models/${VOSK_MODEL}" ]; then
    echo -e "${GREEN}Vosk model already exists${NC}"
else
    echo "Downloading Vosk model (this may take a few minutes)..."
    mkdir -p models
    cd models
    
    wget -q --show-progress ${VOSK_MODEL_URL}
    unzip -q ${VOSK_MODEL}.zip
    rm ${VOSK_MODEL}.zip
    
    cd ..
    echo -e "${GREEN}Vosk model downloaded${NC}"
fi

echo ""
echo "Step 6: Downloading OpenWakeWord models..."
echo "=========================================="

# OpenWakeWord models are downloaded automatically on first run
# But we can pre-download them
python3 << 'PYEOF'
try:
    from openwakeword.model import Model
    print("Pre-loading OpenWakeWord models...")
    model = Model(wakeword_models=['hey_jarvis'], inference_framework='onnx')
    print("OpenWakeWord models ready")
except Exception as e:
    print(f"Note: OpenWakeWord models will be downloaded on first run: {e}")
PYEOF

echo ""
echo "Step 7: Creating necessary directories..."
echo "=========================================="

mkdir -p logs
mkdir -p data/orders
mkdir -p models

echo ""
echo "Step 8: Testing audio devices..."
echo "=========================================="

echo "Available audio capture devices:"
arecord -l

echo ""
echo "Available audio playback devices:"
aplay -l

echo ""
echo "Step 9: Testing microphone..."
echo "=========================================="

echo "Recording 3-second audio test..."
arecord -D plughw:2,0 -f S16_LE -r 16000 -d 3 /tmp/test.wav 2>/dev/null || true

if [ -f /tmp/test.wav ]; then
    echo -e "${GREEN}Microphone test successful${NC}"
    rm /tmp/test.wav
else
    echo -e "${YELLOW}Warning: Microphone test failed${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "To run the Digital Waiter Robot:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the robot:"
echo "     python3 src/main.py"
echo ""
echo "Configuration files:"
echo "  - config/settings.yaml - Robot settings"
echo "  - config/menu.yaml - Restaurant menu"
echo ""
echo "Notes:"
echo "  - Make sure the ReSpeaker Mic Array is properly connected"
echo "  - Adjust microphone volume with: alsamixer"
echo "  - Check logs in: logs/robot.log"
echo ""

if ! aplay -l | grep -q "seeed"; then
    echo -e "${YELLOW}Warning: ReSpeaker device not detected${NC}"
    echo "You may need to reboot for the driver to load:"
    echo "  sudo reboot"
    echo ""
fi

echo "For more information, see README.md"
echo ""

