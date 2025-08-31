/**
 * SocialCast Content Script
 * Extracts posts from social media sites and sends them to the backend
 */

// Prevent multiple script injections
if (window.SocialCastContentScript) {
    console.log('SocialCast: Content script already loaded, skipping...');
} else {
    window.SocialCastContentScript = true;

    class SocialCastContentScript {
        constructor() {
            this.isListening = false;
            this.backendUrl = 'http://localhost:8000';
            this.extractedPosts = new Set();
            this.audioPlayer = null;
            this.voiceRecognition = null;
            this.currentPlatform = this.detectPlatform();
            this.observer = null;
            
            this.init();
        }
        
        init() {
            console.log('SocialCast: Content script initialized for', this.currentPlatform);
            
            // Create audio player overlay
            this.createAudioPlayer();
            
            // Setup voice recognition
            this.setupVoiceRecognition();
            
            // Start observing DOM changes
            this.observeDOM();
            
            // Listen for messages from popup
            chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
                this.handleMessage(request, sendResponse);
                return true;
            });
        }
        
        detectPlatform() {
            const hostname = window.location.hostname;
            
            if (hostname.includes('linkedin.com')) return 'linkedin';
            if (hostname.includes('whatsapp.com')) return 'whatsapp';
            if (hostname.includes('instagram.com')) return 'instagram';
            if (hostname.includes('twitter.com') || hostname.includes('x.com')) return 'twitter';
            if (hostname.includes('telegram.org')) return 'telegram';
            if (hostname.includes('facebook.com')) return 'facebook';
            
            return 'unknown';
        }
        
        createAudioPlayer() {
            // Check if player already exists
            if (document.getElementById('socialcast-player')) {
                return;
            }
            
            // Create audio player overlay
            const playerHTML = `
                <div id="socialcast-player" style="display: none;">
                    <div class="socialcast-controls">
                        <button id="socialcast-play" class="socialcast-btn">▶️ Play</button>
                        <button id="socialcast-pause" class="socialcast-btn">⏸️ Pause</button>
                        <button id="socialcast-skip" class="socialcast-btn">⏭️ Skip</button>
                        <button id="socialcast-stop" class="socialcast-btn">⏹️ Stop</button>
                        <span id="socialcast-status">Ready</span>
                    </div>
                    <div class="socialcast-progress">
                        <div id="socialcast-progress-bar"></div>
                    </div>
                </div>
            `;
            
            // Add styles
            const styles = `
                <style>
                    #socialcast-player {
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background: rgba(0, 0, 0, 0.9);
                        color: white;
                        padding: 15px;
                        border-radius: 10px;
                        z-index: 10000;
                        font-family: Arial, sans-serif;
                        min-width: 300px;
                    }
                    
                    .socialcast-controls {
                        display: flex;
                        gap: 10px;
                        align-items: center;
                        margin-bottom: 10px;
                    }
                    
                    .socialcast-btn {
                        background: #007bff;
                        color: white;
                        border: none;
                        padding: 8px 12px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 12px;
                    }
                    
                    .socialcast-btn:hover {
                        background: #0056b3;
                    }
                    
                    .socialcast-progress {
                        width: 100%;
                        height: 4px;
                        background: rgba(255, 255, 255, 0.3);
                        border-radius: 2px;
                        overflow: hidden;
                    }
                    
                    #socialcast-progress-bar {
                        height: 100%;
                        background: #007bff;
                        width: 0%;
                        transition: width 0.3s ease;
                    }
                </style>
            `;
            
            // Add to page
            document.head.insertAdjacentHTML('beforeend', styles);
            document.body.insertAdjacentHTML('beforeend', playerHTML);
            
            // Get player element
            this.audioPlayer = document.getElementById('socialcast-player');
            
            // Add event listeners
            this.addPlayerEventListeners();
        }
        
        addPlayerEventListeners() {
            const playBtn = document.getElementById('socialcast-play');
            const pauseBtn = document.getElementById('socialcast-pause');
            const skipBtn = document.getElementById('socialcast-skip');
            const stopBtn = document.getElementById('socialcast-stop');
            
            if (playBtn) playBtn.addEventListener('click', () => this.startListening());
            if (pauseBtn) pauseBtn.addEventListener('click', () => this.pauseListening());
            if (skipBtn) skipBtn.addEventListener('click', () => this.skipPost());
            if (stopBtn) stopBtn.addEventListener('click', () => this.stopListening());
        }
        
        setupVoiceRecognition() {
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                this.voiceRecognition = new SpeechRecognition();
                this.voiceRecognition.continuous = true;
                this.voiceRecognition.interimResults = false;
                this.voiceRecognition.lang = 'en-US';
                
                this.voiceRecognition.onresult = (event) => {
                    const command = event.results[event.results.length - 1][0].transcript.toLowerCase();
                    this.handleVoiceCommand(command);
                };
                
                this.voiceRecognition.onerror = (event) => {
                    console.log('Voice recognition error:', event.error);
                };
            }
        }
        
        handleVoiceCommand(command) {
            console.log('Voice command received:', command);
            
            if (command.includes('pause') || command.includes('stop')) {
                this.pauseListening();
            } else if (command.includes('skip') || command.includes('next')) {
                this.skipPost();
            } else if (command.includes('play') || command.includes('start')) {
                this.startListening();
            } else if (command.includes('replay')) {
                this.replayPost();
            }
        }
        
        observeDOM() {
            if (this.observer) {
                this.observer.disconnect();
            }
            
            this.observer = new MutationObserver((mutations) => {
                if (this.isListening) {
                    mutations.forEach((mutation) => {
                        if (mutation.type === 'childList') {
                            mutation.addedNodes.forEach((node) => {
                                if (node.nodeType === Node.ELEMENT_NODE) {
                                    this.extractPostsFromNode(node);
                                }
                            });
                        }
                    });
                }
            });
            
            this.observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        }
        
        extractPostsFromNode(node) {
            const selectors = this.getPlatformSelectors();
            
            for (const selector of selectors) {
                try {
                    const elements = Array.from(node.querySelectorAll ? node.querySelectorAll(selector) : []);
                    if (node.matches && node.matches(selector)) {
                        elements.push(node);
                    }
                    
                    elements.forEach(element => {
                        this.processPost(element);
                    });
                } catch (error) {
                    console.log('Error extracting posts:', error);
                }
            }
        }
        
        getPlatformSelectors() {
            switch (this.currentPlatform) {
                case 'linkedin':
                    return [
                        'article[data-test-id="post"]',
                        '.feed-shared-update-v2',
                        '.feed-shared-text',
                        '.update-components-text'
                    ];
                case 'twitter':
                case 'x':
                    return [
                        'article[data-testid="tweet"]',
                        '.tweet-text',
                        '[data-testid="tweetText"]'
                    ];
                case 'instagram':
                    return [
                        'article[role="presentation"]',
                        '.caption',
                        '[data-testid="post-caption"]'
                    ];
                case 'whatsapp':
                    return [
                        '.message-in',
                        '.message-out',
                        '.copyable-text'
                    ];
                case 'facebook':
                    return [
                        '[data-testid="post_message"]',
                        '.userContent',
                        '.story_body_container'
                    ];
                default:
                    return ['p', 'div', 'span'];
            }
        }
        
        processPost(element) {
            try {
                const text = element.textContent?.trim();
                if (!text || text.length < 10 || this.extractedPosts.has(text)) {
                    return;
                }
                
                this.extractedPosts.add(text);
                
                const post = {
                    platform: this.currentPlatform,
                    author: this.extractAuthor(element),
                    content: text,
                    url: window.location.href,
                    timestamp: new Date().toISOString()
                };
                
                console.log('SocialCast: Extracted post:', post);
                
                // Send to backend
                this.sendPostToBackend(post);
                
            } catch (error) {
                console.log('Error processing post:', error);
            }
        }
        
        extractAuthor(element) {
            // Try to extract author from various selectors
            const authorSelectors = [
                '[data-testid="author"]',
                '.author',
                '.username',
                '.user-name',
                '[data-testid="user-name"]'
            ];
            
            for (const selector of authorSelectors) {
                const authorElement = element.querySelector(selector) || element.closest(selector);
                if (authorElement) {
                    return authorElement.textContent?.trim() || 'Unknown';
                }
            }
            
            return 'Unknown';
        }
        
        async sendPostToBackend(post) {
            try {
                const response = await fetch(`${this.backendUrl}/posts/process`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        posts: [post]
                    })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    console.log('SocialCast: Post processed successfully:', result);
                    
                    // Update UI
                    this.updateStatus(`Processed: ${post.content.substring(0, 50)}...`);
                } else {
                    console.error('SocialCast: Failed to process post:', response.status);
                }
            } catch (error) {
                console.error('SocialCast: Error sending post to backend:', error);
            }
        }
        
        handleMessage(request, sendResponse) {
            console.log('SocialCast: Received message:', request);
            
            switch (request.action) {
                case 'startListening':
                    this.startListening();
                    sendResponse({ success: true });
                    break;
                    
                case 'stopListening':
                    this.stopListening();
                    sendResponse({ success: true });
                    break;
                    
                case 'getStatus':
                    sendResponse({
                        isListening: this.isListening,
                        platform: this.currentPlatform,
                        postsCount: this.extractedPosts.size
                    });
                    break;
                    
                default:
                    sendResponse({ error: 'Unknown action' });
            }
        }
        
        startListening() {
            this.isListening = true;
            this.showPlayer();
            this.updateStatus('Listening for posts...');
            
            if (this.voiceRecognition) {
                this.voiceRecognition.start();
            }
            
            console.log('SocialCast: Started listening');
        }
        
        stopListening() {
            this.isListening = false;
            this.hidePlayer();
            this.updateStatus('Stopped');
            
            if (this.voiceRecognition) {
                this.voiceRecognition.stop();
            }
            
            console.log('SocialCast: Stopped listening');
        }
        
        pauseListening() {
            this.updateStatus('Paused');
            console.log('SocialCast: Paused listening');
        }
        
        skipPost() {
            this.updateStatus('Skipped to next post');
            console.log('SocialCast: Skipped post');
        }
        
        replayPost() {
            this.updateStatus('Replaying last post');
            console.log('SocialCast: Replaying post');
        }
        
        showPlayer() {
            if (this.audioPlayer) {
                this.audioPlayer.style.display = 'block';
            }
        }
        
        hidePlayer() {
            if (this.audioPlayer) {
                this.audioPlayer.style.display = 'none';
            }
        }
        
        updateStatus(message) {
            const statusElement = document.getElementById('socialcast-status');
            if (statusElement) {
                statusElement.textContent = message;
            }
        }
    }
    
    // Initialize the content script
    const socialCast = new SocialCastContentScript();
}

