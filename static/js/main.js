/**
 * AutoComm - Main JavaScript File
 * Handles common functionality across all pages
 */

// Global variables
let currentTheme = 'light';
let notifications = [];

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('🚀 AutoComm Application Initializing...');
    
    // Initialize Bootstrap tooltips
    initializeTooltips();
    
    // Initialize theme system
    initializeTheme();
    
    // Initialize navigation
    initializeNavigation();
    
    // Initialize common form handlers
    initializeCommonFormHandlers();
    
    // Initialize animations
    initializeAnimations();
    
    // Initialize error handling
    initializeGlobalErrorHandling();
    
    console.log('✅ AutoComm Application Initialized Successfully');
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    try {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        console.log('✅ Tooltips initialized');
    } catch (error) {
        console.warn('⚠️ Tooltips initialization failed:', error);
    }
}

/**
 * Initialize theme system
 */
function initializeTheme() {
    // Get saved theme from localStorage
    const savedTheme = localStorage.getItem('autocomm-theme');
    if (savedTheme) {
        currentTheme = savedTheme;
        applyTheme(currentTheme);
    }
    
    // Add theme toggle listener if button exists
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

/**
 * Toggle between light and dark themes
 */
function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(currentTheme);
    localStorage.setItem('autocomm-theme', currentTheme);
}

/**
 * Apply theme to the document
 */
function applyTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    
    // Update theme toggle button icon
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
    }
}

/**
 * Initialize navigation features
 */
function initializeNavigation() {
    // Highlight active navigation item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
    
    // Mobile navigation auto-close
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        document.addEventListener('click', function(e) {
            if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
                if (navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            }
        });
    }
}

/**
 * Initialize common form handlers
 */
function initializeCommonFormHandlers() {
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea[data-auto-resize]');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', autoResizeTextarea);
    });
    
    // Form validation helpers
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormValidation);
    });
    
    // File upload handlers
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', handleFileUpload);
    });
}

/**
 * Auto-resize textarea based on content
 */
function autoResizeTextarea(e) {
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

/**
 * Handle form validation
 */
function handleFormValidation(e) {
    const form = e.target;
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    if (!isValid) {
        e.preventDefault();
        showNotification('Please fill in all required fields', 'error');
    }
}

/**
 * Show error message for a field
 */
function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    let errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        field.parentNode.appendChild(errorDiv);
    }
    
    errorDiv.textContent = message;
}

/**
 * Clear error message for a field
 */
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

/**
 * Handle file upload preview and validation
 */
function handleFileUpload(e) {
    const input = e.target;
    const file = input.files[0];
    
    if (!file) return;
    
    // Validate file size (default 10MB)
    const maxSize = input.dataset.maxSize ? parseInt(input.dataset.maxSize) : 10 * 1024 * 1024;
    if (file.size > maxSize) {
        showNotification(`File size must be less than ${formatFileSize(maxSize)}`, 'error');
        input.value = '';
        return;
    }
    
    // Validate file type if specified
    const allowedTypes = input.dataset.allowedTypes;
    if (allowedTypes) {
        const allowed = allowedTypes.split(',').map(type => type.trim());
        if (!allowed.some(type => file.type.includes(type))) {
            showNotification(`File type not allowed. Allowed types: ${allowedTypes}`, 'error');
            input.value = '';
            return;
        }
    }
    
    // Show file info
    showFileInfo(input, file);
}

/**
 * Show file information
 */
function showFileInfo(input, file) {
    let infoDiv = input.parentNode.querySelector('.file-info');
    if (!infoDiv) {
        infoDiv = document.createElement('div');
        infoDiv.className = 'file-info text-muted small mt-2';
        input.parentNode.appendChild(infoDiv);
    }
    
    infoDiv.innerHTML = `
        <i class="fas fa-file me-1"></i>
        <strong>${file.name}</strong> (${formatFileSize(file.size)})
    `;
}

/**
 * Format file size in human readable format
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Initialize animations
 */
function initializeAnimations() {
    // Intersection Observer for fade-in animations
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
    
    // Observe elements with animation classes
    const animatedElements = document.querySelectorAll('.animate-on-scroll, .feature-card, .stat-item');
    animatedElements.forEach(el => observer.observe(el));
    
    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', handleSmoothScroll);
    });
}

/**
 * Handle smooth scrolling for anchor links
 */
function handleSmoothScroll(e) {
    e.preventDefault();
    
    const targetId = e.target.getAttribute('href');
    const targetElement = document.querySelector(targetId);
    
    if (targetElement) {
        targetElement.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/**
 * Initialize global error handling
 */
function initializeGlobalErrorHandling() {
    // Handle uncaught errors
    window.addEventListener('error', function(e) {
        console.error('Global error caught:', e.error);
        showNotification('An unexpected error occurred. Please try again.', 'error');
    });
    
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        showNotification('An error occurred while processing your request.', 'error');
    });
}

/**
 * Show notification to user
 */
function showNotification(message, type = 'info', duration = 5000) {
    const notification = {
        id: Date.now(),
        message: message,
        type: type,
        duration: duration
    };
    
    notifications.push(notification);
    renderNotification(notification);
    
    // Auto-remove notification
    setTimeout(() => {
        removeNotification(notification.id);
    }, duration);
}

/**
 * Render notification element
 */
function renderNotification(notification) {
    // Create notification container if it doesn't exist
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    // Create notification element
    const notificationEl = document.createElement('div');
    notificationEl.className = `alert alert-${getBootstrapAlertClass(notification.type)} alert-dismissible fade show`;
    notificationEl.setAttribute('data-notification-id', notification.id);
    
    const iconClass = getNotificationIcon(notification.type);
    
    notificationEl.innerHTML = `
        <i class="fas ${iconClass} me-2"></i>
        ${notification.message}
        <button type="button" class="btn-close" onclick="removeNotification(${notification.id})"></button>
    `;
    
    container.appendChild(notificationEl);
    
    // Animate in
    setTimeout(() => {
        notificationEl.classList.add('slide-up');
    }, 10);
}

/**
 * Remove notification
 */
function removeNotification(id) {
    const notificationEl = document.querySelector(`[data-notification-id="${id}"]`);
    if (notificationEl) {
        notificationEl.style.opacity = '0';
        notificationEl.style.transform = 'translateX(100%)';
        
        setTimeout(() => {
            if (notificationEl.parentNode) {
                notificationEl.parentNode.removeChild(notificationEl);
            }
        }, 300);
    }
    
    notifications = notifications.filter(n => n.id !== id);
}

/**
 * Get Bootstrap alert class for notification type
 */
function getBootstrapAlertClass(type) {
    const classMap = {
        'success': 'success',
        'error': 'danger',
        'warning': 'warning',
        'info': 'info'
    };
    
    return classMap[type] || 'info';
}

/**
 * Get icon for notification type
 */
function getNotificationIcon(type) {
    const iconMap = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-triangle',
        'warning': 'fa-exclamation-circle',
        'info': 'fa-info-circle'
    };
    
    return iconMap[type] || 'fa-info-circle';
}

/**
 * Utility function to format text
 */
function formatText(text, options = {}) {
    if (!text) return '';
    
    let formatted = text.toString();
    
    // Trim whitespace
    if (options.trim !== false) {
        formatted = formatted.trim();
    }
    
    // Convert to title case
    if (options.titleCase) {
        formatted = formatted.replace(/\w\S*/g, (txt) => 
            txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
        );
    }
    
    // Truncate text
    if (options.maxLength && formatted.length > options.maxLength) {
        formatted = formatted.substring(0, options.maxLength) + '...';
    }
    
    return formatted;
}

/**
 * Utility function to debounce function calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Utility function to copy text to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied to clipboard!', 'success', 2000);
        return true;
    } catch (err) {
        console.error('Failed to copy text:', err);
        showNotification('Failed to copy to clipboard', 'error');
        return false;
    }
}

/**
 * Utility function to download text as file
 */
function downloadTextAsFile(text, filename = 'download.txt', mimeType = 'text/plain') {
    const blob = new Blob([text], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

/**
 * Utility function to validate email address
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Utility function to validate URL
 */
function isValidURL(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

/**
 * Utility function to format date
 */
function formatDate(date, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        ...options
    };
    
    return new Date(date).toLocaleDateString('en-US', defaultOptions);
}

/**
 * Utility function to format time
 */
function formatTime(date, options = {}) {
    const defaultOptions = {
        hour: '2-digit',
        minute: '2-digit',
        ...options
    };
    
    return new Date(date).toLocaleTimeString('en-US', defaultOptions);
}

/**
 * Utility function to check if element is in viewport
 */
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Utility function to create loading state
 */
function showLoadingState(element, loadingText = 'Loading...') {
    if (!element) return;
    
    element.dataset.originalContent = element.innerHTML;
    element.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        ${loadingText}
    `;
    element.disabled = true;
}

/**
 * Utility function to hide loading state
 */
function hideLoadingState(element) {
    if (!element || !element.dataset.originalContent) return;
    
    element.innerHTML = element.dataset.originalContent;
    element.disabled = false;
    delete element.dataset.originalContent;
}

/**
 * API Helper function for making HTTP requests
 */
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
        ...options
    };
    
    try {
        const response = await fetch(url, defaultOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else {
            return await response.blob();
        }
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Export functions for global access
window.AutoComm = {
    showNotification,
    removeNotification,
    formatText,
    debounce,
    copyToClipboard,
    downloadTextAsFile,
    isValidEmail,
    isValidURL,
    formatDate,
    formatTime,
    isInViewport,
    showLoadingState,
    hideLoadingState,
    apiRequest
};

console.log('📦 AutoComm JavaScript Library Loaded');