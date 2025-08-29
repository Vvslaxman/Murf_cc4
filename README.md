# Murf_cc4

# 🎙️ SocialCast – Your Social Media Podcast

 **Turn your social feeds into a narrated podcast using Murf TTS, LangChain, MCP & n8n**


## 🧠 Problem Statement

**"Social media feeds are endless, visually overwhelming, and drain productivity.  
Multitaskers often want to stay updated but cannot spend hours scrolling through Instagram, LinkedIn, Twitter, or WhatsApp Web.  
There’s no unified way to consume these feeds passively like a podcast."**


## 🚀 Our Solution – SocialCast

**SocialCast** transforms your social media feeds and messages into a narrated **real-time podcast**.  
Instead of endless scrolling, you simply **hit play** and listen to posts, updates, and messages in a human-like voice powered by **Murf API**.  


## ✅ Core Features

### 🔊 Cross-Platform Social Feed Reader
- Extracts new posts/messages from **LinkedIn, WhatsApp Web, Instagram, Telegram, and Twitter**.  
- Works via a **browser extension** that scrapes and sends content to the backend.  

### 🧠 LLM-Powered Summarization (LangChain + MCP)
- Summarizes long posts into **short, crisp spoken text**.  
- Filters out **spammy or low-value content** (like "ok", "haha", emojis).  
- Uses lightweight models (DistilBART / Flan-T5-small) or APIs (OpenAI GPT-4o-mini, Cohere Summarize).  

### 🎙️ Murf TTS Narration
- Converts feed updates into **natural, professional-quality audio**.  
- Supports **multiple voices, languages, and playback speeds**.  
- Uses **Murf WebSocket Streaming API** for real-time narration.  

### ⚡ Automation with n8n
- Triggers when new posts/messages arrive.  
- Sends content → summarizer → Murf → returns audio → auto-plays in browser.  

### 🎧 Smart Listening Experience
- Auto-queues new posts like a **playlist**.  
- Supports **voice commands** (*Pause, Skip, Replay*) via browser Web Speech API.  
- Optional **daily digest mode**: generates a podcast of all updates from the past 24h.  


## 📸 Workflow

**1. Browser Extension (content.js)**  
- Injects scripts into social media websites (LinkedIn, WhatsApp Web, Instagram, Twitter, Telegram).  
- Extracts feed content (posts, messages, captions, notifications).  
- Sends extracted text to backend (via REST API or n8n webhook).  

**2. Backend / n8n Automation**  
- n8n triggers on new incoming feed data.  
- Routes text through summarization pipeline.  
- Prioritizes/filter spammy or low-value content.  

**3. LangChain Pipeline (via MCP)**  
- Uses LLM (OpenAI GPT-4o-mini / Cohere / local Flan-T5-small) to:  
  - Summarize long posts into 1–2 crisp sentences.  
  - Classify posts/messages as “important” or “low-priority.”  
- Returns only useful, digestible content.  

**4. Murf API (WebSocket Streaming / TTS)**  
- Summarized text sent to Murf TTS.  
- Audio generated in near real-time.  
- Multiple voice, tone, speed, and language options available.  

**5. Browser Extension Audio Player**  
- Receives audio stream and plays it back-to-back like a podcast.  
- Provides voice control: “Pause”, “Skip”, “Replay.”  


```text
 ┌──────────────┐
 │ Social Media  │
 │ Websites      │
 └───────┬──────┘
         │ Extract posts/messages
         ▼
 ┌──────────────┐
 │ Browser Extn │
 └───────┬──────┘
         │ Send text
         ▼
 ┌──────────────┐      ┌──────────────┐
 │ Backend API  │─────▶│ LangChain    │
 │ (FastAPI/n8n)│      │ Summarizer   │
 └───────┬──────┘      └───────┬──────┘
         │ Filter / Prioritize  │
         ▼                      │
 ┌──────────────┐               │
 │ Murf API     │◀──────────────┘
 │ WebSocket TTS│
 └───────┬──────┘
         │ Audio
         ▼
 ┌──────────────┐
 │ Audio Player │
 │ + Voice Cmds │
 └──────────────┘
```

## 📦 Deliverables (Submission Plan)

- ✅ **MVP (Aug 29):**  
  - Chrome Extension + Backend + Murf API + Summarizer.  
  - Reads LinkedIn + WhatsApp Web feeds aloud.  

- ✅ **Multi-Site Support (Aug 30):**  
  - Add Instagram + Telegram + Twitter support.  
  - Implement smart filters (skip “ok”, “haha”, emoji-only messages).  

- ✅ **Automation & Voice Customization (Aug 31):**  
  - n8n daily digest automation.  
  - User-selectable Murf voices, languages, and playback speed.  
  - Voice command support.  


## ⚡ Proposed Advanced Yet Feasible Enhancements

### 1. AI Summarization without Heavy Models  
- Use **OpenAI GPT-4o-mini** or **Cohere Summarize** for cloud summarization.  
- If offline: run **DistilBART / Flan-T5-small** locally (lightweight).  
- Runs fine on 8GB RAM laptop without GPU stress.  

### 2. Smart Prioritization Layer  
- Rule-based + ML filter:  
  - Skip low-value posts (“ok”, “thanks”, emojis).  
  - Highlight priority posts with relevant keywords (e.g., “job update”, “AI research”, “event”).  

### 3. Daily Digest Mode  
- Collect last 24 hours of feeds → summarize → merge into a single audio file.  
- Output like a **personalized podcast**.  
- Batch Murf API call → cost and latency efficient.  

### 4. Lightweight Voice Commands  
- Powered by **Web Speech API (browser-native)**.  
- Commands: “Next”, “Pause”, “Replay.”  
- No external speech recognition engine needed.  

### 5. Offline-First Mode (Optional)  
- Summarization runs locally with Flan-T5-small.  
- Murf API still used for TTS.  
- Ensures feed narration works even with poor internet.  


## 🖥️ Feasibility Check (Your Laptop Specs)

- **Laptop:** i5 10th Gen, 8GB RAM, 512GB SSD, NVIDIA MX350.  
- **Backend (FastAPI/Flask):** ~200MB memory.  
- **LangChain + Flan-T5-small (optional):** ~2GB RAM CPU load.  
- **Murf TTS (API-based):** negligible local load.  
- **n8n Automation Tool:** ~400MB memory in Docker.  
- **Chrome Extension:** lightweight, negligible.  

👉 **Total Load < 4GB RAM → Perfectly feasible on your machine.**  


## 🎥 Demo Pitch Plan

- Show Chrome Extension overlay → click “Play Feed.”  
- Narration begins: “New LinkedIn post from Sarah: AI in Healthcare is transforming outcomes…”  
- Then WhatsApp: “Message from Rahul: Meeting shifted to 3PM.”  
- Then Instagram caption: “Photo by Priya: Exploring Ladakh!”  
- Demonstrate:  
  - Pause/Skip command.  
  - Switch between Murf voices.  
  - Generate “My Daily Digest” podcast.  


## 🔧 Tech Stack

| Component              | Technology Used |
|------------------------|-----------------|
| Feed Extraction        | Chrome Extension (content.js) |
| Automation / Orchestration | n8n (local/Docker) |
| Summarization + Filtering | LangChain + MCP + (OpenAI / Cohere / Flan-T5) |
| Text-to-Speech         | Murf API (TTS, Streaming, Dubbing) |
| Backend                | FastAPI / Flask |
| Playback               | Browser `<audio>` + Web Audio API |
| Voice Commands         | Browser Web Speech API |



## 📑 Submission Checklist

- [ ] Chrome Extension (multi-site support: LinkedIn, WhatsApp, Instagram, Twitter, Telegram).  
- [ ] Backend API (Flask/FastAPI) integrated with Murf API.  
- [ ] Summarization pipeline (LangChain + MCP).  
- [ ] n8n automation workflows (instant narration + daily digest).  
- [ ] Demo video (60–90 sec) highlighting accessibility, productivity, and real-world use.  
- [ ] GitHub repo with clean README + setup instructions.  




