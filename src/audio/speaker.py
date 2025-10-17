"""
Speaker handler for audio output
Manages audio playback through the system
"""

import pyaudio
import wave
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Speaker:
    """
    Speaker class for handling audio output.
    
    Features:
    - Audio playback from WAV files
    - Volume control
    - Stream management
    """
    
    def __init__(self, device_index: Optional[int] = None):
        """
        Initialize the speaker.
        
        Args:
            device_index: Specific device index to use (None for default)
        """
        self.device_index = device_index
        self.audio = pyaudio.PyAudio()
        logger.info("Speaker initialized")
        
    def play_wav(self, filename: str, volume: float = 1.0) -> bool:
        """
        Play a WAV file through the speaker.
        
        Args:
            filename: Path to WAV file
            volume: Volume level (0.0 to 1.0)
            
        Returns:
            True if playback successful, False otherwise
        """
        try:
            # Open the WAV file
            with wave.open(filename, 'rb') as wf:
                # Create output stream
                stream = self.audio.open(
                    format=self.audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    output_device_index=self.device_index
                )
                
                # Read and play audio in chunks
                chunk_size = 1024
                data = wf.readframes(chunk_size)
                
                while data:
                    stream.write(data)
                    data = wf.readframes(chunk_size)
                    
                # Clean up
                stream.stop_stream()
                stream.close()
                
            logger.info(f"Played audio file: {filename}")
            return True
            
        except FileNotFoundError:
            logger.error(f"Audio file not found: {filename}")
            return False
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False
            
    def list_devices(self) -> None:
        """List all available audio output devices."""
        logger.info("Available audio output devices:")
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info.get('maxOutputChannels', 0) > 0:
                logger.info(f"  [{i}] {info.get('name')} - "
                          f"{info.get('maxOutputChannels')} channels")
                          
    def close(self) -> None:
        """Clean up resources."""
        self.audio.terminate()
        logger.info("Speaker closed")
        
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

