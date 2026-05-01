// Main application JavaScript for Online Examination Platform

// Utility functions
const utils = {
    formatTime: (seconds) => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hours > 0) {
            return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        }
        return `${minutes}:${String(secs).padStart(2, '0')}`;
    },

    showAlert: (message, type = 'info') => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const alertContainer = document.getElementById('alert-container');
        const main = document.querySelector('main');

        if (alertContainer) {
            alertContainer.innerHTML = ''; // Clear existing
            alertContainer.appendChild(alertDiv);
        } else if (main) {
            main.insertBefore(alertDiv, main.firstChild);
        }

        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    },

    clearAlerts: () => {
        const alertContainer = document.getElementById('alert-container');
        if (alertContainer) {
            alertContainer.innerHTML = '';
        }
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => alert.remove());
    },

    getCurrentUser: () => {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    },

    isAuthenticated: () => {
        return !!localStorage.getItem('access_token');
    },

    requireAuth: () => {
        if (!utils.isAuthenticated()) {
            window.location.href = '/frontend/login.html';
            return false;
        }
        return true;
    },

    logout: () => {
        try {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            localStorage.removeItem('refresh_token');
            window.location.href = '/frontend/login.html';
        } catch (e) {
            console.error('Logout error', e);
            window.location.href = '/frontend/login.html';
        }
    },

    checkAdminVisibility: () => {
        const user = utils.getCurrentUser();
        // If no user or user is not administrator
        if (!user || user.role !== 'administrator') {
            document.querySelectorAll('.admin-only').forEach(el => {
                el.style.display = 'none';
            });

            // If current page is admin-only, redirect or show denied?
            // Optional: stricter enforcement for full pages could go here.
        }
    }
};

// Make logout globally available for inline onclick handlers
window.logout = utils.logout;

// Exam Timer
class ExamTimer {
    constructor(durationSeconds, onTimeUp) {
        this.duration = durationSeconds;
        this.remaining = durationSeconds;
        this.onTimeUp = onTimeUp;
        this.interval = null;
    }

    start() {
        this.interval = setInterval(() => {
            this.remaining--;
            this.updateDisplay();

            if (this.remaining <= 0) {
                this.stop();
                if (this.onTimeUp) {
                    this.onTimeUp();
                }
            }
        }, 1000);
    }

    stop() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    }

    updateDisplay() {
        const timerElement = document.getElementById('exam-timer');
        if (timerElement) {
            timerElement.textContent = utils.formatTime(this.remaining);

            // Add warning classes
            timerElement.classList.remove('warning', 'danger');
            if (this.remaining < 300) { // Less than 5 minutes
                timerElement.classList.add('danger');
            } else if (this.remaining < 600) { // Less than 10 minutes
                timerElement.classList.add('warning');
            }
        }
    }

    getRemaining() {
        return this.remaining;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication for protected pages
    const protectedPaths = ['/frontend/exams.html', '/frontend/results.html', '/frontend/admin.html', '/frontend/grading.html'];
    const currentPath = window.location.pathname;

    if (protectedPaths.some(path => currentPath.startsWith(path))) {
        if (!utils.requireAuth()) {
            return;
        }
    }

    // Check admin visibility
    utils.checkAdminVisibility();

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-save functionality for exam forms
    const examForm = document.getElementById('exam-form');
    if (examForm) {
        let autoSaveInterval = setInterval(() => {
            // Auto-save logic would go here
        }, 30000); // Every 30 seconds

        // Clear on page unload
        window.addEventListener('beforeunload', () => {
            clearInterval(autoSaveInterval);
        });
    }
});

// Export utilities
window.utils = utils;
window.ExamTimer = ExamTimer;

