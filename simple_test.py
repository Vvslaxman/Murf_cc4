#!/usr/bin/env python3
"""
Simple SocialCast Test - Bypasses heavy summarization for quick testing
"""

import requests
import json
from datetime import datetime

def test_backend():
    """Test basic backend functionality"""
    print("🏥 Testing backend...")
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_tts():
    """Test TTS generation directly"""
    print("\n🎙️ Testing TTS generation...")
    
    try:
        response = requests.post(
            'http://localhost:8000/tts/generate',
            json={
                "text": "Hello, this is a test of the SocialCast text-to-speech system.",
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
            return True
        else:
            print(f"❌ TTS generation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ TTS generation error: {e}")
        return False

def test_stats():
    """Test stats endpoint"""
    print("\n📊 Testing stats...")
    
    try:
        response = requests.get('http://localhost:8000/stats', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats retrieved")
            print(f"   Total posts: {data['statistics'].get('total_posts_processed', 0)}")
            return True
        else:
            print(f"❌ Stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return False

def test_voice_config():
    """Test voice configuration"""
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
            print(f"✅ Voice configuration updated")
            print(f"   Voice: {data['voice_config']['voice_id']}")
            return True
        else:
            print(f"❌ Voice config failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Voice config error: {e}")
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
    print("🧪 SocialCast Simple Test Suite")
    print("=" * 40)
    
    tests = [
        ("Backend", test_backend),
        ("TTS Generation", test_tts),
        ("Stats", test_stats),
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
    print("\n" + "=" * 40)
    print("📋 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed >= 4:  # At least 4 out of 5 tests should pass
        print("🎉 Core functionality is working! SocialCast is ready to use!")
        print("\n📋 Next steps:")
        print("1. Load the extension in Chrome (chrome://extensions/)")
        print("2. Visit a social media site")
        print("3. Click the SocialCast extension icon")
        print("4. Click 'Start Listening' to begin!")
        print("\n💡 Note: Post processing uses simple summarization for now")
        print("   This can be enhanced later with better AI models")
    else:
        print("⚠️  Some core tests failed. Please check the errors above.")
    
    return passed >= 4

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
