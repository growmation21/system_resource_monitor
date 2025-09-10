// Background service worker for Chrome Extension
console.log('System Resource Monitor extension loaded');

// Handle extension installation
chrome.runtime.onInstalled.addListener((details) => {
  console.log('System Resource Monitor installed');
  
  if (details.reason === 'install') {
    // Set default settings
    chrome.storage.local.set({
      backend_url: 'http://localhost:8888',
      update_interval: 2000,
      theme: 'dark'
    });
  }
});

// Handle extension icon click (opens popup)
chrome.action.onClicked.addListener((tab) => {
  console.log('Extension icon clicked');
});

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  try {
    if (request.action === 'openWindow') {
      // Create a new window for monitoring
      chrome.windows.create({
        url: chrome.runtime.getURL('monitor.html'),
        type: 'popup',
        width: 600,
        height: 400,
        focused: true
      }).then((window) => {
        sendResponse({success: true, windowId: window.id});
      }).catch((error) => {
        console.error('Error creating monitor window:', error);
        sendResponse({success: false, error: error.message});
      });
      return true; // Keep the message channel open for async response
      
    } else if (request.action === 'openSettings') {
      // Create a new window for settings
      chrome.windows.create({
        url: chrome.runtime.getURL('settings.html'),
        type: 'popup',
        width: 800,
        height: 700,
        focused: true
      }).then((window) => {
        sendResponse({success: true, windowId: window.id});
      }).catch((error) => {
        console.error('Error creating settings window:', error);
        sendResponse({success: false, error: error.message});
      });
      return true; // Keep the message channel open for async response
      
    } else if (request.type === 'settingsUpdated') {
      // Handle settings updates - just acknowledge, storage events will handle the rest
      console.log('Settings updated:', request.settings);
      sendResponse({success: true});
      
    } else {
      sendResponse({success: false, error: 'Unknown action'});
    }
  } catch (error) {
    console.error('Error in message handler:', error);
    sendResponse({success: false, error: error.message});
  }
});
