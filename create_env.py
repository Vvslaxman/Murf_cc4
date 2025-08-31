#!/usr/bin/env python3
"""
Create .env file for SocialCast
"""

import os

def create_env_file():
    """Create .env file with proper settings"""
    
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

# Summarization Settings - Using Fast Local Models by Default
MAX_TEXT_LENGTH=3000
SUMMARY_MAX_LENGTH=200
USE_LOCAL_MODEL=True
LOCAL_MODEL_NAME=sshleifer/distilbart-cnn-12-6
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
    
    print("✅ .env file created successfully!")
    print("📝 Please edit the .env file and add your actual API keys:")
    print("   - MURF_API_KEY: Get from https://murf.ai")
    print("   - OPENAI_API_KEY: Optional, for cloud summarization")
    print("   - COHERE_API_KEY: Optional, alternative summarization")

if __name__ == "__main__":
    create_env_file()
