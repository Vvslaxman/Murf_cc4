#!/usr/bin/env python3
"""
SocialCast Test Script
Tests the backend functionality and Murf TTS integration
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.murf_tts import murf_tts_service, TTSRequest, VoiceConfig
from services.summarizer import summarizer_service
from services.feed_processor import feed_processor, SocialPost

# Load environment variables
load_dotenv()

async def test_murf_tts():
    """Test Murf TTS functionality"""
    print("🧪 Testing Murf TTS...")
    
    try:
        # Test text chunking
        long_text = """
        This is a very long text that exceeds the 3000 character limit for Murf TTS. 
        It contains multiple sentences and should be automatically chunked into smaller pieces.
        The chunking algorithm should try to break at sentence boundaries when possible.
        This ensures that the text is processed correctly and efficiently by the Murf API.
        """ * 50  # Make it very long
        
        chunks = murf_tts_service.chunk_text(long_text)
        print(f"✅ Text chunking: {len(chunks)} chunks created")
        
        # Test TTS with short text
        short_text = "Hello, this is a test of the SocialCast TTS system."
        
        voice_config = VoiceConfig(
            voice_id="en-US-amara",
            style="Conversational",
            rate=0,
            pitch=0,
            variation=1
        )
        
        tts_request = TTSRequest(
            text=short_text,
            voice_config=voice_config
        )
        
        print("🎙️ Generating test audio...")
        
        # Generate audio file
        timestamp = int(datetime.now().timestamp())
        output_path = f"test_audio_{timestamp}.wav"
        
        audio_path = await murf_tts_service.generate_audio_file(tts_request, output_path)
        
        if os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path)
            print(f"✅ TTS audio generated: {audio_path} ({file_size} bytes)")
            
            # Clean up test file
            os.remove(audio_path)
            print("🧹 Test audio file cleaned up")
        else:
            print("❌ TTS audio file not found")
            
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False
    
    return True

async def test_summarizer():
    """Test summarization functionality"""
    print("\n🧪 Testing Summarizer...")
    
    try:
        # Test content filtering
        test_texts = [
            "This is a meaningful post about AI and machine learning.",
            "ok",
            "haha",
            "😀😀😀",
            "This is another important post with useful information.",
            "thanks",
            "Meeting scheduled for tomorrow at 3 PM.",
            "lol"
        ]
        
        print("📝 Testing content filtering...")
        for text in test_texts:
            summary = summarizer_service.summarize_text(text)
            if summary:
                print(f"✅ '{text[:30]}...' -> '{summary}'")
            else:
                print(f"🚫 '{text[:30]}...' -> Filtered out")
        
        # Test prioritization
        print("\n📊 Testing content prioritization...")
        prioritized = summarizer_service.prioritize_content(test_texts)
        
        for i, item in enumerate(prioritized[:3], 1):
            print(f"{i}. Priority {item['priority']:.1f}: '{item['summary']}'")
            
    except Exception as e:
        print(f"❌ Summarizer test failed: {e}")
        return False
    
    return True

async def test_feed_processor():
    """Test feed processing functionality"""
    print("\n🧪 Testing Feed Processor...")
    
    try:
        # Create test posts
        test_posts = [
            SocialPost(
                id="test_1",
                platform="linkedin",
                author="John Doe",
                content="Excited to share that I've joined a new AI startup! The future of technology looks promising.",
                timestamp=datetime.now(),
                url="https://linkedin.com/post/1",
                media_type="text"
            ),
            SocialPost(
                id="test_2", 
                platform="whatsapp",
                author="Jane Smith",
                content="Meeting moved to 3 PM tomorrow. Please update your calendars.",
                timestamp=datetime.now(),
                url="https://whatsapp.com/chat/1",
                media_type="text"
            ),
            SocialPost(
                id="test_3",
                platform="instagram", 
                author="Traveler",
                content="Amazing sunset in Bali! 🌅 This place is absolutely breathtaking.",
                timestamp=datetime.now(),
                url="https://instagram.com/post/1",
                media_type="image"
            )
        ]
        
        print("📱 Processing test posts...")
        processed_posts = await feed_processor.process_new_posts(test_posts)
        
        print(f"✅ Processed {len(processed_posts)} posts")
        
        for i, post in enumerate(processed_posts, 1):
            print(f"{i}. {post.original_post.platform} - {post.original_post.author}")
            print(f"   Summary: {post.summary}")
            print(f"   Priority: {post.priority:.1f}")
            print(f"   Audio: {'✅' if post.audio_url else '❌'}")
            print()
        
        # Test daily digest
        print("📊 Testing daily digest...")
        digest_path = await feed_processor.generate_daily_digest(hours=24)
        
        if digest_path:
            print(f"✅ Daily digest generated: {digest_path}")
            # Clean up
            if os.path.exists(digest_path):
                os.remove(digest_path)
                print("🧹 Digest file cleaned up")
        else:
            print("ℹ️ No posts found for digest")
            
    except Exception as e:
        print(f"❌ Feed processor test failed: {e}")
        return False
    
    return True

async def test_backend_api():
    """Test backend API endpoints"""
    print("\n🧪 Testing Backend API...")
    
    try:
        import requests
        
        base_url = "http://localhost:8000"
        
        # Test health endpoint
        print("🏥 Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend healthy: {health_data}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
        
        # Test TTS endpoint
        print("🎙️ Testing TTS endpoint...")
        tts_data = {
            "text": "This is a test of the SocialCast TTS API endpoint.",
            "voice_config": {
                "voice_id": "en-US-amara",
                "style": "Conversational",
                "rate": 0,
                "pitch": 0,
                "variation": 1
            }
        }
        
        response = requests.post(f"{base_url}/tts/generate", json=tts_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ TTS API working: {result['message']}")
        else:
            print(f"❌ TTS API failed: {response.status_code}")
            return False
        
        # Test voices endpoint
        print("🎤 Testing voices endpoint...")
        response = requests.get(f"{base_url}/voices", timeout=5)
        
        if response.status_code == 200:
            voices_data = response.json()
            print(f"✅ Voices API working: {voices_data['count']} voices available")
        else:
            print(f"❌ Voices API failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend not running. Please start the backend server first.")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("🚀 SocialCast Test Suite")
    print("=" * 50)
    
    # Check environment
    print("🔧 Checking environment...")
    murf_key = os.getenv("MURF_API_KEY")
    if not murf_key or murf_key == "your_murf_api_key_here":
        print("❌ MURF_API_KEY not set. Please set it in your .env file.")
        return
    
    print("✅ Environment variables loaded")
    
    # Run tests
    tests = [
        ("Murf TTS", test_murf_tts),
        ("Summarizer", test_summarizer), 
        ("Feed Processor", test_feed_processor),
        ("Backend API", test_backend_api)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! SocialCast is ready to use.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())

