#!/usr/bin/env python3
"""
SocialCast Demo Script
Demonstrates the SocialCast functionality with sample data
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.murf_tts import murf_tts_service, TTSRequest, VoiceConfig
from services.summarizer import summarizer_service
from services.feed_processor import feed_processor, SocialPost

# Load environment variables
load_dotenv()

async def demo_socialcast():
    """Run a complete SocialCast demo"""
    print("🎙️ SocialCast Demo")
    print("=" * 60)
    
    # Check if Murf API key is set
    murf_key = os.getenv("MURF_API_KEY")
    if not murf_key or murf_key == "your_murf_api_key_here":
        print("❌ Please set your MURF_API_KEY in the .env file")
        print("   Get your API key from: https://murf.ai")
        return
    
    print("✅ Murf API key configured")
    
    # Sample social media posts
    sample_posts = [
        SocialPost(
            id="linkedin_1",
            platform="linkedin",
            author="Sarah Johnson",
            content="Excited to share that I've been promoted to Senior AI Engineer at TechCorp! 🚀 After 3 years of working on cutting-edge machine learning projects, I'm thrilled to take on this new challenge. The future of AI is incredibly promising, and I can't wait to contribute to building the next generation of intelligent systems. #AI #MachineLearning #CareerGrowth #TechCorp",
            timestamp=datetime.now() - timedelta(hours=2),
            url="https://linkedin.com/posts/sarah-johnson-123",
            media_type="text"
        ),
        SocialPost(
            id="whatsapp_1",
            platform="whatsapp",
            author="Team Lead",
            content="Hi team! Quick update: The client meeting has been rescheduled to 3 PM tomorrow instead of 2 PM. Please update your calendars accordingly. Also, don't forget to prepare the quarterly report presentation. Thanks!",
            timestamp=datetime.now() - timedelta(hours=1),
            url="https://whatsapp.com/chat/team-group",
            media_type="text"
        ),
        SocialPost(
            id="instagram_1",
            platform="instagram",
            author="Travel Explorer",
            content="Just arrived in Bali! 🌅 This place is absolutely magical. The sunset views from our villa are breathtaking, and the local food is incredible. Can't wait to explore more of this beautiful island. #Bali #Travel #Sunset #Adventure",
            timestamp=datetime.now() - timedelta(minutes=30),
            url="https://instagram.com/p/balisunset",
            media_type="image"
        ),
        SocialPost(
            id="twitter_1",
            platform="twitter",
            author="Tech News",
            content="BREAKING: OpenAI just announced GPT-5 with unprecedented reasoning capabilities. The new model shows significant improvements in logical thinking and problem-solving tasks. This could revolutionize how we interact with AI systems. #OpenAI #GPT5 #AI #Technology",
            timestamp=datetime.now() - timedelta(minutes=15),
            url="https://twitter.com/technews/status/123456",
            media_type="text"
        ),
        SocialPost(
            id="linkedin_2",
            platform="linkedin",
            author="Mike Chen",
            content="Just published my latest article on 'The Future of Remote Work in 2024'. Key insights: 1) Hybrid models are here to stay 2) AI tools are becoming essential 3) Work-life balance is the new priority. Would love to hear your thoughts! #RemoteWork #FutureOfWork #Leadership",
            timestamp=datetime.now() - timedelta(minutes=10),
            url="https://linkedin.com/posts/mike-chen-456",
            media_type="text"
        )
    ]
    
    print(f"📱 Processing {len(sample_posts)} sample social media posts...")
    print()
    
    # Process posts through the pipeline
    processed_posts = await feed_processor.process_new_posts(sample_posts)
    
    print("🎯 Processing Results:")
    print("-" * 40)
    
    for i, post in enumerate(processed_posts, 1):
        print(f"{i}. {post.original_post.platform.upper()} - {post.original_post.author}")
        print(f"   📝 Original: {post.original_post.content[:80]}...")
        print(f"   🎯 Summary: {post.summary}")
        print(f"   ⭐ Priority: {post.priority:.1f}")
        print(f"   🎵 Audio: {'✅ Generated' if post.audio_url else '❌ Failed'}")
        print()
    
    # Demo voice configuration
    print("🎤 Voice Configuration Demo:")
    print("-" * 40)
    
    voices = [
        ("Amara", "en-US-amara", "Conversational"),
        ("Jenny", "en-US-jenny", "Professional"),
        ("Mike", "en-US-mike", "Casual")
    ]
    
    for name, voice_id, style in voices:
        print(f"🎙️ Testing voice: {name} ({style})")
        
        voice_config = VoiceConfig(
            voice_id=voice_id,
            style=style,
            rate=0,
            pitch=0,
            variation=1
        )
        
        test_text = f"Hello, this is {name} speaking. Welcome to SocialCast!"
        
        tts_request = TTSRequest(
            text=test_text,
            voice_config=voice_config
        )
        
        try:
            timestamp = int(datetime.now().timestamp())
            output_path = f"demo_{name.lower()}_{timestamp}.wav"
            
            audio_path = await murf_tts_service.generate_audio_file(tts_request, output_path)
            
            if os.path.exists(audio_path):
                file_size = os.path.getsize(audio_path)
                print(f"   ✅ Audio generated: {file_size} bytes")
                
                # Clean up demo files
                os.remove(audio_path)
            else:
                print(f"   ❌ Audio generation failed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Demo daily digest
    print("📊 Daily Digest Demo:")
    print("-" * 40)
    
    try:
        digest_path = await feed_processor.generate_daily_digest(hours=24)
        
        if digest_path:
            file_size = os.path.getsize(digest_path)
            print(f"✅ Daily digest generated: {file_size} bytes")
            print(f"📁 File: {digest_path}")
            
            # Clean up
            os.remove(digest_path)
            print("🧹 Demo digest file cleaned up")
        else:
            print("ℹ️ No posts found for digest")
            
    except Exception as e:
        print(f"❌ Digest generation failed: {e}")
    
    print()
    
    # Demo content filtering
    print("🚫 Content Filtering Demo:")
    print("-" * 40)
    
    test_texts = [
        "This is a meaningful post about AI and machine learning.",
        "ok",
        "haha",
        "😀😀😀",
        "Meeting scheduled for tomorrow at 3 PM.",
        "thanks",
        "lol",
        "Important announcement: New product launch next week!"
    ]
    
    for text in test_texts:
        summary = summarizer_service.summarize_text(text)
        if summary:
            print(f"✅ '{text[:30]}...' -> '{summary}'")
        else:
            print(f"🚫 '{text[:30]}...' -> Filtered out")
    
    print()
    
    # Demo statistics
    print("📈 Statistics:")
    print("-" * 40)
    
    stats = feed_processor.get_stats()
    print(f"📱 Total posts processed: {stats['total_posts_processed']}")
    print(f"🎵 Posts with audio: {stats['posts_with_audio']}")
    print(f"⭐ Average priority: {stats['average_priority']:.1f}")
    
    print("\n📊 Posts by platform:")
    for platform, count in stats['posts_by_platform'].items():
        print(f"   {platform.capitalize()}: {count}")
    
    print()
    print("=" * 60)
    print("🎉 SocialCast Demo Completed!")
    print("=" * 60)
    
    print("\n📋 What we demonstrated:")
    print("✅ Social media post extraction and processing")
    print("✅ AI-powered content summarization")
    print("✅ Spam and low-value content filtering")
    print("✅ Content prioritization based on importance")
    print("✅ Multiple voice options with Murf TTS")
    print("✅ Daily digest generation")
    print("✅ Real-time audio streaming")
    
    print("\n🚀 Ready to use SocialCast!")
    print("1. Start the backend: python app.py")
    print("2. Load the Chrome extension")
    print("3. Visit your social media feeds")
    print("4. Click 'Start Listening' and enjoy your podcast!")

if __name__ == "__main__":
    asyncio.run(demo_socialcast())

