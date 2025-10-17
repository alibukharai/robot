"""
Microphone handler for ReSpeaker Mic Array v2.0
Handles audio input, VAD (Voice Activity Detection), and recording

ReSpeaker Mic Array v2.0 specifications:
- 4 digital MEMS microphones
- XVF-3000 chipset with on-board speech algorithms
- USB Audio Class 1.0 (UAC 1.0) - works as USB sound card
- 6-channel firmware (default):
  * Channel 0: Processed audio for ASR (recommended)
  * Channels 1-4: Raw microphone data
  * Channel 5: Merged playback
- Max sample rate: 16kHz
"""

import pyaudio
import numpy as np
import wave
import logging
from typing import Optional, Tuple
import time

logger = logging.getLogger(__name__)


class Microphone:
    """
    Microphone class for handling audio input from ReSpeaker Mic Array v2.0.
    
    The ReSpeaker Mic Array v2.0 is a USB device with 6 channels available.
    For ASR (speech recognition), we use Channel 0 which provides processed
    audio with on-chip algorithms (VAD, beamforming, noise suppression, AEC).
    
    Features:
    - Audio stream management
    - Voice Activity Detection (VAD)
    - Recording with automatic silence detection
    - USB device auto-detection for ReSpeaker
    - Support for 6-channel firmware (uses channel 0 for ASR)
    """
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1, 
                 chunk_size: int = 1024, device_name: Optional[str] = None):
        """
        Initialize the microphone.
        
        Args:
            sample_rate: Audio sample rate in Hz (default: 16000, max for ReSpeaker)
            channels: Number of audio channels (default: 1 for mono, channel 0)
            chunk_size: Size of audio chunks to read (default: 1024)
            device_name: Device name keyword to search for (e.g., "ReSpeaker", "XMOS")
                        If None, will auto-detect ReSpeaker or use default device
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.device_name = device_name
        
        self.audio = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        self.device_index = self._find_device_index()
        
        logger.info(f"Microphone initialized: {sample_rate}Hz, {channels} channel(s)")
        if self.device_index is not None:
            device_info = self.audio.get_device_info_by_index(self.device_index)
            logger.info(f"Using device: {device_info.get('name')}")
        
    def _find_device_index(self) -> Optional[int]:
        """
        Find the device index for ReSpeaker USB device.
        
        The ReSpeaker Mic Array v2.0 appears as a USB audio device.
        We search for common identifiers: "ReSpeaker", "XMOS", "USB PnP".
        
        Returns:
            Device index if found, None to use default
        """
        # Auto-detect ReSpeaker if no specific name given
        if self.device_name is None:
            respeaker_keywords = ["respeaker", "xmos", "usb pnp audio"]
            
            for i in range(self.audio.get_device_count()):
                info = self.audio.get_device_info_by_index(i)
                device_name = info.get('name', '').lower()
                
                # Check if input device
                if info.get('maxInputChannels', 0) == 0:
                    continue
                
                # Look for ReSpeaker identifiers
                for keyword in respeaker_keywords:
                    if keyword in device_name:
                        logger.info(f"Auto-detected ReSpeaker: {info.get('name')} (index: {i})")
                        logger.info(f"Device channels: {info.get('maxInputChannels')}")
                        return i
            
            logger.info("ReSpeaker not auto-detected, using default audio input device")
            return None
        
        # Search for user-specified device name
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            device_name = info.get('name', '').lower()
            
            # Check if this is the target device
            if self.device_name.lower() in device_name:
                logger.info(f"Found device: {info.get('name')} (index: {i})")
                return i
                
        logger.warning(f"Device '{self.device_name}' not found, using default")
        return None
        
    def start_stream(self) -> None:
        """Start the audio input stream."""
        if self.stream is not None:
            logger.warning("Stream already started")
            return
            
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=None
            )
            logger.info("Audio stream started")
        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")
            raise
            
    def stop_stream(self) -> None:
        """Stop the audio input stream."""
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            logger.info("Audio stream stopped")
            
    def read_chunk(self) -> Optional[bytes]:
        """
        Read a single chunk of audio data.
        
        Returns:
            Audio data as bytes, or None if stream not active
        """
        if self.stream is None:
            logger.error("Stream not started")
            return None
            
        try:
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            return data
        except Exception as e:
            logger.error(f"Error reading audio chunk: {e}")
            return None
            
    def record_until_silence(self, silence_threshold: int = 500, 
                            silence_duration: float = 1.5,
                            max_duration: float = 10.0) -> Optional[bytes]:
        """
        Record audio until silence is detected or max duration reached.
        
        Args:
            silence_threshold: Amplitude threshold for silence detection
            silence_duration: Seconds of silence before stopping
            max_duration: Maximum recording duration in seconds
            
        Returns:
            Recorded audio as bytes, or None if error
        """
        if self.stream is None:
            logger.error("Stream not started")
            return None
            
        logger.info("Recording started...")
        frames = []
        silent_chunks = 0
        chunks_per_silence = int(self.sample_rate / self.chunk_size * silence_duration)
        max_chunks = int(self.sample_rate / self.chunk_size * max_duration)
        
        start_time = time.time()
        
        try:
            for _ in range(max_chunks):
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                # Calculate audio amplitude for VAD
                audio_data = np.frombuffer(data, dtype=np.int16)
                amplitude = np.abs(audio_data).mean()
                
                if amplitude < silence_threshold:
                    silent_chunks += 1
                    if silent_chunks >= chunks_per_silence:
                        logger.info(f"Silence detected after {time.time() - start_time:.2f}s")
                        break
                else:
                    silent_chunks = 0
                    
            duration = time.time() - start_time
            logger.info(f"Recording finished: {duration:.2f}s, {len(frames)} chunks")
            
            return b''.join(frames)
            
        except Exception as e:
            logger.error(f"Error during recording: {e}")
            return None
            
    def save_audio(self, audio_data: bytes, filename: str) -> bool:
        """
        Save audio data to a WAV file.
        
        Args:
            audio_data: Raw audio bytes
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data)
            logger.info(f"Audio saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            return False
            
    def list_devices(self) -> None:
        """List all available audio input devices."""
        logger.info("Available audio input devices:")
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info.get('maxInputChannels', 0) > 0:
                logger.info(f"  [{i}] {info.get('name')} - "
                          f"{info.get('maxInputChannels')} channels")
                          
    def close(self) -> None:
        """Clean up resources."""
        self.stop_stream()
        self.audio.terminate()
        logger.info("Microphone closed")
        
    def __enter__(self):
        """Context manager entry."""
        self.start_stream()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

