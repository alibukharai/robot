"""
Speech module for ASR (Automatic Speech Recognition) and TTS (Text-to-Speech).
All components are offline and license-free for commercial use.
"""

from .recognizer import SpeechRecognizer
from .synthesizer import SpeechSynthesizer

__all__ = ["SpeechRecognizer", "SpeechSynthesizer"]

