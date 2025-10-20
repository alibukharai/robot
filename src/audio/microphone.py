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
        We search for common identifiers and prioritize ReSpeaker devices.
        
        Returns:
            Device index if found, None to use default
        """
        # Auto-detect ReSpeaker if no specific name given
        if self.device_name is None:
            # Enhanced keywords for better detection on Raspberry Pi
            respeaker_keywords = [
                "respeaker", "xmos", "usb pnp audio", "seeed", 
                "xvf3000", "usb audio", "mic array"
            ]
            
            # Store potential matches with priority
            potential_devices = []
            
            logger.info("Scanning for audio input devices...")
            for i in range(self.audio.get_device_count()):
                try:
                    info = self.audio.get_device_info_by_index(i)
                    device_name = info.get('name', '').lower()
                    max_input_channels = info.get('maxInputChannels', 0)
                    
                    # Skip output-only devices
                    if max_input_channels == 0:
                        continue
                    
                    logger.debug(f"Device {i}: {info.get('name')} - {max_input_channels} input channels")
                    
                    # Check for ReSpeaker identifiers with priority
                    priority = 0
                    for j, keyword in enumerate(respeaker_keywords):
                        if keyword in device_name:
                            priority = len(respeaker_keywords) - j  # Higher priority for earlier keywords
                            break
                    
                    # Special handling for common ReSpeaker device names
                    if "respeaker" in device_name:
                        priority += 10
                    elif "seeed" in device_name:
                        priority += 8
                    elif "xmos" in device_name:
                        priority += 6
                    elif max_input_channels >= 4:  # Multi-channel devices are likely ReSpeaker
                        priority += 2
                    
                    if priority > 0:
                        potential_devices.append((priority, i, info))
                        
                except Exception as e:
                    logger.debug(f"Error checking device {i}: {e}")
                    continue
            
            # Sort by priority (highest first)
            potential_devices.sort(reverse=True, key=lambda x: x[0])
            
            if potential_devices:
                priority, device_index, info = potential_devices[0]
                logger.info(f"Auto-detected audio device: {info.get('name')} (index: {device_index})")
                logger.info(f"Device channels: {info.get('maxInputChannels')}, Sample rate: {info.get('defaultSampleRate')}")
                return device_index
            
            logger.warning("No ReSpeaker device found, checking for any suitable input device...")
            
            # Fallback: find any input device with sufficient channels
            for i in range(self.audio.get_device_count()):
                try:
                    info = self.audio.get_device_info_by_index(i)
                    if info.get('maxInputChannels', 0) >= 1:
                        logger.info(f"Using fallback device: {info.get('name')} (index: {i})")
                        return i
                except:
                    continue
            
            logger.info("No suitable audio input device found, using system default")
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
        """Start the audio input stream with retry logic."""
        if self.stream is not None:
            logger.warning("Stream already started")
            return
            
        # Try different configurations if the first attempt fails
        configs_to_try = [
            # Original configuration
            {
                'format': pyaudio.paInt16,
                'channels': self.channels,
                'rate': self.sample_rate,
                'frames_per_buffer': self.chunk_size
            },
            # Raspberry Pi friendly configuration
            {
                'format': pyaudio.paInt16,
                'channels': 1,  # Force mono
                'rate': 16000,  # Force 16kHz
                'frames_per_buffer': 1024  # Smaller buffer
            },
            # More conservative configuration
            {
                'format': pyaudio.paInt16,
                'channels': 1,
                'rate': 8000,  # Lower sample rate
                'frames_per_buffer': 512  # Even smaller buffer
            }
        ]
        
        last_error = None
        
        for i, config in enumerate(configs_to_try):
            try:
                logger.info(f"Attempting to start audio stream (config {i+1}/3)...")
                logger.info(f"  Format: {config['format']}")
                logger.info(f"  Channels: {config['channels']}")
                logger.info(f"  Sample rate: {config['rate']}")
                logger.info(f"  Buffer size: {config['frames_per_buffer']}")
                logger.info(f"  Device index: {self.device_index}")
                
                self.stream = self.audio.open(
                    format=config['format'],
                    channels=config['channels'],
                    rate=config['rate'],
                    input=True,
                    input_device_index=self.device_index,
                    frames_per_buffer=config['frames_per_buffer'],
                    stream_callback=None
                )
                
                # Update instance variables if different config was used
                if i > 0:
                    self.channels = config['channels']
                    self.sample_rate = config['rate']
                    self.chunk_size = config['frames_per_buffer']
                    logger.info(f"Updated audio parameters: {self.sample_rate}Hz, {self.channels} channels, {self.chunk_size} buffer")
                
                logger.info("Audio stream started successfully")
                return
                
            except Exception as e:
                last_error = e
                logger.warning(f"Configuration {i+1} failed: {e}")
                if i < len(configs_to_try) - 1:
                    logger.info("Trying next configuration...")
                continue
        
        # If all configurations failed
        logger.error(f"Failed to start audio stream with all configurations. Last error: {last_error}")
        
        # Try to list available devices for debugging
        try:
            logger.error("Available audio devices for debugging:")
            for i in range(self.audio.get_device_count()):
                info = self.audio.get_device_info_by_index(i)
                if info.get('maxInputChannels', 0) > 0:
                    logger.error(f"  [{i}] {info.get('name')} - {info.get('maxInputChannels')} channels")
        except:
            pass
            
        raise RuntimeError(f"Unable to start audio stream: {last_error}")
            
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

