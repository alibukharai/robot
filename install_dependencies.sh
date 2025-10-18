#!/bin/bash

# Digital Waiter Robot - Dependency Installation Script
# This script installs all required dependencies for the robot

echo "=== Digital Waiter Robot Dependency Installation ==="
echo

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✓ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  Warning: No virtual environment detected. It's recommended to use a virtual environment."
    echo "   You can create one with: python3 -m venv venv && source venv/bin/activate"
    echo
fi

# Update system packages
echo "1. Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-dev build-essential

# Install Python dependencies
echo
echo "2. Installing Python dependencies..."

# Install core dependencies
pip install --upgrade pip

# Install audio libraries
echo "   Installing audio libraries..."
pip install pyaudio

# Install wake word detection
echo "   Installing wake word detection..."
pip install openwakeword

# Install speech recognition
echo "   Installing speech recognition..."
pip install vosk

# Install text-to-speech
echo "   Installing text-to-speech..."
pip install pyttsx3

# Install configuration and data handling
echo "   Installing configuration libraries..."
pip install PyYAML

# Install scientific computing
echo "   Installing scientific computing libraries..."
pip install numpy

# Verify installations
echo
echo "3. Verifying installations..."

python3 -c "
import sys
print(f'Python version: {sys.version}')
print(f'Python executable: {sys.executable}')
print()

# Test imports
try:
    import pyaudio
    print('✓ PyAudio imported successfully')
except ImportError as e:
    print(f'✗ PyAudio import failed: {e}')

try:
    import openwakeword
    print('✓ OpenWakeWord imported successfully')
    from openwakeword.model import Model
    model = Model()
    print(f'✓ OpenWakeWord models available: {list(model.models.keys())}')
except ImportError as e:
    print(f'✗ OpenWakeWord import failed: {e}')
except Exception as e:
    print(f'✗ OpenWakeWord model loading failed: {e}')

try:
    import vosk
    print('✓ Vosk imported successfully')
except ImportError as e:
    print(f'✗ Vosk import failed: {e}')

try:
    import pyttsx3
    print('✓ pyttsx3 imported successfully')
except ImportError as e:
    print(f'✗ pyttsx3 import failed: {e}')

try:
    import yaml
    print('✓ PyYAML imported successfully')
except ImportError as e:
    print(f'✗ PyYAML import failed: {e}')

try:
    import numpy
    print('✓ NumPy imported successfully')
except ImportError as e:
    print(f'✗ NumPy import failed: {e}')
"

echo
echo "4. Creating required directories..."
mkdir -p logs data/orders models

echo
echo "=== Installation Complete ==="
echo
echo "To test the installation, run:"
echo "  python3 src/main.py"
echo
echo "If you encounter any issues, make sure you're in the correct virtual environment:"
echo "  source venv/bin/activate  # if using venv"
echo "  source activate myenv     # if using conda"