"""
SocialCast Backend - FastAPI application for social media podcast generation
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

from services.murf_tts import murf_tts_service, VoiceConfig, TTSRequest
from services.summarizer import summarizer_service
from services.feed_processor import feed_processor, SocialPost, ProcessedPost

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SocialCast API",
    description="Turn your social feeds into a narrated podcast using Murf TTS",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class PostRequest(BaseModel):
    platform: str
    author: str
    content: str
    url: Optional[str] = None
    media_type: Optional[str] = None

class VoiceConfigRequest(BaseModel):
    voice_id: str = "en-US-amara"
    style: str = "Conversational"
    rate: int = Field(ge=-10, le=10, default=0)
    pitch: int = Field(ge=-10, le=10, default=0)
    variation: int = Field(ge=1, le=10, default=1)

class TTSRequestModel(BaseModel):
    text: str
    voice_config: Optional[VoiceConfigRequest] = None

class ProcessPostsRequest(BaseModel):
    posts: List[PostRequest]

class DigestRequest(BaseModel):
    hours: int = Field(ge=1, le=168, default=24)  # 1 hour to 1 week

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting SocialCast backend...")
    
    # Ensure temp directories exist
    os.makedirs("temp_audio", exist_ok=True)
    
    logger.info("SocialCast backend started successfully!")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "SocialCast API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "murf_tts": "available",
            "summarizer": "available",
            "feed_processor": "available"
        }
    }

@app.post("/posts/process")
async def process_posts(request: ProcessPostsRequest) -> Dict[str, Any]:
    """Process new social media posts"""
    try:
        # Convert to SocialPost objects
        posts = []
        for post_data in request.posts:
            post = SocialPost(
                id=f"{post_data.platform}_{int(datetime.now().timestamp())}_{len(posts)}",
                platform=post_data.platform,
                author=post_data.author,
                content=post_data.content,
                timestamp=datetime.now(),
                url=post_data.url,
                media_type=post_data.media_type
            )
            posts.append(post)
        
        # Process posts
        processed_posts = await feed_processor.process_new_posts(posts)
        
        return {
            "message": f"Successfully processed {len(processed_posts)} posts",
            "processed_posts": [
                {
                    "id": post.original_post.id,
                    "platform": post.original_post.platform,
                    "author": post.original_post.author,
                    "summary": post.summary,
                    "priority": post.priority,
                    "audio_url": post.audio_url,
                    "duration": post.duration
                }
                for post in processed_posts
            ]
        }
    
    except Exception as e:
        logger.error(f"Error processing posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts/generate")
async def generate_tts(request: TTSRequestModel) -> Dict[str, Any]:
    """Generate TTS audio for text"""
    try:
        # Use provided voice config or default
        voice_config = VoiceConfig()
        if request.voice_config:
            voice_config = VoiceConfig(
                voice_id=request.voice_config.voice_id,
                style=request.voice_config.style,
                rate=request.voice_config.rate,
                pitch=request.voice_config.pitch,
                variation=request.voice_config.variation
            )
        
        # Create TTS request
        tts_request = TTSRequest(
            text=request.text,
            voice_config=voice_config
        )
        
        # Generate audio file
        timestamp = int(datetime.now().timestamp())
        output_path = f"temp_audio/tts_{timestamp}.wav"
        
        audio_path = await murf_tts_service.generate_audio_file(tts_request, output_path)
        
        return {
            "message": "TTS audio generated successfully",
            "audio_url": audio_path,
            "text_length": len(request.text)
        }
    
    except Exception as e:
        logger.error(f"Error generating TTS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tts/stream/{text:path}")
async def stream_tts(text: str, voice_id: str = "en-US-amara"):
    """Stream TTS audio for text"""
    try:
        # URL decode the text
        import urllib.parse
        decoded_text = urllib.parse.unquote(text)
        
        # Create TTS request
        voice_config = VoiceConfig(voice_id=voice_id)
        tts_request = TTSRequest(text=decoded_text, voice_config=voice_config)
        
        # Stream audio
        async def audio_generator():
            async for audio_chunk in murf_tts_service.stream_audio(tts_request):
                yield audio_chunk
        
        return StreamingResponse(
            audio_generator(),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=audio.wav"}
        )
    
    except Exception as e:
        logger.error(f"Error streaming TTS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """Serve audio files"""
    file_path = f"temp_audio/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(file_path, media_type="audio/wav")

@app.post("/digest/generate")
async def generate_daily_digest(request: DigestRequest) -> Dict[str, Any]:
    """Generate daily digest audio"""
    try:
        audio_path = await feed_processor.generate_daily_digest(request.hours)
        
        if not audio_path or audio_path == "no_posts":
            return {
                "message": "No posts found for digest",
                "audio_url": None,
                "posts_count": 0
            }
        
        return {
            "message": f"Daily digest generated for last {request.hours} hours",
            "audio_url": audio_path,
            "posts_count": len(feed_processor.get_daily_digest_posts(request.hours))
        }
    
    except Exception as e:
        logger.error(f"Error generating digest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voices")
async def get_available_voices() -> Dict[str, Any]:
    """Get available Murf voices"""
    try:
        voices = murf_tts_service.get_available_voices()
        return {
            "voices": voices,
            "count": len(voices)
        }
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/voice/config")
async def update_voice_config(request: VoiceConfigRequest):
    """Update voice configuration"""
    try:
        voice_config = VoiceConfig(
            voice_id=request.voice_id,
            style=request.style,
            rate=request.rate,
            pitch=request.pitch,
            variation=request.variation
        )
        
        feed_processor.update_voice_config(voice_config)
        
        return {
            "message": "Voice configuration updated successfully",
            "voice_config": {
                "voice_id": voice_config.voice_id,
                "style": voice_config.style,
                "rate": voice_config.rate,
                "pitch": voice_config.pitch,
                "variation": voice_config.variation
            }
        }
    
    except Exception as e:
        logger.error(f"Error updating voice config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """Get processing statistics"""
    try:
        stats = feed_processor.get_stats()
        return {
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            
            # Parse the message
            try:
                import json
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "tts_request":
                    # Handle TTS request
                    text = message.get("text", "")
                    voice_id = message.get("voice_id", "en-US-amara")
                    
                    voice_config = VoiceConfig(voice_id=voice_id)
                    tts_request = TTSRequest(text=text, voice_config=voice_config)
                    
                    # Stream audio back
                    async for audio_chunk in murf_tts_service.stream_audio(tts_request):
                        await websocket.send_bytes(audio_chunk)
                
                elif message_type == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("BACKEND_HOST", "localhost")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    # Start the server
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )

