#!/bin/bash

# Simple fix for OpenWakeWord model issues
# This script downgrades to a known working version

echo "=== OpenWakeWord Fix Script ==="
echo

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✓ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "❌ Error: No virtual environment detected!"
    echo "Please activate your virtual environment first:"
    echo "  source venv/bin/activate"
    exit 1
fi

echo "Current OpenWakeWord installation:"
pip show openwakeword

echo
echo "The issue is that OpenWakeWord 0.6.0 has compatibility problems."
echo "We'll downgrade to version 0.5.1 which is known to work reliably."
echo

read -p "Do you want to proceed with the fix? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Fix cancelled."
    exit 0
fi

echo "Uninstalling current OpenWakeWord..."
pip uninstall -y openwakeword

echo "Installing OpenWakeWord 0.5.1..."
pip install openwakeword==0.5.1

echo
echo "Testing the fix..."
python3 -c "
try:
    from openwakeword.model import Model
    print('✓ Import successful')
    
    model = Model()
    print('✓ Model initialization successful')
    print('Available models:', list(model.models.keys()))
    
    # Test prediction
    import numpy as np
    dummy_audio = np.zeros(1600, dtype=np.float32)
    predictions = model.predict(dummy_audio)
    print('✓ Prediction test successful')
    
    print()
    print('🎉 OpenWakeWord is now working correctly!')
    
except Exception as e:
    print('❌ Still having issues:', e)
    print('You may need to check your internet connection or try:')
    print('  pip install --force-reinstall openwakeword==0.5.1')
"

echo
echo "=== Fix Complete ==="
echo "You can now run: python3 src/main.py"