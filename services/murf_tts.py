"""
Murf TTS Service - Handles text-to-speech conversion using Murf API WebSocket streaming
Supports chunking for texts longer than 3000 characters
"""

import asyncio
import json
import base64
import websockets
import os
from typing import List, Dict, Optional, AsyncGenerator
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class VoiceConfig:
    """Voice configuration for Murf TTS"""
    voice_id: str = "en-US-amara"
    style: str = "Conversational"
    rate: int = 0
    pitch: int = 0
    variation: int = 1

@dataclass
class TTSRequest:
    """TTS request structure"""
    text: str
    voice_config: VoiceConfig
    context_id: Optional[str] = None

class MurfTTSService:
    """Murf TTS Service with WebSocket streaming support"""
    
    def __init__(self):
        self.api_key = os.getenv("MURF_API_KEY")
        self.ws_url = os.getenv("MURF_WS_URL", "wss://api.murf.ai/v1/speech/stream-input")
        self.sample_rate = int(os.getenv("DEFAULT_SAMPLE_RATE", "44100"))
        self.channel_type = os.getenv("DEFAULT_CHANNEL_TYPE", "MONO")
        self.format = os.getenv("DEFAULT_FORMAT", "WAV")
        self.max_chunk_size = 3000  # Murf's character limit
        
        if not self.api_key:
            raise ValueError("MURF_API_KEY environment variable is required")
    
    def chunk_text(self, text: str, max_size: int = 3000) -> List[str]:
        """
        Split text into chunks that fit within Murf's character limit
        Tries to break at sentence boundaries when possible
        """
        if len(text) <= max_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by sentences first
        sentences = text.split('. ')
        
        for sentence in sentences:
            # Add period back if it's not the last sentence
            if sentence != sentences[-1]:
                sentence += '. '
            
            # If adding this sentence would exceed limit, save current chunk and start new one
            if len(current_chunk + sentence) > max_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # Single sentence is too long, split by words
                    words = sentence.split()
                    for word in words:
                        if len(current_chunk + word + " ") > max_size:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                                current_chunk = word + " "
                            else:
                                # Single word is too long, truncate
                                chunks.append(word[:max_size])
                        else:
                            current_chunk += word + " "
            else:
                current_chunk += sentence
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def stream_audio(self, request: TTSRequest) -> AsyncGenerator[bytes, None]:
        """
        Stream audio from Murf TTS using WebSocket
        Handles text chunking automatically for long texts
        """
        # Chunk the text if it's too long
        text_chunks = self.chunk_text(request.text, self.max_chunk_size)
        
        # Build WebSocket URL with parameters
        ws_url = f"{self.ws_url}?api-key={self.api_key}&sample_rate={self.sample_rate}&channel_type={self.channel_type}&format={self.format}"
        
        try:
            async with websockets.connect(ws_url) as ws:
                # Send voice configuration
                voice_config_msg = {
                    "voice_config": {
                        "voiceId": request.voice_config.voice_id,
                        "style": request.voice_config.style,
                        "rate": request.voice_config.rate,
                        "pitch": request.voice_config.pitch,
                        "variation": request.voice_config.variation
                    }
                }
                
                if request.context_id:
                    voice_config_msg["context_id"] = request.context_id
                
                await ws.send(json.dumps(voice_config_msg))
                logger.info(f"Sent voice config: {voice_config_msg}")
                
                # Process each text chunk
                for i, chunk in enumerate(text_chunks):
                    text_msg = {
                        "text": chunk,
                        "end": i == len(text_chunks) - 1  # End flag for last chunk
                    }
                    
                    await ws.send(json.dumps(text_msg))
                    logger.info(f"Sent text chunk {i+1}/{len(text_chunks)}: {len(chunk)} chars")
                    
                    # Receive audio for this chunk
                    first_chunk = True
                    while True:
                        response = await ws.recv()
                        data = json.loads(response)
                        
                        if "audio" in data:
                            audio_bytes = base64.b64decode(data["audio"])
                            
                            # Skip WAV header for first chunk of first text chunk
                            if first_chunk and i == 0 and len(audio_bytes) > 44:
                                audio_bytes = audio_bytes[44:]
                            
                            first_chunk = False
                            yield audio_bytes
                        
                        if data.get("final"):
                            break
                
                logger.info("TTS streaming completed")
                
        except Exception as e:
            logger.error(f"Error in TTS streaming: {e}")
            raise
    
    async def generate_audio_file(self, request: TTSRequest, output_path: str) -> str:
        """
        Generate complete audio file from text
        """
        audio_chunks = []
        
        async for audio_chunk in self.stream_audio(request):
            audio_chunks.append(audio_chunk)
        
        # Combine all audio chunks
        combined_audio = b''.join(audio_chunks)
        
        # Save to file
        with open(output_path, 'wb') as f:
            f.write(combined_audio)
        
        logger.info(f"Audio file saved to: {output_path}")
        return output_path
    
    def get_available_voices(self) -> List[Dict]:
        """
        Get list of available voices from Murf
        Note: This would require implementing the voices API endpoint
        """
        # Placeholder - in real implementation, you'd call Murf's voices API
        return [
            {"id": "en-US-amara", "name": "Amara", "language": "en-US", "style": "Conversational"},
            {"id": "en-US-jenny", "name": "Jenny", "language": "en-US", "style": "Professional"},
            {"id": "en-US-mike", "name": "Mike", "language": "en-US", "style": "Casual"},
            {"id": "en-IN-priya", "name": "Priya", "language": "en-IN", "style": "Friendly"},
            {"id": "en-GB-charles", "name": "Charles", "language": "en-GB", "style": "Formal"}
        ]

# Global instance
murf_tts_service = MurfTTSService()

