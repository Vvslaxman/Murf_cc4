/**
 * SocialCast Content Script
 * Extracts posts from social media sites and sends them to the backend
 */

class SocialCastContentScript {
    constructor() {
        this.isListening = false;
        this.backendUrl = 'http://localhost:8000';
        this.extractedPosts = new Set();
        this.audioPlayer = null;
        this.voiceRecognition = null;
        this.currentPlatform = this.detectPlatform();
        
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
                    background: #333;
                    border-radius: 2px;
                    overflow: hidden;
                }
                
                #socialcast-progress-bar {
                    height: 100%;
                    background: #007bff;
                    width: 0%;
                    transition: width 0.3s;
                }
                
                #socialcast-status {
                    font-size: 12px;
                    margin-left: auto;
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
        document.body.insertAdjacentHTML('beforeend', playerHTML);
        
        // Setup event listeners
        this.setupPlayerEvents();
    }
    
    setupPlayerEvents() {
        const playBtn = document.getElementById('socialcast-play');
        const pauseBtn = document.getElementById('socialcast-pause');
        const skipBtn = document.getElementById('socialcast-skip');
        const stopBtn = document.getElementById('socialcast-stop');
        
        playBtn?.addEventListener('click', () => this.startListening());
        pauseBtn?.addEventListener('click', () => this.pauseListening());
        skipBtn?.addEventListener('click', () => this.skipCurrent());
        stopBtn?.addEventListener('click', () => this.stopListening());
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
        console.log('Voice command:', command);
        
        if (command.includes('play') || command.includes('start')) {
            this.startListening();
        } else if (command.includes('pause') || command.includes('stop')) {
            this.pauseListening();
        } else if (command.includes('skip') || command.includes('next')) {
            this.skipCurrent();
        } else if (command.includes('replay') || command.includes('repeat')) {
            this.replayCurrent();
        }
    }
    
    observeDOM() {
        // Create a mutation observer to watch for new posts
        const observer = new MutationObserver((mutations) => {
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
        
        // Start observing
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Also extract existing posts
        this.extractPostsFromNode(document.body);
    }
    
    extractPostsFromNode(node) {
        const selectors = this.getSelectorsForPlatform();
        
        selectors.forEach(selector => {
            const elements = node.querySelectorAll ? node.querySelectorAll(selector) : [];
            if (node.matches && node.matches(selector)) {
                elements.push(node);
            }
            
            elements.forEach(element => {
                this.extractPostFromElement(element);
            });
        });
    }
    
    getSelectorsForPlatform() {
        const selectors = {
            linkedin: [
                '[data-test-id="post-content"]',
                '.feed-shared-update-v2__description',
                '.feed-shared-text',
                '.artdeco-entity-lockup__title'
            ],
            whatsapp: [
                '.message-in .selectable-text',
                '.message-out .selectable-text',
                '[data-testid="conversation-message"]'
            ],
            instagram: [
                'article div[dir="auto"]',
                '.x1lliihq',
                '[data-testid="post-caption"]'
            ],
            twitter: [
                '[data-testid="tweetText"]',
                '.css-901oao',
                '[data-testid="tweet"]'
            ],
            telegram: [
                '.message',
                '.text',
                '.bubble'
            ],
            facebook: [
                '[data-testid="post_message"]',
                '.userContent',
                '.story_body_container'
            ]
        };
        
        return selectors[this.currentPlatform] || [];
    }
    
    extractPostFromElement(element) {
        try {
            const text = element.textContent?.trim();
            if (!text || text.length < 10) return;
            
            // Generate a unique ID for this post
            const postId = this.generatePostId(text);
            if (this.extractedPosts.has(postId)) return;
            
            this.extractedPosts.add(postId);
            
            // Extract author information
            const author = this.extractAuthor(element);
            
            // Create post object
            const post = {
                platform: this.currentPlatform,
                author: author,
                content: text,
                url: window.location.href,
                media_type: this.detectMediaType(element)
            };
            
            console.log('SocialCast: Extracted post:', post);
            
            // Send to backend if listening
            if (this.isListening) {
                this.sendPostToBackend(post);
            }
            
        } catch (error) {
            console.error('SocialCast: Error extracting post:', error);
        }
    }
    
    generatePostId(text) {
        // Create a simple hash of the text content
        let hash = 0;
        for (let i = 0; i < text.length; i++) {
            const char = text.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return `${this.currentPlatform}_${Math.abs(hash)}`;
    }
    
    extractAuthor(element) {
        // Try to find author information based on platform
        const authorSelectors = {
            linkedin: '.feed-shared-actor__name, .artdeco-entity-lockup__title',
            whatsapp: '.copyable-text span[title]',
            instagram: 'a[role="link"]',
            twitter: '[data-testid="User-Name"]',
            telegram: '.peer_title',
            facebook: '.fwb'
        };
        
        const selector = authorSelectors[this.currentPlatform];
        if (selector) {
            const authorElement = element.closest('*').querySelector(selector);
            if (authorElement) {
                return authorElement.textContent?.trim() || 'Unknown';
            }
        }
        
        return 'Unknown';
    }
    
    detectMediaType(element) {
        // Check if the post contains media
        const mediaSelectors = {
            image: 'img, [data-testid="tweetPhoto"]',
            video: 'video, [data-testid="videoPlayer"]',
            link: 'a[href]'
        };
        
        for (const [type, selector] of Object.entries(mediaSelectors)) {
            if (element.querySelector(selector)) {
                return type;
            }
        }
        
        return 'text';
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
                console.log('SocialCast: Post processed:', result);
                
                // Play audio if available
                if (result.processed_posts && result.processed_posts.length > 0) {
                    const processedPost = result.processed_posts[0];
                    if (processedPost.audio_url) {
                        this.playAudio(processedPost);
                    }
                }
            } else {
                console.error('SocialCast: Failed to process post:', response.status);
            }
        } catch (error) {
            console.error('SocialCast: Error sending post to backend:', error);
        }
    }
    
    playAudio(processedPost) {
        const audioUrl = `${this.backendUrl}/audio/${processedPost.audio_url.split('/').pop()}`;
        
        if (this.audioPlayer) {
            this.audioPlayer.pause();
        }
        
        this.audioPlayer = new Audio(audioUrl);
        this.audioPlayer.play();
        
        this.updateStatus(`Playing: ${processedPost.summary}`);
        this.updateProgress(0);
        
        this.audioPlayer.addEventListener('timeupdate', () => {
            const progress = (this.audioPlayer.currentTime / this.audioPlayer.duration) * 100;
            this.updateProgress(progress);
        });
        
        this.audioPlayer.addEventListener('ended', () => {
            this.updateStatus('Ready');
            this.updateProgress(0);
        });
    }
    
    handleMessage(request, sendResponse) {
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
                    postsExtracted: this.extractedPosts.size
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
        
        // Start voice recognition
        if (this.voiceRecognition) {
            this.voiceRecognition.start();
        }
        
        console.log('SocialCast: Started listening for posts');
    }
    
    stopListening() {
        this.isListening = false;
        this.hidePlayer();
        this.updateStatus('Stopped');
        
        // Stop voice recognition
        if (this.voiceRecognition) {
            this.voiceRecognition.stop();
        }
        
        // Stop audio
        if (this.audioPlayer) {
            this.audioPlayer.pause();
            this.audioPlayer = null;
        }
        
        console.log('SocialCast: Stopped listening');
    }
    
    pauseListening() {
        if (this.audioPlayer) {
            this.audioPlayer.pause();
            this.updateStatus('Paused');
        }
    }
    
    skipCurrent() {
        if (this.audioPlayer) {
            this.audioPlayer.currentTime = this.audioPlayer.duration;
            this.updateStatus('Skipped');
        }
    }
    
    replayCurrent() {
        if (this.audioPlayer) {
            this.audioPlayer.currentTime = 0;
            this.audioPlayer.play();
            this.updateStatus('Replaying...');
        }
    }
    
    showPlayer() {
        const player = document.getElementById('socialcast-player');
        if (player) {
            player.style.display = 'block';
        }
    }
    
    hidePlayer() {
        const player = document.getElementById('socialcast-player');
        if (player) {
            player.style.display = 'none';
        }
    }
    
    updateStatus(status) {
        const statusElement = document.getElementById('socialcast-status');
        if (statusElement) {
            statusElement.textContent = status;
        }
    }
    
    updateProgress(percentage) {
        const progressBar = document.getElementById('socialcast-progress-bar');
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }
    }
}

// Initialize the content script
new SocialCastContentScript();

