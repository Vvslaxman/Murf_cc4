/**
 * SocialCast Popup Script
 * Handles popup UI interactions and communication
 */

class SocialCastPopup {
    constructor() {
        this.isListening = false;
        this.startTime = null;
        this.listeningInterval = null;
        
        this.init();
    }
    
    init() {
        // Get DOM elements
        this.elements = {
            startBtn: document.getElementById('start-btn'),
            stopBtn: document.getElementById('stop-btn'),
            digestBtn: document.getElementById('digest-btn'),
            statusDot: document.getElementById('status-dot'),
            statusText: document.getElementById('status-text'),
            currentPlatform: document.getElementById('current-platform'),
            postsCount: document.getElementById('posts-count'),
            audioCount: document.getElementById('audio-count'),
            listeningTime: document.getElementById('listening-time'),
            voiceSelect: document.getElementById('voice-select'),
            speedSlider: document.getElementById('speed-slider'),
            speedValue: document.getElementById('speed-value'),
            updateVoiceBtn: document.getElementById('update-voice-btn'),
            loading: document.getElementById('loading'),
            error: document.getElementById('error')
        };
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load initial state
        this.loadInitialState();
        
        // Update stats periodically
        setInterval(() => this.updateStats(), 5000);
    }
    
    setupEventListeners() {
        // Start/Stop listening
        this.elements.startBtn.addEventListener('click', () => this.startListening());
        this.elements.stopBtn.addEventListener('click', () => this.stopListening());
        
        // Generate digest
        this.elements.digestBtn.addEventListener('click', () => this.generateDigest());
        
        // Voice controls
        this.elements.speedSlider.addEventListener('input', (e) => {
            this.elements.speedValue.textContent = `${e.target.value}x`;
        });
        
        this.elements.updateVoiceBtn.addEventListener('click', () => this.updateVoiceConfig());
    }
    
    async loadInitialState() {
        try {
            // Get current tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (tab) {
                // Get status from content script
                const response = await chrome.tabs.sendMessage(tab.id, { action: 'getStatus' });
                
                if (response) {
                    this.updateStatus(response.isListening, response.platform);
                    this.elements.postsCount.textContent = response.postsExtracted || 0;
                }
            }
        } catch (error) {
            console.error('Error loading initial state:', error);
            this.showError('Could not connect to content script. Please refresh the page.');
        }
    }
    
    async startListening() {
        try {
            this.showLoading(true);
            
            // Get current tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (!tab) {
                throw new Error('No active tab found');
            }
            
            // Send message to content script
            const response = await chrome.tabs.sendMessage(tab.id, { action: 'startListening' });
            
            if (response && response.success) {
                this.isListening = true;
                this.startTime = Date.now();
                this.updateStatus(true);
                this.startListeningTimer();
                
                console.log('SocialCast: Started listening');
            } else {
                throw new Error('Failed to start listening');
            }
            
        } catch (error) {
            console.error('Error starting listening:', error);
            this.showError('Failed to start listening. Please refresh the page.');
        } finally {
            this.showLoading(false);
        }
    }
    
    async stopListening() {
        try {
            this.showLoading(true);
            
            // Get current tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (tab) {
                // Send message to content script
                await chrome.tabs.sendMessage(tab.id, { action: 'stopListening' });
            }
            
            this.isListening = false;
            this.updateStatus(false);
            this.stopListeningTimer();
            
            console.log('SocialCast: Stopped listening');
            
        } catch (error) {
            console.error('Error stopping listening:', error);
            this.showError('Failed to stop listening.');
        } finally {
            this.showLoading(false);
        }
    }
    
    async generateDigest() {
        try {
            this.showLoading(true);
            
            // Call backend API to generate digest
            const response = await fetch('http://localhost:8000/digest/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ hours: 24 })
            });
            
            if (response.ok) {
                const result = await response.json();
                
                if (result.audio_url) {
                    // Play the digest audio
                    const audio = new Audio(`http://localhost:8000/audio/${result.audio_url.split('/').pop()}`);
                    audio.play();
                    
                    this.showSuccess('Daily digest generated and playing!');
                } else {
                    this.showError('No posts found for digest');
                }
            } else {
                throw new Error('Failed to generate digest');
            }
            
        } catch (error) {
            console.error('Error generating digest:', error);
            this.showError('Failed to generate digest. Make sure the backend is running.');
        } finally {
            this.showLoading(false);
        }
    }
    
    async updateVoiceConfig() {
        try {
            this.showLoading(true);
            
            const voiceId = this.elements.voiceSelect.value;
            const speed = parseFloat(this.elements.speedSlider.value);
            
            // Calculate rate from speed (Murf uses -10 to 10 range)
            const rate = Math.round((speed - 1) * 10);
            
            // Call backend API to update voice config
            const response = await fetch('http://localhost:8000/voice/config', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    voice_id: voiceId,
                    style: 'Conversational',
                    rate: rate,
                    pitch: 0,
                    variation: 1
                })
            });
            
            if (response.ok) {
                this.showSuccess('Voice configuration updated!');
            } else {
                throw new Error('Failed to update voice config');
            }
            
        } catch (error) {
            console.error('Error updating voice config:', error);
            this.showError('Failed to update voice config. Make sure the backend is running.');
        } finally {
            this.showLoading(false);
        }
    }
    
    updateStatus(isListening, platform = null) {
        this.isListening = isListening;
        
        // Update UI
        if (isListening) {
            this.elements.statusDot.classList.add('active');
            this.elements.statusText.textContent = 'Listening for posts...';
            this.elements.startBtn.style.display = 'none';
            this.elements.stopBtn.style.display = 'block';
        } else {
            this.elements.statusDot.classList.remove('active');
            this.elements.statusText.textContent = 'Not listening';
            this.elements.startBtn.style.display = 'block';
            this.elements.stopBtn.style.display = 'none';
        }
        
        if (platform) {
            this.elements.currentPlatform.textContent = platform.charAt(0).toUpperCase() + platform.slice(1);
        }
    }
    
    startListeningTimer() {
        this.stopListeningTimer();
        
        this.listeningInterval = setInterval(() => {
            if (this.startTime) {
                const elapsed = Date.now() - this.startTime;
                const minutes = Math.floor(elapsed / 60000);
                const seconds = Math.floor((elapsed % 60000) / 1000);
                this.elements.listeningTime.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            }
        }, 1000);
    }
    
    stopListeningTimer() {
        if (this.listeningInterval) {
            clearInterval(this.listeningInterval);
            this.listeningInterval = null;
        }
    }
    
    async updateStats() {
        try {
            // Get stats from backend
            const response = await fetch('http://localhost:8000/stats');
            
            if (response.ok) {
                const stats = await response.json();
                const data = stats.statistics;
                
                this.elements.postsCount.textContent = data.total_posts_processed || 0;
                this.elements.audioCount.textContent = data.posts_with_audio || 0;
            }
        } catch (error) {
            // Silently fail - backend might not be running
            console.debug('Could not fetch stats:', error);
        }
    }
    
    showLoading(show) {
        this.elements.loading.style.display = show ? 'block' : 'none';
    }
    
    showError(message) {
        this.elements.error.textContent = message;
        this.elements.error.style.display = 'block';
        
        // Hide after 5 seconds
        setTimeout(() => {
            this.elements.error.style.display = 'none';
        }, 5000);
    }
    
    showSuccess(message) {
        // Create a temporary success message
        const successDiv = document.createElement('div');
        successDiv.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #2ed573;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 12px;
            z-index: 10000;
        `;
        successDiv.textContent = message;
        
        document.body.appendChild(successDiv);
        
        // Remove after 3 seconds
        setTimeout(() => {
            document.body.removeChild(successDiv);
        }, 3000);
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SocialCastPopup();
});

