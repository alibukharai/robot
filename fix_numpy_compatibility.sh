#!/bin/bash

# Fix NumPy compatibility issue with OpenWakeWord
echo "=== NumPy Compatibility Fix ==="
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

echo "Current NumPy version:"
python3 -c "import numpy; print('NumPy version:', numpy.__version__)"

echo
echo "The issue is that OpenWakeWord was compiled with NumPy 1.x"
echo "but you have NumPy 2.x installed, which is incompatible."
echo "We need to downgrade NumPy to version 1.24.x"
echo

read -p "Do you want to proceed with the NumPy downgrade? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Fix cancelled."
    exit 0
fi

echo "Downgrading NumPy to compatible version..."
pip install "numpy<2.0,>=1.21.0"

echo
echo "Reinstalling OpenWakeWord to ensure compatibility..."
pip uninstall -y openwakeword
pip install openwakeword==0.5.1

echo
echo "Testing the fix..."
python3 -c "
try:
    import numpy
    print(f'✓ NumPy version: {numpy.__version__}')
    
    from openwakeword.model import Model
    print('✓ OpenWakeWord import successful')
    
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
    import traceback
    traceback.print_exc()
"

echo
echo "=== Fix Complete ==="
echo "You can now run: python3 src/main.py"