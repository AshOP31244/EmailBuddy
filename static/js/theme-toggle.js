/**
 * Theme Toggle Handler
 * Manages dark/light mode switching with smooth transitions
 */

(function() {
  'use strict';

  // Get current theme from HTML attribute
  function getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || 'light';
  }

  // Apply theme immediately on page load (prevent flash)
  function applyStoredTheme() {
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme) {
      document.documentElement.setAttribute('data-theme', storedTheme);
    }
  }

  // Initialize theme on page load
  applyStoredTheme();

  // Wait for DOM to be ready
  document.addEventListener('DOMContentLoaded', function() {
    const desktopToggle = document.getElementById('desktopThemeToggle');
    const mobileToggle = document.getElementById('mobileThemeToggle');

    function toggleTheme() {
      const currentTheme = getCurrentTheme();
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

      // Update DOM immediately for instant feedback
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);

      // Sync with server (if user is authenticated)
      if (typeof toggleThemeUrl !== 'undefined') {
        fetch(toggleThemeUrl, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ theme: newTheme })
        }).catch(err => console.error('Failed to sync theme:', err));
      }
    }

    // Attach event listeners
    if (desktopToggle) {
      desktopToggle.addEventListener('click', toggleTheme);
    }

    if (mobileToggle) {
      mobileToggle.addEventListener('click', toggleTheme);
    }

    // Keyboard shortcut: Ctrl/Cmd + Shift + D
    document.addEventListener('keydown', function(e) {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        toggleTheme();
      }
    });
  });

  // Helper function to get CSRF token
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
})();