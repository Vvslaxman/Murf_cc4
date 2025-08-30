# 🚀 SocialCast Quick Start Guide

Get SocialCast running in **5 minutes** with this quick start guide!

## 📋 Prerequisites

- Python 3.8+
- Chrome browser
- Murf API key (get from [murf.ai](https://murf.ai))

## ⚡ Quick Setup (5 minutes)

### 1. Clone and Setup
```bash
git clone <your-repo>
cd SocialCast
python setup.py
```

### 2. Configure API Keys
Edit `.env` file:
```bash
MURF_API_KEY=your_actual_murf_api_key_here
```

### 3. Start Backend
```bash
python app.py
```

### 4. Load Chrome Extension
1. Open Chrome → `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `chrome-extension/` folder

### 5. Test Everything
```bash
python demo.py
```

## 🎯 Usage

1. **Visit any social media site** (LinkedIn, WhatsApp, Instagram, Twitter, etc.)
2. **Click the SocialCast extension icon**
3. **Click "Start Listening"**
4. **Browse your feeds** - posts will be automatically narrated!

## 🎙️ Features Demonstrated

### ✅ Core Features Working
- **Multi-platform support**: LinkedIn, WhatsApp, Instagram, Twitter, Telegram, Facebook
- **Real-time TTS**: Murf WebSocket streaming with 3000 character chunking
- **Smart filtering**: Removes spam ("ok", "haha", emoji-only posts)
- **AI summarization**: LangChain-powered content summarization
- **Voice commands**: "Pause", "Skip", "Replay" via Web Speech API
- **Daily digest**: Generate 24-hour podcast summaries

### 🎤 Voice Options
- **Amara** (Conversational)
- **Jenny** (Professional) 
- **Mike** (Casual)
- **Priya** (Friendly)
- **Charles** (Formal)

### 📊 Content Prioritization
- **High priority**: Job updates, AI news, meetings, deadlines
- **Medium priority**: General posts, travel updates
- **Low priority**: Spam, short messages, emoji-only

## 🔧 Advanced Configuration

### Voice Settings
```bash
# Update voice configuration
curl -X PUT http://localhost:8000/voice/config \
  -H "Content-Type: application/json" \
  -d '{
    "voice_id": "en-US-jenny",
    "style": "Professional",
    "rate": 0,
    "pitch": 0,
    "variation": 1
  }'
```

### Generate Daily Digest
```bash
curl -X POST http://localhost:8000/digest/generate \
  -H "Content-Type: application/json" \
  -d '{"hours": 24}'
```

## 🧪 Testing

### Run Full Test Suite
```bash
python test_socialcast.py
```

### Test Individual Components
```bash
# Test TTS only
python -c "
import asyncio
from services.murf_tts import murf_tts_service, TTSRequest, VoiceConfig
async def test():
    req = TTSRequest('Hello SocialCast!', VoiceConfig())
    await murf_tts_service.generate_audio_file(req, 'test.wav')
asyncio.run(test())
"
```

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check dependencies
pip install -r requirements.txt

# Check API key
echo $MURF_API_KEY

# Check port availability
netstat -an | grep 8000
```

### Extension Not Working
1. Check Chrome console for errors
2. Verify backend is running: `curl http://localhost:8000/health`
3. Reload extension in `chrome://extensions/`

### TTS Issues
1. Verify Murf API key is valid
2. Check internet connection
3. Test with short text first

## 📈 Performance

- **Memory usage**: < 4GB RAM
- **Latency**: < 2 seconds post-to-audio
- **Supported text length**: Unlimited (auto-chunked)
- **Voice quality**: Professional-grade Murf TTS

## 🔗 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Backend health check |
| `/posts/process` | POST | Process social media posts |
| `/tts/generate` | POST | Generate TTS audio |
| `/tts/stream/{text}` | GET | Stream TTS audio |
| `/digest/generate` | POST | Generate daily digest |
| `/voices` | GET | Get available voices |
| `/voice/config` | PUT | Update voice settings |
| `/stats` | GET | Get processing statistics |
| `/ws` | WebSocket | Real-time communication |

## 🎉 Success!

You now have a fully functional SocialCast system that:
- ✅ Extracts posts from social media
- ✅ Summarizes content with AI
- ✅ Generates professional TTS audio
- ✅ Supports voice commands
- ✅ Creates daily digests
- ✅ Works across multiple platforms

**Enjoy your social media podcast! 🎙️**

