/**
 * Chrome App Background Script
 * 
 * Handles Chrome app lifecycle and window creation
 * for the System Resource Monitor.
 */

chrome.app.runtime.onLaunched.addListener(function() {
  // Window configuration
  const windowOptions = {
    id: 'systemMonitorWindow',
    innerBounds: {
      width: 300,
      height: 200,
      minWidth: 200,
      minHeight: 150,
      maxWidth: 800,
      maxHeight: 600
    },
    outerBounds: {
      left: 100,
      top: 100
    },
    frame: {
      type: 'chrome',
      color: '#2d2d2d'
    },
    alwaysOnTop: true,
    resizable: true,
    focused: true,
    visibleOnAllWorkspaces: true
  };

  // Create the app window
  chrome.app.window.create('window.html', windowOptions, function(createdWindow) {
    // Window event handlers
    createdWindow.onClosed.addListener(function() {
      console.log('System Monitor window closed');
    });

    createdWindow.onMinimized.addListener(function() {
      console.log('System Monitor window minimized');
    });

    createdWindow.onRestored.addListener(function() {
      console.log('System Monitor window restored');
    });

    // Set window properties
    createdWindow.contentWindow.addEventListener('DOMContentLoaded', function() {
      console.log('System Monitor loaded');
      
      // Connect to the Python backend
      const backendUrl = 'http://localhost:8888';
      createdWindow.contentWindow.postMessage({
        type: 'BACKEND_URL',
        url: backendUrl
      }, '*');
    });
  });
});

// Handle restart requests
chrome.app.runtime.onRestarted.addListener(function() {
  console.log('System Monitor restarted');
});

// Handle suspension
chrome.runtime.onSuspend.addListener(function() {
  console.log('System Monitor suspending');
});

// Handle suspension cancellation
chrome.runtime.onSuspendCanceled.addListener(function() {
  console.log('System Monitor suspension canceled');
});
