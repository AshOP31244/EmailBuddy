/**
 * PWA Installation Handler
 * Manages Progressive Web App installation prompts and events
 */

(function() {
  'use strict';

  let deferredPrompt;
  let installBtn = null;

  // Wait for DOM
  document.addEventListener('DOMContentLoaded', function() {
    installBtn = document.getElementById('installBtn');
  });

  // Capture the beforeinstallprompt event
  window.addEventListener('beforeinstallprompt', function(e) {
    console.log('PWA: beforeinstallprompt event fired');
    
    // Prevent the mini-infobar from appearing on mobile
    e.preventDefault();
    
    // Stash the event so it can be triggered later
    deferredPrompt = e;
    
    // Show install button if it exists
    if (installBtn) {
      installBtn.style.display = 'inline-flex';
    }

    // Show subtle notification in navbar (optional)
    showInstallNotification();
  });

  // Handle install button click
  if (installBtn) {
    installBtn.addEventListener('click', async function() {
      if (!deferredPrompt) {
        console.log('PWA: No deferred prompt available');
        return;
      }

      // Show the install prompt
      deferredPrompt.prompt();

      // Wait for the user to respond to the prompt
      const { outcome } = await deferredPrompt.userChoice;
      
      console.log(`PWA: User response to install prompt: ${outcome}`);

      if (outcome === 'accepted') {
        console.log('PWA: User accepted the install prompt');
      } else {
        console.log('PWA: User dismissed the install prompt');
      }

      // Clear the deferredPrompt
      deferredPrompt = null;

      // Hide the install button
      if (installBtn) {
        installBtn.style.display = 'none';
      }
    });
  }

  // Handle successful installation
  window.addEventListener('appinstalled', function() {
    console.log('PWA: App installed successfully');
    
    // Clear the deferredPrompt
    deferredPrompt = null;

    // Hide install button
    if (installBtn) {
      installBtn.style.display = 'none';
    }

    // Show success message (optional)
    showInstallSuccessMessage();
  });

  // Check if app is running in standalone mode
  function isStandalone() {
    return (
      window.matchMedia('(display-mode: standalone)').matches ||
      window.navigator.standalone === true
    );
  }

  // Log PWA status
  if (isStandalone()) {
    console.log('PWA: Running in standalone mode');
  } else {
    console.log('PWA: Running in browser mode');
  }

  // Optional: Show install notification
  function showInstallNotification() {
    // You can add a small badge or notification here
    // For now, we'll just log it
    console.log('PWA: Install prompt is available');
  }

  // Optional: Show success message after install
  function showInstallSuccessMessage() {
    // You can show a toast notification here
    console.log('PWA: Installation complete!');
  }
})();