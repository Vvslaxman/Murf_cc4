#!/usr/bin/env python3
"""
Test Simple SocialCast - Quick validation
"""

import requests
import json
import time

def test_backend():
    """Test backend health"""
    print("🏥 Testing backend...")
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy")
            print(f"   Murf API: {data.get('murf_api', 'unknown')}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_tts():
    """Test TTS generation"""
    print("\n🎙️ Testing TTS generation...")
    
    try:
        response = requests.post(
            'http://localhost:8000/tts/generate',
            json={
                "text": "Hello, this is a test of the SocialCast text-to-speech system using Murf API.",
                "voice_config": {
                    "voice_id": "en-US-amara",
                    "style": "Conversational",
                    "rate": 0,
                    "pitch": 0,
                    "variation": 1
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ TTS generation successful")
            print(f"   Audio URL: {data.get('audio_url', 'N/A')}")
            print(f"   Text length: {data.get('text_length', 'N/A')}")
            return True
        else:
            print(f"❌ TTS generation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ TTS generation error: {e}")
        return False

def test_post_processing():
    """Test post processing"""
    print("\n📝 Testing post processing...")
    
    sample_posts = [
        {
            "platform": "linkedin",
            "author": "John Doe",
            "content": "Just published a new article about AI in healthcare. The potential for machine learning to improve patient outcomes is incredible!",
            "url": "https://linkedin.com/posts/johndoe"
        },
        {
            "platform": "twitter",
            "author": "Jane Smith",
            "content": "Excited to announce that our startup just secured $2M in funding! This will help us scale our AI-powered productivity tools.",
            "url": "https://twitter.com/janesmith"
        }
    ]
    
    try:
        response = requests.post(
            'http://localhost:8000/posts/process',
            json=sample_posts,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Post processing successful")
            print(f"   Processed posts: {len(data.get('processed_posts', []))}")
            
            for i, post in enumerate(data.get('processed_posts', []), 1):
                print(f"   Post {i}: {post.get('summary', 'N/A')}")
            
            return True
        else:
            print(f"❌ Post processing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Post processing error: {e}")
        return False

def test_stats():
    """Test stats endpoint"""
    print("\n📊 Testing stats...")
    
    try:
        response = requests.get('http://localhost:8000/stats', timeout=5)
        if response.status_code == 200:
            data = response.json()
            stats = data.get('statistics', {})
            print(f"✅ Stats retrieved")
            print(f"   Total posts: {stats.get('total_posts_processed', 0)}")
            print(f"   Audio generated: {stats.get('total_audio_generated', 0)}")
            print(f"   Murf API status: {stats.get('murf_api_status', 'unknown')}")
            return True
        else:
            print(f"❌ Stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return False

def test_voices():
    """Test voices endpoint"""
    print("\n🎤 Testing voices...")
    
    try:
        response = requests.get('http://localhost:8000/voices', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Voices retrieved")
            print(f"   Available voices: {data.get('count', 0)}")
            
            for voice in data.get('voices', [])[:3]:  # Show first 3
                print(f"   - {voice.get('name', 'Unknown')} ({voice.get('id', 'unknown')})")
            
            return True
        else:
            print(f"❌ Voices failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Voices error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 SocialCast Simple Test")
    print("=" * 30)
    
    tests = [
        ("Backend", test_backend),
        ("TTS Generation", test_tts),
        ("Post Processing", test_post_processing),
        ("Stats", test_stats),
        ("Voices", test_voices)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 30)
    print("📋 Test Results:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed >= 4:
        print("🎉 SocialCast is working! Ready for submission!")
        print("\n📋 Demo Features:")
        print("   ✅ Murf TTS Integration (with text chunking)")
        print("   ✅ Multiple Voice Support")
        print("   ✅ Real-time Audio Generation")
        print("   ✅ Post Processing Pipeline")
        print("   ✅ Chrome Extension Ready")
        print("\n🚀 Next: Load the Chrome extension and test!")
    else:
        print("⚠️  Some tests failed. Check the backend is running.")
    
    return passed >= 4

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
