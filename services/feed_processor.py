"""
Feed Processor Service - Handles social media content extraction and processing
"""

import asyncio
import json
import time
from typing import List, Dict, Optional, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from .summarizer import summarizer_service
from .murf_tts import murf_tts_service, TTSRequest, VoiceConfig

logger = logging.getLogger(__name__)

@dataclass
class SocialPost:
    """Represents a social media post"""
    id: str
    platform: str
    author: str
    content: str
    timestamp: datetime
    url: Optional[str] = None
    media_type: Optional[str] = None  # text, image, video, link
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ProcessedPost:
    """Represents a processed post ready for TTS"""
    original_post: SocialPost
    summary: str
    priority: float
    audio_url: Optional[str] = None
    duration: Optional[float] = None

class FeedProcessor:
    """Main feed processing service"""
    
    def __init__(self):
        self.processed_posts: List[ProcessedPost] = []
        self.post_cache: Dict[str, SocialPost] = {}
        self.voice_config = VoiceConfig()
        self.context_id = f"socialcast_{int(time.time())}"
    
    async def process_new_posts(self, posts: List[SocialPost]) -> List[ProcessedPost]:
        """
        Process new social media posts through the pipeline:
        1. Filter and summarize
        2. Prioritize content
        3. Generate TTS audio
        """
        logger.info(f"Processing {len(posts)} new posts")
        
        # Filter out already processed posts
        new_posts = [post for post in posts if post.id not in self.post_cache]
        
        if not new_posts:
            logger.info("No new posts to process")
            return []
        
        # Add to cache
        for post in new_posts:
            self.post_cache[post.id] = post
        
        # Summarize and prioritize content
        prioritized_content = summarizer_service.prioritize_content(
            [post.content for post in new_posts]
        )
        
        # Create processed posts
        processed_posts = []
        for i, content_data in enumerate(prioritized_content):
            original_post = new_posts[i]
            
            processed_post = ProcessedPost(
                original_post=original_post,
                summary=content_data["summary"],
                priority=content_data["priority"]
            )
            
            processed_posts.append(processed_post)
        
        # Generate TTS for each processed post
        for processed_post in processed_posts:
            await self._generate_audio(processed_post)
        
        # Add to processed posts list
        self.processed_posts.extend(processed_posts)
        
        logger.info(f"Successfully processed {len(processed_posts)} posts")
        return processed_posts
    
    async def _generate_audio(self, processed_post: ProcessedPost):
        """Generate TTS audio for a processed post"""
        try:
            # Create TTS request
            tts_request = TTSRequest(
                text=processed_post.summary,
                voice_config=self.voice_config,
                context_id=self.context_id
            )
            
            # Generate audio file
            timestamp = int(time.time())
            filename = f"audio_{processed_post.original_post.id}_{timestamp}.wav"
            output_path = f"temp_audio/{filename}"
            
            # Ensure temp directory exists
            import os
            os.makedirs("temp_audio", exist_ok=True)
            
            audio_path = await murf_tts_service.generate_audio_file(tts_request, output_path)
            
            # Update processed post with audio info
            processed_post.audio_url = audio_path
            # Estimate duration (rough calculation: ~150 words per minute)
            word_count = len(processed_post.summary.split())
            processed_post.duration = (word_count / 150) * 60  # seconds
            
            logger.info(f"Generated audio for post {processed_post.original_post.id}")
            
        except Exception as e:
            logger.error(f"Failed to generate audio for post {processed_post.original_post.id}: {e}")
    
    async def stream_audio_playlist(self, posts: List[ProcessedPost]) -> AsyncGenerator[bytes, None]:
        """
        Stream audio for multiple posts as a playlist
        """
        for post in posts:
            if post.audio_url:
                try:
                    # Read and yield audio file
                    with open(post.audio_url, 'rb') as f:
                        audio_data = f.read()
                        yield audio_data
                    
                    # Small pause between posts
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Failed to stream audio for post {post.original_post.id}: {e}")
    
    def get_daily_digest_posts(self, hours: int = 24) -> List[ProcessedPost]:
        """
        Get posts from the last N hours for daily digest
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        digest_posts = [
            post for post in self.processed_posts
            if post.original_post.timestamp >= cutoff_time
        ]
        
        # Sort by priority
        digest_posts.sort(key=lambda x: x.priority, reverse=True)
        
        return digest_posts
    
    async def generate_daily_digest(self, hours: int = 24) -> Optional[str]:
        """
        Generate a daily digest audio file
        """
        digest_posts = self.get_daily_digest_posts(hours)
        
        if not digest_posts:
            logger.info("No posts found for daily digest")
            return None
        
        # Create digest text
        digest_text = self._create_digest_text(digest_posts)
        
        # Generate audio
        tts_request = TTSRequest(
            text=digest_text,
            voice_config=self.voice_config,
            context_id=f"digest_{self.context_id}"
        )
        
        timestamp = int(time.time())
        output_path = f"temp_audio/daily_digest_{timestamp}.wav"
        
        # Ensure temp directory exists
        import os
        os.makedirs("temp_audio", exist_ok=True)
        
        audio_path = await murf_tts_service.generate_audio_file(tts_request, output_path)
        
        logger.info(f"Generated daily digest: {audio_path}")
        return audio_path
    
    def _create_digest_text(self, posts: List[ProcessedPost]) -> str:
        """Create digest text from multiple posts"""
        if not posts:
            return ""
        
        digest_lines = [f"Here's your {len(posts)}-post social media digest:"]
        
        for i, post in enumerate(posts, 1):
            platform = post.original_post.platform
            author = post.original_post.author
            summary = post.summary
            
            digest_lines.append(f"Post {i} from {author} on {platform}: {summary}")
        
        digest_lines.append("That concludes your social media digest. Thanks for listening!")
        
        return " ".join(digest_lines)
    
    def update_voice_config(self, voice_config: VoiceConfig):
        """Update the voice configuration"""
        self.voice_config = voice_config
        logger.info(f"Updated voice config: {voice_config}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        total_posts = len(self.processed_posts)
        platforms = {}
        
        for post in self.processed_posts:
            platform = post.original_post.platform
            platforms[platform] = platforms.get(platform, 0) + 1
        
        return {
            "total_posts_processed": total_posts,
            "posts_by_platform": platforms,
            "average_priority": sum(p.priority for p in self.processed_posts) / total_posts if total_posts > 0 else 0,
            "posts_with_audio": len([p for p in self.processed_posts if p.audio_url])
        }

# Global instance
feed_processor = FeedProcessor()

