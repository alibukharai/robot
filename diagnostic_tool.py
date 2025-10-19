#!/usr/bin/env python3
"""
Digital Waiter Robot Diagnostic Tool
Comprehensive testing and troubleshooting utility
"""

import sys
import os
import logging
import subprocess
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def run_command(cmd, capture_output=True):
    """Run a shell command and return result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_system_dependencies():
    """Test system-level dependencies."""
    print("🔍 Testing System Dependencies")
    print("=" * 40)
    
    dependencies = [
        ("Python 3", "python3 --version"),
        ("pip", "pip --version"),
        ("espeak", "espeak --version"),
        ("arecord", "arecord --version"),
        ("aplay", "aplay --version"),
    ]
    
    results = {}
    for name, cmd in dependencies:
        success, stdout, stderr = run_command(cmd)
        results[name] = success
        status = "✅" if success else "❌"
        print(f"{status} {name}: {'OK' if success else 'MISSING'}")
        if success and stdout:
            print(f"   Version: {stdout.strip().split()[0] if stdout else 'Unknown'}")
    
    return results

def test_python_dependencies():
    """Test Python package dependencies."""
    print("\n🐍 Testing Python Dependencies")
    print("=" * 40)
    
    packages = [
        "pyaudio",
        "vosk", 
        "openwakeword",
        "pyttsx3",
        "yaml",
        "numpy"
    ]
    
    results = {}
    for package in packages:
        try:
            __import__(package)
            results[package] = True
            print(f"✅ {package}: OK")
        except ImportError as e:
            results[package] = False
            print(f"❌ {package}: MISSING ({e})")
    
    return results

def test_audio_devices():
    """Test audio input/output devices."""
    print("\n🔊 Testing Audio Devices")
    print("=" * 40)
    
    # List recording devices
    print("Recording devices:")
    success, stdout, stderr = run_command("arecord -l")
    if success:
        lines = stdout.strip().split('\n')
        for line in lines:
            if 'card' in line.lower():
                print(f"  📱 {line}")
    else:
        print("  ❌ Could not list recording devices")
    
    # List playback devices  
    print("\nPlayback devices:")
    success, stdout, stderr = run_command("aplay -l")
    if success:
        lines = stdout.strip().split('\n')
        for line in lines:
            if 'card' in line.lower():
                print(f"  🔊 {line}")
    else:
        print("  ❌ Could not list playback devices")
    
    # Check for ReSpeaker
    respeaker_found = False
    if success and stdout:
        if any(keyword in stdout.lower() for keyword in ['respeaker', 'seeed', 'xmos']):
            respeaker_found = True
            print("  ✅ ReSpeaker detected!")
        else:
            print("  ⚠️  ReSpeaker not detected")
    
    return respeaker_found

def test_models():
    """Test if required models are present."""
    print("\n🧠 Testing Models")
    print("=" * 40)
    
    results = {}
    
    # Check Vosk model
    vosk_model_path = Path("models/vosk-model-small-en-us-0.15")
    if vosk_model_path.exists():
        print("✅ Vosk model: Found")
        results['vosk'] = True
        
        # Test loading
        try:
            from vosk import Model
            model = Model(str(vosk_model_path))
            print("  ✅ Model loads successfully")
            results['vosk_load'] = True
        except Exception as e:
            print(f"  ❌ Model loading failed: {e}")
            results['vosk_load'] = False
    else:
        print("❌ Vosk model: Missing")
        print(f"  Expected at: {vosk_model_path}")
        results['vosk'] = False
        results['vosk_load'] = False
    
    # Check OpenWakeWord models
    try:
        from openwakeword.model import Model
        oww_model = Model()
        available_models = list(oww_model.models.keys())
        print(f"✅ OpenWakeWord models: {', '.join(available_models)}")
        results['openwakeword'] = True
    except Exception as e:
        print(f"❌ OpenWakeWord models: Failed to load ({e})")
        results['openwakeword'] = False
    
    return results

def test_configuration():
    """Test configuration files."""
    print("\n⚙️ Testing Configuration")
    print("=" * 40)
    
    results = {}
    
    # Check settings.yaml
    settings_path = Path("config/settings.yaml")
    if settings_path.exists():
        print("✅ settings.yaml: Found")
        try:
            import yaml
            with open(settings_path) as f:
                config = yaml.safe_load(f)
            print("  ✅ Valid YAML format")
            results['settings'] = True
        except Exception as e:
            print(f"  ❌ Invalid YAML: {e}")
            results['settings'] = False
    else:
        print("❌ settings.yaml: Missing")
        results['settings'] = False
    
    # Check menu.yaml
    menu_path = Path("config/menu.yaml")
    if menu_path.exists():
        print("✅ menu.yaml: Found")
        try:
            import yaml
            with open(menu_path) as f:
                menu = yaml.safe_load(f)
            item_count = sum(len(cat.get('items', [])) for cat in menu.get('categories', []))
            print(f"  ✅ {item_count} menu items loaded")
            results['menu'] = True
        except Exception as e:
            print(f"  ❌ Invalid menu YAML: {e}")
            results['menu'] = False
    else:
        print("❌ menu.yaml: Missing")
        results['menu'] = False
    
    return results

def test_directories():
    """Test required directories."""
    print("\n📁 Testing Directories")
    print("=" * 40)
    
    required_dirs = [
        "logs",
        "data/orders", 
        "models",
        "config"
    ]
    
    results = {}
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}: Exists")
            results[dir_path] = True
        else:
            print(f"❌ {dir_path}: Missing")
            results[dir_path] = False
    
    return results

def test_audio_functionality():
    """Test basic audio functionality."""
    print("\n🎵 Testing Audio Functionality")
    print("=" * 40)
    
    # Test TTS
    print("Testing text-to-speech...")
    success, stdout, stderr = run_command('espeak "Testing audio output" 2>/dev/null')
    if success:
        print("✅ TTS: Working")
    else:
        print("❌ TTS: Failed")
    
    # Test microphone (record 2 seconds)
    print("Testing microphone (2 second recording)...")
    success, stdout, stderr = run_command('timeout 2s arecord -f S16_LE -r 16000 -c 1 /tmp/test_audio.wav 2>/dev/null')
    if success and Path("/tmp/test_audio.wav").exists():
        print("✅ Microphone: Working")
        # Clean up
        Path("/tmp/test_audio.wav").unlink(missing_ok=True)
    else:
        print("❌ Microphone: Failed")

def generate_report(all_results):
    """Generate a comprehensive diagnostic report."""
    print("\n📊 DIAGNOSTIC REPORT")
    print("=" * 50)
    
    total_tests = sum(len(results) for results in all_results.values())
    passed_tests = sum(sum(results.values()) for results in all_results.values())
    
    print(f"Overall Status: {passed_tests}/{total_tests} tests passed")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nCritical Issues:")
    critical_issues = []
    
    # Check critical dependencies
    if not all_results.get('python_deps', {}).get('vosk', False):
        critical_issues.append("❌ Vosk not installed - speech recognition will not work")
    
    if not all_results.get('python_deps', {}).get('openwakeword', False):
        critical_issues.append("❌ OpenWakeWord not installed - wake word detection will not work")
    
    if not all_results.get('models', {}).get('vosk', False):
        critical_issues.append("❌ Vosk model missing - download required")
    
    if not all_results.get('directories', {}).get('logs', False):
        critical_issues.append("❌ Logs directory missing - application may crash")
    
    if critical_issues:
        for issue in critical_issues:
            print(f"  {issue}")
    else:
        print("  ✅ No critical issues found!")
    
    print("\nRecommendations:")
    if not all_results.get('models', {}).get('vosk', False):
        print("  1. Run: ./enhanced_setup.sh to download models")
    
    if not all_results.get('python_deps', {}).get('vosk', False):
        print("  2. Install Python dependencies: pip install -r requirements.txt")
    
    missing_dirs = [d for d, exists in all_results.get('directories', {}).items() if not exists]
    if missing_dirs:
        print(f"  3. Create missing directories: mkdir -p {' '.join(missing_dirs)}")
    
    print("\nNext Steps:")
    if passed_tests == total_tests:
        print("  🎉 All tests passed! Your robot should work perfectly.")
        print("  🚀 Start with: python3 src/main.py")
    elif passed_tests > total_tests * 0.8:
        print("  ⚠️  Most tests passed. Fix the issues above and retry.")
    else:
        print("  🔧 Multiple issues found. Run ./enhanced_setup.sh first.")

def main():
    """Run all diagnostic tests."""
    print("🤖 Digital Waiter Robot Diagnostic Tool")
    print("=" * 50)
    
    all_results = {}
    
    # Run all tests
    all_results['system_deps'] = test_system_dependencies()
    all_results['python_deps'] = test_python_dependencies()
    all_results['audio_devices'] = {'respeaker': test_audio_devices()}
    all_results['models'] = test_models()
    all_results['config'] = test_configuration()
    all_results['directories'] = test_directories()
    
    # Test audio functionality
    test_audio_functionality()
    
    # Generate report
    generate_report(all_results)
    
    # Save detailed results
    with open('diagnostic_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\n💾 Detailed results saved to: diagnostic_results.json")

if __name__ == "__main__":
    main()