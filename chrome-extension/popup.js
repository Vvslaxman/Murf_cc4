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
                
                if (response && !response.error) {
                    this.updateStatus(response.isListening, response.platform);
                    this.elements.postsCount.textContent = response.postsCount || 0;
                } else {
                    // Try to get status from background script
                    const bgResponse = await chrome.runtime.sendMessage({ action: 'getStatus' });
                    if (bgResponse && !bgResponse.error) {
                        this.updateStatus(bgResponse.isListening, bgResponse.platform);
                        this.elements.postsCount.textContent = bgResponse.postsCount || 0;
                    }
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
            
            // Send message to background script
            const response = await chrome.runtime.sendMessage({ action: 'startListening' });
            
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
            this.showError('Error starting listening: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }
    
    async stopListening() {
        try {
            this.showLoading(true);
            
            // Send message to background script
            const response = await chrome.runtime.sendMessage({ action: 'stopListening' });
            
            if (response && response.success) {
                this.isListening = false;
                this.updateStatus(false);
                this.stopListeningTimer();
                
                console.log('SocialCast: Stopped listening');
            } else {
                throw new Error('Failed to stop listening');
            }
        } catch (error) {
            console.error('Error stopping listening:', error);
            this.showError('Error stopping listening: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }
    
    async generateDigest() {
        try {
            this.showLoading(true);
            
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
                    const audio = new Audio(`http://localhost:8000${result.audio_url}`);
                    audio.play();
                    
                    this.showMessage('Daily digest generated and playing!');
                } else {
                    this.showMessage('No posts found for digest');
                }
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error generating digest:', error);
            this.showError('Error generating digest: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }
    
    async updateVoiceConfig() {
        try {
            const voiceConfig = {
                voice_id: this.elements.voiceSelect.value,
                rate: parseFloat(this.elements.speedSlider.value) - 1, // Convert to -1 to 1 range
                style: 'Conversational'
            };
            
            const response = await fetch('http://localhost:8000/voice/config', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(voiceConfig)
            });
            
            if (response.ok) {
                this.showMessage('Voice configuration updated!');
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error updating voice config:', error);
            this.showError('Error updating voice config: ' + error.message);
        }
    }
    
    async updateStats() {
        try {
            const response = await fetch('http://localhost:8000/stats');
            
            if (response.ok) {
                const stats = await response.json();
                
                this.elements.postsCount.textContent = stats.statistics.total_posts || 0;
                this.elements.audioCount.textContent = stats.statistics.total_audio_generated || 0;
                
                // Update listening time
                if (this.isListening && this.startTime) {
                    const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
                    const minutes = Math.floor(elapsed / 60);
                    const seconds = elapsed % 60;
                    this.elements.listeningTime.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
                }
            }
        } catch (error) {
            console.error('Error updating stats:', error);
        }
    }
    
    updateStatus(isListening, platform = null) {
        this.isListening = isListening;
        
        // Update UI
        if (isListening) {
            this.elements.statusDot.classList.add('active');
            this.elements.statusText.textContent = 'Listening';
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
                const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
                const minutes = Math.floor(elapsed / 60);
                const seconds = elapsed % 60;
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
    
    showLoading(show) {
        this.elements.loading.style.display = show ? 'block' : 'none';
    }
    
    showError(message) {
        this.elements.error.textContent = message;
        this.elements.error.style.display = 'block';
        
        setTimeout(() => {
            this.elements.error.style.display = 'none';
        }, 5000);
    }
    
    showMessage(message) {
        // Create a temporary message element
        const messageEl = document.createElement('div');
        messageEl.textContent = message;
        messageEl.style.cssText = `
            position: fixed;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            background: #2ed573;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            z-index: 10000;
            font-size: 14px;
        `;
        
        document.body.appendChild(messageEl);
        
        setTimeout(() => {
            document.body.removeChild(messageEl);
        }, 3000);
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SocialCastPopup();
});

