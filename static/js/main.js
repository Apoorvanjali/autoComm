/* ============================================
   AutoComm - Main JavaScript
   Theme Switching & Enhanced Interactions
   ============================================ */

// Theme Management
const ThemeManager = {
    init() {
        this.createThemeToggle();
        this.loadTheme();
        this.setupEventListeners();
    },

    createThemeToggle() {
        // Check if toggle already exists
        if (document.querySelector('.theme-toggle')) return;

        const toggle = document.createElement('button');
        toggle.className = 'theme-toggle';
        toggle.setAttribute('aria-label', 'Toggle theme');
        toggle.innerHTML = '<i class="fas fa-moon"></i>';
        document.body.appendChild(toggle);
    },

    loadTheme() {
        const savedTheme = localStorage.getItem('autocomm-theme') || 'light';
        this.setTheme(savedTheme, false);
    },

    setTheme(theme, save = true) {
        const html = document.documentElement;
        const toggle = document.querySelector('.theme-toggle i');

        if (theme === 'dark') {
            html.setAttribute('data-theme', 'dark');
            if (toggle) toggle.className = 'fas fa-sun';
        } else {
            html.removeAttribute('data-theme');
            if (toggle) toggle.className = 'fas fa-moon';
        }

        if (save) {
            localStorage.setItem('autocomm-theme', theme);
        }
    },

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    },

    setupEventListeners() {
        const toggle = document.querySelector('.theme-toggle');
        if (toggle) {
            toggle.addEventListener('click', () => this.toggleTheme());
        }
    }
};

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();

    // Add fade-in animation to main content
    const mainContent = document.querySelector('.container');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add ripple effect to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function (e) {
            // Remove any existing ripples first
            const existingRipples = this.querySelectorAll('.ripple');
            existingRipples.forEach(r => r.remove());

            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.style.position = 'absolute';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(255, 255, 255, 0.5)';
            ripple.style.transform = 'scale(0)';
            ripple.style.animation = 'ripple-animation 0.6s ease-out';
            ripple.style.pointerEvents = 'none';
            ripple.classList.add('ripple');

            this.appendChild(ripple);

            setTimeout(() => {
                if (ripple.parentNode) {
                    ripple.remove();
                }
            }, 600);
        });
    });

    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe cards and feature elements
    document.querySelectorAll('.card, .feature-card, .stat-item').forEach(el => {
        observer.observe(el);
    });
});

// Utility Functions
const Utils = {
    // Copy text to clipboard
    copyToClipboard(text) {
        return navigator.clipboard.writeText(text).then(() => {
            return true;
        }).catch(() => {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            const success = document.execCommand('copy');
            document.body.removeChild(textarea);
            return success;
        });
    },

    // Show toast notification
    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('show');
        }, 100);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    // Download text as file
    downloadTextFile(text, filename) {
        const blob = new Blob([text], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    },

    // Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
};

// Export for use in other scripts
window.ThemeManager = ThemeManager;
window.Utils = Utils;

// Add CSS for toast notifications
const toastStyles = document.createElement('style');
toastStyles.textContent = `
    .toast-notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--bg-card);
        color: var(--text-primary);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: var(--shadow-lg);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        z-index: 9999;
        transform: translateX(400px);
        opacity: 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-left: 4px solid;
    }
    
    .toast-notification.show {
        transform: translateX(0);
        opacity: 1;
    }
    
    .toast-notification.toast-success {
        border-left-color: var(--success);
    }
    
    .toast-notification.toast-success i {
        color: var(--success);
    }
    
    .toast-notification.toast-error {
        border-left-color: var(--danger);
    }
    
    .toast-notification.toast-error i {
        color: var(--danger);
    }
    
    .toast-notification i {
        font-size: 1.25rem;
    }
    
    @media (max-width: 768px) {
        .toast-notification {
            right: 10px;
            left: 10px;
            transform: translateY(-100px);
        }
        
        .toast-notification.show {
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(toastStyles);