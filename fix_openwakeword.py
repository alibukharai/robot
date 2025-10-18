#!/usr/bin/env python3
"""
Fix OpenWakeWord model issues
This script helps resolve missing model files and version compatibility issues
"""

import os
import sys
import logging
import traceback
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_openwakeword_installation():
    """Check OpenWakeWord installation and available models"""
    try:
        import openwakeword
        logger.info(f"OpenWakeWord is installed")
        
        # Try to get version
        try:
            version = openwakeword.__version__
            logger.info(f"OpenWakeWord version: {version}")
        except AttributeError:
            logger.info("OpenWakeWord version: Unknown (no __version__ attribute)")
        
        # Check installation path
        install_path = Path(openwakeword.__file__).parent
        logger.info(f"Installation path: {install_path}")
        
        # Check models directory
        models_dir = install_path / "resources" / "models"
        if models_dir.exists():
            logger.info(f"Models directory exists: {models_dir}")
            
            # List all files in models directory
            model_files = list(models_dir.glob("*"))
            logger.info(f"Found {len(model_files)} files in models directory:")
            for f in sorted(model_files):
                logger.info(f"  {f.name}")
                
            # Check for specific model types
            tflite_files = list(models_dir.glob("*.tflite"))
            onnx_files = list(models_dir.glob("*.onnx"))
            
            logger.info(f"TensorFlow Lite models: {len(tflite_files)}")
            logger.info(f"ONNX models: {len(onnx_files)}")
            
            return True, models_dir, tflite_files, onnx_files
        else:
            logger.error(f"Models directory not found: {models_dir}")
            return False, None, [], []
            
    except ImportError as e:
        logger.error(f"OpenWakeWord not installed: {e}")
        return False, None, [], []

def test_model_initialization():
    """Test different ways to initialize OpenWakeWord models"""
    try:
        from openwakeword.model import Model
        
        # Test 1: Default initialization
        logger.info("Testing default Model() initialization...")
        try:
            model = Model()
            logger.info(f"✓ Default initialization successful")
            logger.info(f"Available models: {list(model.models.keys())}")
            return True, model
        except Exception as e:
            logger.error(f"✗ Default initialization failed: {e}")
            
        # Test 2: Force ONNX
        logger.info("Testing ONNX inference framework...")
        try:
            model = Model(inference_framework='onnx')
            logger.info(f"✓ ONNX initialization successful")
            logger.info(f"Available models: {list(model.models.keys())}")
            return True, model
        except Exception as e:
            logger.error(f"✗ ONNX initialization failed: {e}")
            
        # Test 3: Force TensorFlow Lite
        logger.info("Testing TensorFlow Lite inference framework...")
        try:
            model = Model(inference_framework='tflite')
            logger.info(f"✓ TensorFlow Lite initialization successful")
            logger.info(f"Available models: {list(model.models.keys())}")
            return True, model
        except Exception as e:
            logger.error(f"✗ TensorFlow Lite initialization failed: {e}")
            
        return False, None
        
    except ImportError as e:
        logger.error(f"Cannot import Model class: {e}")
        return False, None

def download_models():
    """Try to download missing models"""
    logger.info("Attempting to download missing models...")
    
    try:
        from openwakeword.model import Model
        
        # The Model class should automatically download models on first use
        # Try initializing with different parameters to trigger downloads
        
        logger.info("Initializing model to trigger downloads...")
        model = Model()
        logger.info("✓ Model initialization completed (models should be downloaded)")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download models: {e}")
        return False

def fix_openwakeword_version():
    """Try to fix OpenWakeWord by reinstalling compatible version"""
    logger.info("Attempting to fix OpenWakeWord installation...")
    
    try:
        import subprocess
        
        # Try to reinstall a known working version
        logger.info("Reinstalling OpenWakeWord 0.5.1 (known stable version)...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "openwakeword==0.5.1", "--force-reinstall"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✓ Successfully reinstalled OpenWakeWord 0.5.1")
            return True
        else:
            logger.error(f"Failed to reinstall: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error during reinstallation: {e}")
        return False

def main():
    """Main function to diagnose and fix OpenWakeWord issues"""
    logger.info("=== OpenWakeWord Diagnostic and Fix Tool ===")
    
    # Step 1: Check installation
    logger.info("\n1. Checking OpenWakeWord installation...")
    installed, models_dir, tflite_files, onnx_files = check_openwakeword_installation()
    
    if not installed:
        logger.error("OpenWakeWord is not properly installed. Please run: pip install openwakeword")
        return 1
    
    # Step 2: Test model initialization
    logger.info("\n2. Testing model initialization...")
    success, model = test_model_initialization()
    
    if success:
        logger.info("✓ OpenWakeWord is working correctly!")
        return 0
    
    # Step 3: Try to download models
    logger.info("\n3. Attempting to fix by downloading models...")
    if download_models():
        # Test again
        success, model = test_model_initialization()
        if success:
            logger.info("✓ Fixed by downloading models!")
            return 0
    
    # Step 4: Try reinstalling compatible version
    logger.info("\n4. Attempting to fix by reinstalling compatible version...")
    if fix_openwakeword_version():
        # Test again
        success, model = test_model_initialization()
        if success:
            logger.info("✓ Fixed by reinstalling compatible version!")
            return 0
    
    # If we get here, nothing worked
    logger.error("\n=== Fix Failed ===")
    logger.error("Unable to fix OpenWakeWord automatically.")
    logger.error("\nManual steps to try:")
    logger.error("1. Reinstall OpenWakeWord: pip uninstall openwakeword && pip install openwakeword==0.5.1")
    logger.error("2. Check internet connection (models need to be downloaded)")
    logger.error("3. Try in a fresh virtual environment")
    logger.error("4. Check system dependencies: sudo apt-get install portaudio19-dev")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())