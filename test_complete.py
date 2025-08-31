#!/usr/bin/env python3
"""
Complete SocialCast Test - Tests all components working together
"""

import asyncio
import requests
import json
import time
from datetime import datetime

def test_backend_health():
    """Test backend health endpoint"""
    print("🏥 Testing backend health...")
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {data['status']}")
            print(f"   Services: {data['services']}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_stats_endpoint():
    """Test stats endpoint"""
    print("\n📊 Testing stats endpoint...")
    
    try:
        response = requests.get('http://localhost:8000/stats', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats retrieved successfully")
            print(f"   Total posts: {data['statistics'].get('total_posts_processed', 0)}")
            print(f"   Audio generated: {data['statistics'].get('posts_with_audio', 0)}")
            return True
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats endpoint error: {e}")
        return False

def test_post_processing():
    """Test post processing endpoint"""
    print("\n📝 Testing post processing...")
    
    test_posts = [
        {
            "platform": "linkedin",
            "author": "Test User",
            "content": "This is a test post about AI and machine learning. It contains useful information that should be processed and converted to audio.",
            "url": "https://linkedin.com/test",
            "media_type": "text"
        }
    ]
    
    try:
        response = requests.post(
            'http://localhost:8000/posts/process',
            json={"posts": test_posts},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Post processing successful")
            print(f"   Processed posts: {len(data.get('processed_posts', []))}")
            
            if data.get('processed_posts'):
                post = data['processed_posts'][0]
                print(f"   Summary: {post.get('summary', 'N/A')}")
                print(f"   Audio URL: {post.get('audio_url', 'N/A')}")
            
            return True
        else:
            print(f"❌ Post processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Post processing error: {e}")
        return False

def test_tts_generation():
    """Test TTS generation"""
    print("\n🎙️ Testing TTS generation...")
    
    test_text = "Hello, this is a test of the SocialCast text-to-speech system."
    
    try:
        response = requests.post(
            'http://localhost:8000/tts/generate',
            json={
                "text": test_text,
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
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ TTS generation error: {e}")
        return False

def test_daily_digest():
    """Test daily digest generation"""
    print("\n📅 Testing daily digest generation...")
    
    try:
        response = requests.post(
            'http://localhost:8000/digest/generate',
            json={"hours": 24},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Daily digest generation successful")
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Audio URL: {data.get('audio_url', 'N/A')}")
            return True
        else:
            print(f"❌ Daily digest generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Daily digest generation error: {e}")
        return False

def test_voice_config():
    """Test voice configuration update"""
    print("\n🎤 Testing voice configuration...")
    
    try:
        response = requests.put(
            'http://localhost:8000/voice/config',
            json={
                "voice_id": "en-US-jenny",
                "style": "Professional",
                "rate": 0,
                "pitch": 0,
                "variation": 1
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Voice configuration updated successfully")
            print(f"   Voice ID: {data['voice_config']['voice_id']}")
            print(f"   Style: {data['voice_config']['style']}")
            return True
        else:
            print(f"❌ Voice configuration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Voice configuration error: {e}")
        return False

def test_extension_files():
    """Test if extension files exist"""
    print("\n🔧 Testing extension files...")
    
    required_files = [
        'chrome-extension/manifest.json',
        'chrome-extension/background.js',
        'chrome-extension/content.js',
        'chrome-extension/popup.html',
        'chrome-extension/popup.js',
        'chrome-extension/package.json',
        'chrome-extension/icons/icon16.svg',
        'chrome-extension/icons/icon48.svg',
        'chrome-extension/icons/icon128.svg'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        try:
            with open(file_path, 'r') as f:
                print(f"✅ {file_path}")
        except FileNotFoundError:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} files")
        return False
    else:
        print(f"\n✅ All extension files present")
        return True

def main():
    """Run all tests"""
    print("🧪 SocialCast Complete Test Suite")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Stats Endpoint", test_stats_endpoint),
        ("Post Processing", test_post_processing),
        ("TTS Generation", test_tts_generation),
        ("Daily Digest", test_daily_digest),
        ("Voice Configuration", test_voice_config),
        ("Extension Files", test_extension_files)
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
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! SocialCast is ready to use!")
        print("\n📋 Next steps:")
        print("1. Load the extension in Chrome (chrome://extensions/)")
        print("2. Visit a social media site")
        print("3. Click the SocialCast extension icon")
        print("4. Click 'Start Listening' to begin!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
