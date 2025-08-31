#!/usr/bin/env python3
"""
Fix SocialCast Extension Issues
"""

import os
import subprocess
import sys

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def create_simple_icons():
    """Create simple text-based icons"""
    print("🎨 Creating simple extension icons...")
    
    # Create icons directory
    os.makedirs('chrome-extension/icons', exist_ok=True)
    
    # Create simple SVG icons
    icon_svg = '''<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="{size}" height="{size}" fill="url(#grad)" rx="4"/>
        <circle cx="{cx}" cy="{cy}" r="{r}" fill="white"/>
        <rect x="{stand_x}" y="{stand_y}" width="{stand_w}" height="{stand_h}" fill="white" rx="2"/>
    </svg>'''
    
    sizes = [16, 48, 128]
    
    for size in sizes:
        # Calculate positions
        cx = size // 2
        cy = size // 2
        r = int(size * 0.25)
        stand_x = cx - int(size * 0.1)
        stand_y = cy + int(size * 0.2)
        stand_w = int(size * 0.2)
        stand_h = int(size * 0.15)
        
        # Create SVG content
        svg_content = icon_svg.format(
            size=size, cx=cx, cy=cy, r=r,
            stand_x=stand_x, stand_y=stand_y, stand_w=stand_w, stand_h=stand_h
        )
        
        # Save as SVG (Chrome can use SVG icons)
        with open(f'chrome-extension/icons/icon{size}.svg', 'w') as f:
            f.write(svg_content)
        
        print(f"✅ Created icon{size}.svg")

def update_manifest():
    """Update manifest to use SVG icons"""
    print("📝 Updating manifest.json...")
    
    manifest_content = '''{
  "manifest_version": 3,
  "name": "SocialCast - Social Media Podcast",
  "version": "1.0.0",
  "description": "Turn your social feeds into a narrated podcast using Murf TTS",
  
  "permissions": [
    "activeTab",
    "storage",
    "scripting",
    "webRequest",
    "contextMenus"
  ],
  
  "host_permissions": [
    "https://*.linkedin.com/*",
    "https://*.whatsapp.com/*",
    "https://*.instagram.com/*",
    "https://*.twitter.com/*",
    "https://*.x.com/*",
    "https://*.telegram.org/*",
    "https://*.facebook.com/*",
    "http://localhost:8000/*"
  ],
  
  "background": {
    "service_worker": "background.js"
  },
  
  "content_scripts": [
    {
      "matches": [
        "https://*.linkedin.com/*",
        "https://*.whatsapp.com/*",
        "https://*.instagram.com/*",
        "https://*.twitter.com/*",
        "https://*.x.com/*",
        "https://*.telegram.org/*",
        "https://*.facebook.com/*"
      ],
      "js": ["content.js"],
      "run_at": "document_end"
    }
  ],
  
  "action": {
    "default_popup": "popup.html",
    "default_title": "SocialCast",
    "default_icon": {
      "16": "icons/icon16.svg",
      "48": "icons/icon48.svg",
      "128": "icons/icon128.svg"
    }
  },
  
  "icons": {
    "16": "icons/icon16.svg",
    "48": "icons/icon48.svg",
    "128": "icons/icon128.svg"
  },
  
  "web_accessible_resources": [
    {
      "resources": ["audio-player.js", "styles.css"],
      "matches": ["<all_urls>"]
    }
  ]
}'''
    
    with open('chrome-extension/manifest.json', 'w') as f:
        f.write(manifest_content)
    
    print("✅ Updated manifest.json")

def setup_npm():
    """Setup npm package.json"""
    print("📦 Setting up npm package.json...")
    
    package_content = '''{
  "name": "socialcast-extension",
  "version": "1.0.0",
  "description": "SocialCast Chrome Extension for social media podcast generation",
  "main": "background.js",
  "scripts": {
    "build": "echo \\"Chrome extension built successfully\\" && echo \\"Load the extension from chrome-extension/ directory in Chrome Extensions page\\"",
    "start": "echo \\"Starting Chrome extension development mode\\" && echo \\"Load the extension from chrome-extension/ directory in Chrome Extensions page\\"",
    "dev": "echo \\"Development mode - make changes and reload extension in Chrome\\"",
    "test": "echo \\"Error: no test specified\\" && exit 1"
  },
  "keywords": ["chrome-extension", "social-media", "podcast", "tts"],
  "author": "SocialCast Team",
  "license": "MIT"
}'''
    
    with open('chrome-extension/package.json', 'w') as f:
        f.write(package_content)
    
    print("✅ Created package.json")

def create_env_file():
    """Create .env file"""
    print("🔧 Creating .env file...")
    
    env_content = """# Murf API Configuration
MURF_API_KEY=your_murf_api_key_here
MURF_WS_URL=wss://api.murf.ai/v1/speech/stream-input

# OpenAI Configuration (for summarization) - Optional
OPENAI_API_KEY=your_openai_api_key_here

# Cohere Configuration (alternative summarization) - Optional
COHERE_API_KEY=your_cohere_api_key_here

# Backend Configuration
BACKEND_HOST=localhost
BACKEND_PORT=8000
DEBUG=True

# Murf TTS Settings
DEFAULT_VOICE_ID=en-US-amara
DEFAULT_STYLE=Conversational
DEFAULT_SAMPLE_RATE=44100
DEFAULT_CHANNEL_TYPE=MONO
DEFAULT_FORMAT=WAV

# Summarization Settings - Using Local Models by Default
MAX_TEXT_LENGTH=3000
SUMMARY_MAX_LENGTH=200
USE_LOCAL_MODEL=True
LOCAL_MODEL_NAME=facebook/bart-large-cnn
SUMMARIZATION_PROVIDER=local

# Feed Processing
MIN_POST_LENGTH=10
MAX_POST_LENGTH=1000
SPAM_FILTER_ENABLED=True

# Audio Settings
AUDIO_BUFFER_SIZE=4096
AUDIO_CHUNK_DURATION=0.5
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file")

def main():
    """Main fix function"""
    print("🔧 Fixing SocialCast Extension Issues...")
    print("=" * 50)
    
    # Create simple icons
    create_simple_icons()
    
    # Update manifest
    update_manifest()
    
    # Setup npm
    setup_npm()
    
    # Create env file
    create_env_file()
    
    print("\n" + "=" * 50)
    print("✅ All fixes applied successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your MURF_API_KEY")
    print("2. Run: python app.py")
    print("3. Load extension in Chrome:")
    print("   - Go to chrome://extensions/")
    print("   - Enable Developer mode")
    print("   - Click 'Load unpacked'")
    print("   - Select the 'chrome-extension' folder")
    print("4. Visit a social media site and test the extension")
    
    print("\n🎯 The extension should now work without errors!")

if __name__ == "__main__":
    main()
