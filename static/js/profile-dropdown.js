/**
 * Profile Dropdown Handler
 * Manages the profile menu dropdown functionality
 */

(function() {
  'use strict';

  document.addEventListener('DOMContentLoaded', function() {
    const profileBtn = document.getElementById('profileBtn');
    const profileDropdown = document.getElementById('profileDropdown');

    if (!profileBtn || !profileDropdown) {
      return; // Exit if elements don't exist
    }

    // Toggle dropdown on button click
    profileBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      profileDropdown.classList.toggle('show');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
      if (!profileDropdown.contains(e.target) && e.target !== profileBtn) {
        profileDropdown.classList.remove('show');
      }
    });

    // Prevent dropdown from closing when clicking inside
    profileDropdown.addEventListener('click', function(e) {
      e.stopPropagation();
    });

    // Close dropdown on ESC key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        profileDropdown.classList.remove('show');
      }
    });
  });
})();