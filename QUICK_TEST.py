#!/usr/bin/env python3
"""
Quick test for SocialCast Final Working Version
"""

import requests
import json

def test_endpoints():
    """Test all endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing SocialCast Final Working Version")
    print("=" * 50)
    
    # Test health
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data.get('status', 'unknown')}")
            print(f"   Murf API: {data.get('murf_api', 'unknown')}")
        else:
            print(f"❌ Health failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health error: {e}")
    
    # Test stats
    try:
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            stats = data.get('statistics', {})
            print(f"✅ Stats: {stats.get('total_posts', 0)} posts, {stats.get('total_audio_generated', 0)} audio")
        else:
            print(f"❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats error: {e}")
    
    # Test voices
    try:
        response = requests.get(f"{base_url}/voices", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Voices: {data.get('count', 0)} available")
        else:
            print(f"❌ Voices failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Voices error: {e}")
    
    # Test TTS generation
    try:
        response = requests.post(
            f"{base_url}/tts/generate",
            json={
                "text": "Hello, this is a test of SocialCast TTS!",
                "voice_config": {"voice_id": "en-US-amara"}
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ TTS: Generated audio file")
            print(f"   Audio: {data.get('audio_url', 'N/A')}")
        else:
            print(f"❌ TTS failed: {response.status_code}")
    except Exception as e:
        print(f"❌ TTS error: {e}")
    
    # Test post processing
    try:
        response = requests.post(
            f"{base_url}/posts/process",
            json=[{
                "platform": "linkedin",
                "author": "Test User",
                "content": "This is a test post for SocialCast!"
            }],
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Posts: Processed {len(data.get('processed_posts', []))} posts")
        else:
            print(f"❌ Posts failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Posts error: {e}")
    
    # Test digest generation
    try:
        response = requests.post(
            f"{base_url}/digest/generate",
            json={"hours": 24},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Digest: {data.get('message', 'Generated')}")
        else:
            print(f"❌ Digest failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Digest error: {e}")
    
    # Test voice config
    try:
        response = requests.put(
            f"{base_url}/voice/config",
            json={
                "voice_id": "en-US-jenny",
                "style": "Professional"
            },
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Voice Config: Updated successfully")
        else:
            print(f"❌ Voice Config failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Voice Config error: {e}")
    
    print("=" * 50)
    print("🎉 All tests completed!")
    print("🚀 Your Chrome extension should now work perfectly!")

if __name__ == "__main__":
    test_endpoints()
