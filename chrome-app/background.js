/**
 * Chrome App Background Script
 * 
 * Handles Chrome app lifecycle and window creation
 * for the System Resource Monitor.
 */

chrome.app.runtime.onLaunched.addListener(function() {
  console.log('System Monitor launching...');
  
  // Create window with default settings
  chrome.app.window.create('window.html', {
    id: 'systemMonitor',
    bounds: {
      width: 600,
      height: 400
    },
    minWidth: 400,
    minHeight: 300,
    alwaysOnTop: false,
    resizable: true
  }, function(createdWindow) {
    if (chrome.runtime.lastError) {
      console.error('Failed to create System Monitor window:', chrome.runtime.lastError);
    } else {
      console.log('System Monitor window created successfully');
    }
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
