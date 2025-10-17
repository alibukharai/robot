"""
Audio module for handling microphone input and speaker output.
Optimized for ReSpeaker Mic Array v2.0 on Raspberry Pi 5.
"""

from .microphone import Microphone
from .speaker import Speaker

__all__ = ["Microphone", "Speaker"]

