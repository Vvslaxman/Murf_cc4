#!/usr/bin/env python3
"""
Add sample posts to test SocialCast functionality
"""

import requests
import json
from datetime import datetime

def add_sample_posts():
    """Add sample posts to test the system"""
    
    sample_posts = [
        {
            "platform": "linkedin",
            "author": "John Doe",
            "content": "Just published a new article about AI in healthcare. The potential for machine learning to improve patient outcomes is incredible. Check out the full research here!",
            "url": "https://linkedin.com/posts/johndoe",
            "media_type": "text"
        },
        {
            "platform": "twitter",
            "author": "Jane Smith",
            "content": "Excited to announce that our startup just secured $2M in funding! This will help us scale our AI-powered productivity tools. Thanks to all our supporters! 🚀",
            "url": "https://twitter.com/janesmith",
            "media_type": "text"
        },
        {
            "platform": "instagram",
            "author": "Tech Guru",
            "content": "Working on some amazing new features for our app. The team has been putting in long hours and the results are showing. Can't wait to share more details soon!",
            "url": "https://instagram.com/techguru",
            "media_type": "text"
        },
        {
            "platform": "whatsapp",
            "author": "Team Lead",
            "content": "Meeting reminder: Tomorrow at 3 PM we'll be discussing the Q4 roadmap. Please prepare your updates and come ready to share your insights.",
            "url": "https://whatsapp.com/group",
            "media_type": "text"
        }
    ]
    
    try:
        print("📝 Adding sample posts...")
        
        response = requests.post(
            'http://localhost:8000/posts/process',
            json={"posts": sample_posts},
            timeout=60  # Increased timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully added {len(data.get('processed_posts', []))} posts")
            
            for i, post in enumerate(data.get('processed_posts', []), 1):
                print(f"   Post {i}: {post.get('summary', 'N/A')}")
            
            return True
        else:
            print(f"❌ Failed to add posts: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error adding posts: {e}")
        return False

def test_digest():
    """Test the daily digest functionality"""
    
    try:
        print("\n📅 Testing daily digest...")
        
        response = requests.post(
            'http://localhost:8000/digest/generate',
            json={"hours": 24},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Digest test successful")
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Posts count: {data.get('posts_count', 0)}")
            print(f"   Audio URL: {data.get('audio_url', 'N/A')}")
            return True
        else:
            print(f"❌ Digest test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing digest: {e}")
        return False

def main():
    """Main function"""
    print("🧪 SocialCast Sample Posts Test")
    print("=" * 40)
    
    # Add sample posts
    if add_sample_posts():
        print("\n✅ Sample posts added successfully!")
        
        # Test digest
        test_digest()
        
        print("\n🎯 Now you can:")
        print("1. Test the Chrome extension")
        print("2. Generate daily digests")
        print("3. See posts in the statistics")
    else:
        print("\n❌ Failed to add sample posts")

if __name__ == "__main__":
    main()
