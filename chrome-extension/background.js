/**
 * SocialCast Background Script
 * Handles extension lifecycle and background tasks
 */

// Extension installation
chrome.runtime.onInstalled.addListener((details) => {
    console.log('SocialCast extension installed:', details.reason);
    
    if (details.reason === 'install') {
        // Show welcome page or setup instructions
        chrome.tabs.create({
            url: 'https://github.com/your-repo/socialcast#readme'
        });
    }
});

// Handle messages from content scripts and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Background script received message:', request);
    
    switch (request.action) {
        case 'getTabInfo':
            // Return information about the current tab
            sendResponse({
                url: sender.tab?.url,
                title: sender.tab?.title,
                id: sender.tab?.id
            });
            break;
            
        case 'openOptions':
            // Open options page
            chrome.runtime.openOptionsPage();
            sendResponse({ success: true });
            break;
            
        case 'checkBackend':
            // Check if backend is running
            checkBackendStatus().then(status => {
                sendResponse({ backendRunning: status });
            });
            return true; // Keep message channel open for async response
            
        case 'startListening':
            // Forward to content script
            chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
                if (tabs[0]) {
                    chrome.tabs.sendMessage(tabs[0].id, {action: 'startListening'});
                }
            });
            sendResponse({ success: true });
            break;
            
        case 'stopListening':
            // Forward to content script
            chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
                if (tabs[0]) {
                    chrome.tabs.sendMessage(tabs[0].id, {action: 'stopListening'});
                }
            });
            sendResponse({ success: true });
            break;
            
        case 'getStatus':
            // Get status from content script
            chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
                if (tabs[0]) {
                    chrome.tabs.sendMessage(tabs[0].id, {action: 'getStatus'}, function(response) {
                        sendResponse(response);
                    });
                } else {
                    sendResponse({ error: 'No active tab' });
                }
            });
            return true; // Keep message channel open for async response
            
        default:
            sendResponse({ error: 'Unknown action' });
    }
});

// Check if backend is running
async function checkBackendStatus() {
    try {
        const response = await fetch('http://localhost:8000/health', {
            method: 'GET',
            timeout: 3000
        });
        return response.ok;
    } catch (error) {
        console.log('Backend not running:', error);
        return false;
    }
}

// Handle tab updates to inject content script if needed
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        // Check if this is a supported social media site
        const supportedSites = [
            'linkedin.com',
            'whatsapp.com',
            'instagram.com',
            'twitter.com',
            'x.com',
            'telegram.org',
            'facebook.com'
        ];
        
        const isSupported = supportedSites.some(site => tab.url.includes(site));
        
        if (isSupported) {
            console.log('SocialCast: Detected supported site:', tab.url);
            
            // Inject content script if not already injected
            chrome.scripting.executeScript({
                target: { tabId: tabId },
                files: ['content.js']
            }).catch(error => {
                // Script might already be injected
                console.log('Content script injection skipped:', error);
            });
        }
    }
});

// Handle extension startup
chrome.runtime.onStartup.addListener(() => {
    console.log('SocialCast extension started');
    
    // Check backend status on startup
    checkBackendStatus().then(running => {
        if (!running) {
            console.log('SocialCast: Backend not running. Please start the backend server.');
        }
    });
});

// Handle extension shutdown
chrome.runtime.onSuspend.addListener(() => {
    console.log('SocialCast extension shutting down');
});

// Web request listener for debugging
chrome.webRequest.onBeforeRequest.addListener(
    (details) => {
        // Log requests to our backend for debugging
        if (details.url.includes('localhost:8000')) {
            console.log('SocialCast backend request:', details.url);
        }
    },
    { urls: ["http://localhost:8000/*"] }
);

// Handle errors
chrome.runtime.onSuspend.addListener(() => {
    console.log('SocialCast extension suspended');
});

// Optional: Add context menu items
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: 'socialcast-start',
        title: 'Start SocialCast Listening',
        contexts: ['page'],
        documentUrlPatterns: [
            '*://*.linkedin.com/*',
            '*://*.whatsapp.com/*',
            '*://*.instagram.com/*',
            '*://*.twitter.com/*',
            '*://*.x.com/*',
            '*://*.telegram.org/*',
            '*://*.facebook.com/*'
        ]
    });
    
    chrome.contextMenus.create({
        id: 'socialcast-stop',
        title: 'Stop SocialCast Listening',
        contexts: ['page'],
        documentUrlPatterns: [
            '*://*.linkedin.com/*',
            '*://*.whatsapp.com/*',
            '*://*.instagram.com/*',
            '*://*.twitter.com/*',
            '*://*.x.com/*',
            '*://*.telegram.org/*',
            '*://*.facebook.com/*'
        ]
    });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'socialcast-start') {
        chrome.tabs.sendMessage(tab.id, { action: 'startListening' });
    } else if (info.menuItemId === 'socialcast-stop') {
        chrome.tabs.sendMessage(tab.id, { action: 'stopListening' });
    }
});

