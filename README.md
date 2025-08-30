# 🎙️ SocialCast – Your Social Media Podcast

**Turn your social feeds into a narrated podcast using Murf TTS, LangChain, MCP & n8n**

## 🧠 Problem Statement

Social media feeds are endless, visually overwhelming, and drain productivity. Multitaskers often want to stay updated but cannot spend hours scrolling through Instagram, LinkedIn, Twitter, or WhatsApp Web. There's no unified way to consume these feeds passively like a podcast.

## 🚀 Our Solution – SocialCast

**SocialCast** transforms your social media feeds and messages into a narrated **real-time podcast**. Instead of endless scrolling, you simply **hit play** and listen to posts, updates, and messages in a human-like voice powered by **Murf API**.

## ✅ Core Features

### 🔊 Cross-Platform Social Feed Reader
- Extracts new posts/messages from **LinkedIn, WhatsApp Web, Instagram, Telegram, and Twitter**
- Works via a **browser extension** that scrapes and sends content to the backend

### 🧠 LLM-Powered Summarization (LangChain + MCP)
- Summarizes long posts into **short, crisp spoken text**
- Filters out **spammy or low-value content** (like "ok", "haha", emojis)
- Uses lightweight models (DistilBART / Flan-T5-small) or APIs (OpenAI GPT-4o-mini, Cohere Summarize)

### 🎙️ Murf TTS Narration
- Converts feed updates into **natural, professional-quality audio**
- Supports **multiple voices, languages, and playback speeds**
- Uses **Murf WebSocket Streaming API** for real-time narration

### ⚡ Automation with n8n
- Triggers when new posts/messages arrive
- Sends content → summarizer → Murf → returns audio → auto-plays in browser

### 🎧 Smart Listening Experience
- Auto-queues new posts like a **playlist**
- Supports **voice commands** (*Pause, Skip, Replay*) via browser Web Speech API
- Optional **daily digest mode**: generates a podcast of all updates from the past 24h

## 🛠️ Quick Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Chrome browser
- Murf API key (get from [murf.ai](https://murf.ai))

### Installation

1. **Clone and setup backend:**
```bash
git clone <your-repo>
cd SocialCast
pip install -r requirements.txt
```

2. **Setup environment variables:**
```bash
cp .env.example .env
# Edit .env with your Murf API key and other settings
```

3. **Install Chrome Extension:**
```bash
cd chrome-extension
npm install
npm run build
# Load the extension in Chrome from the dist/ folder
```

4. **Start the backend:**
```bash
python app.py
```

5. **Setup n8n (optional):**
```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

## 📦 Project Structure

```
SocialCast/
├── app.py                 # FastAPI backend
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── chrome-extension/     # Browser extension
│   ├── manifest.json
│   ├── src/
│   │   ├── content.js    # Content script for social sites
│   │   ├── background.js # Background script
│   │   └── popup.js      # Extension popup
│   └── dist/             # Built extension
├── services/
│   ├── summarizer.py     # LangChain summarization
│   ├── murf_tts.py      # Murf TTS integration
│   └── feed_processor.py # Feed processing logic
├── n8n-workflows/        # n8n automation workflows
└── README.md
```

## 🎯 Usage

1. **Load the Chrome Extension** on your social media sites
2. **Click "Start Listening"** in the extension popup
3. **Browse your feeds** - posts will be automatically narrated
4. **Use voice commands**: "Pause", "Skip", "Replay"

## 🔧 Configuration

### Murf TTS Settings
- Voice selection (150+ voices available)
- Language support (21+ languages)
- Speed and pitch control
- Style customization (Conversational, Professional, etc.)

### Summarization Options
- OpenAI GPT-4o-mini (cloud)
- Cohere Summarize (cloud)
- Flan-T5-small (local)

## 📊 Performance

- **Memory Usage**: < 4GB RAM total
- **Latency**: < 2 seconds from post to audio
- **Supported Sites**: LinkedIn, WhatsApp Web, Instagram, Twitter, Telegram

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- Issues: GitHub Issues
- Documentation: [murf.ai/api/docs](https://murf.ai/api/docs)
- Community: Discord server

