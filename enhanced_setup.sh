#!/bin/bash

# Enhanced Digital Waiter Robot Setup Script
# This script sets up all dependencies and downloads required models

set -e  # Exit on any error

echo "🤖 Enhanced Digital Waiter Robot Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Raspberry Pi
if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    print_status "Detected Raspberry Pi"
    IS_RPI=true
else
    print_warning "Not running on Raspberry Pi - some optimizations may not apply"
    IS_RPI=false
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    portaudio19-dev \
    libasound2-dev \
    espeak \
    espeak-data \
    alsa-utils \
    wget \
    unzip \
    git \
    build-essential

# Install additional audio libraries for Raspberry Pi
if [ "$IS_RPI" = true ]; then
    print_status "Installing Raspberry Pi audio packages..."
    sudo apt install -y \
        pulseaudio \
        pulseaudio-utils \
        pavucontrol
fi

# Create project directories
print_status "Creating project directories..."
mkdir -p logs data/orders models

# Create Python virtual environment
print_status "Creating Python virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists, removing old one..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Download Vosk speech recognition model
print_status "Downloading speech recognition model..."
cd models

# Check if model already exists
if [ -d "vosk-model-small-en-us-0.15" ]; then
    print_warning "Vosk model already exists, skipping download..."
else
    print_status "Downloading Vosk model (this may take a few minutes)..."
    wget -q --show-progress https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    
    print_status "Extracting model..."
    unzip -q vosk-model-small-en-us-0.15.zip
    rm vosk-model-small-en-us-0.15.zip
    
    print_status "Vosk model installed successfully"
fi

cd ..

# Test audio system
print_status "Testing audio system..."

# Test speakers
print_status "Testing text-to-speech..."
if command -v espeak >/dev/null 2>&1; then
    espeak "Audio test successful" 2>/dev/null || print_warning "TTS test failed"
else
    print_warning "espeak not found"
fi

# List audio devices
print_status "Available audio devices:"
arecord -l 2>/dev/null || print_warning "Could not list recording devices"
aplay -l 2>/dev/null || print_warning "Could not list playback devices"

# Test Python imports
print_status "Testing Python dependencies..."
python3 << EOF
try:
    import pyaudio
    print("✓ PyAudio imported successfully")
except ImportError as e:
    print("✗ PyAudio import failed:", e)

try:
    import vosk
    print("✓ Vosk imported successfully")
except ImportError as e:
    print("✗ Vosk import failed:", e)

try:
    import openwakeword
    print("✓ OpenWakeWord imported successfully")
except ImportError as e:
    print("✗ OpenWakeWord import failed:", e)

try:
    import pyttsx3
    print("✓ pyttsx3 imported successfully")
except ImportError as e:
    print("✗ pyttsx3 import failed:", e)

try:
    import yaml
    print("✓ PyYAML imported successfully")
except ImportError as e:
    print("✗ PyYAML import failed:", e)
EOF

# Test Vosk model loading
print_status "Testing Vosk model..."
python3 << EOF
try:
    from vosk import Model
    model = Model('models/vosk-model-small-en-us-0.15')
    print("✓ Vosk model loaded successfully")
except Exception as e:
    print("✗ Vosk model test failed:", e)
EOF

# Create systemd service (optional)
if [ "$IS_RPI" = true ]; then
    print_status "Would you like to create a systemd service for auto-start? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        SERVICE_FILE="/etc/systemd/system/digital-waiter.service"
        WORK_DIR=$(pwd)
        USER=$(whoami)
        
        sudo tee $SERVICE_FILE > /dev/null << EOF
[Unit]
Description=Digital Waiter Robot
After=network.target sound.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORK_DIR
Environment=PATH=$WORK_DIR/venv/bin
ExecStart=$WORK_DIR/venv/bin/python3 $WORK_DIR/src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        sudo systemctl enable digital-waiter.service
        print_status "Systemd service created. Use 'sudo systemctl start digital-waiter' to start"
    fi
fi

# Final setup completion
print_status "Setup completed successfully!"
echo ""
echo "🎉 Your Digital Waiter Robot is ready!"
echo ""
echo "To start the robot:"
echo "  1. source venv/bin/activate"
echo "  2. python3 src/main.py"
echo ""
echo "To test individual components:"
echo "  - Test TTS: espeak 'Hello World'"
echo "  - Test microphone: arecord -d 5 test.wav && aplay test.wav"
echo "  - Check audio devices: arecord -l"
echo ""

if [ "$IS_RPI" = true ]; then
    echo "Raspberry Pi specific notes:"
    echo "  - Make sure your ReSpeaker is connected to a USB 3.0 port (blue)"
    echo "  - You may need to reboot after first setup"
    echo "  - Use 'alsamixer' to adjust microphone levels"
    echo ""
fi

print_status "Setup script completed!"