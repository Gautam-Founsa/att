// Main JavaScript for AI Attendance System

// Initialize tooltips and popovers on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
});

// Utility function for API calls
async function apiCall(url, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error('API Call Error:', error);
        throw error;
    }
}

// Format date and time
function formatDateTime(date) {
    const options = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    };
    return new Date(date).toLocaleDateString('en-US', options);
}

// Show notification
function showNotification(message, type = 'info', duration = 3000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Add to first available container
    const container = document.querySelector('main') || document.body;
    container.insertBefore(alertDiv, container.firstChild);

    // Auto-remove after duration
    setTimeout(() => {
        alertDiv.remove();
    }, duration);
}

// Confirm dialog
function confirmDialog(message) {
    return new Promise((resolve) => {
        const result = confirm(message);
        resolve(result);
    });
}

// Load content dynamically
async function loadContent(url, containerId) {
    try {
        const response = await fetch(url);
        const html = await response.text();
        document.getElementById(containerId).innerHTML = html;
    } catch (error) {
        console.error('Error loading content:', error);
        showNotification('Error loading content', 'danger');
    }
}

// Handle form submission
function handleFormSubmit(formId, onSuccess) {
    const form = document.getElementById(formId);
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                const formData = new FormData(form);
                const response = await fetch(form.action, {
                    method: form.method,
                    body: formData
                });

                if (response.ok) {
                    if (onSuccess) {
                        onSuccess();
                    } else {
                        showNotification('Form submitted successfully', 'success');
                    }
                } else {
                    showNotification('Error submitting form', 'danger');
                }
            } catch (error) {
                console.error('Form submission error:', error);
                showNotification('Error submitting form', 'danger');
            }
        });
    }
}

// Request camera permission
async function requestCameraPermission() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: 'user' },
            audio: false 
        });
        
        // Stop the stream immediately
        stream.getTracks().forEach(track => track.stop());
        
        return true;
    } catch (error) {
        console.error('Camera permission denied:', error);
        showNotification('Camera permission denied. Please allow camera access in browser settings.', 'danger');
        return false;
    }
}

// Check if camera is available
async function isCameraAvailable() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        return devices.some(device => device.kind === 'videoinput');
    } catch (error) {
        console.error('Error checking camera availability:', error);
        return false;
    }
}

// Debounce function
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

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Export data to CSV
function exportToCSV(filename, data) {
    const csv = data.map(row => 
        Object.values(row).map(value => 
            typeof value === 'string' && value.includes(',') ? `"${value}"` : value
        ).join(',')
    ).join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Validate email
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Format currency
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

// Get URL parameter
function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    const results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

// Set URL parameter
function setUrlParameter(param, value) {
    const url = new URL(window.location);
    url.searchParams.set(param, value);
    window.history.pushState({}, '', url);
}

// Local storage wrapper
const Storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    },
    
    get: (key) => {
        try {
            const value = localStorage.getItem(key);
            return value ? JSON.parse(value) : null;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return null;
        }
    },
    
    remove: (key) => {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Error removing from localStorage:', error);
        }
    },
    
    clear: () => {
        try {
            localStorage.clear();
        } catch (error) {
            console.error('Error clearing localStorage:', error);
        }
    }
};

// Console logging wrapper
const Logger = {
    info: (message, data = null) => {
        console.log(`[INFO] ${message}`, data);
    },
    
    warn: (message, data = null) => {
        console.warn(`[WARN] ${message}`, data);
    },
    
    error: (message, error = null) => {
        console.error(`[ERROR] ${message}`, error);
    },
    
    debug: (message, data = null) => {
        if (true) { // Set to true for debugging
            console.debug(`[DEBUG] ${message}`, data);
        }
    }
};

// Document ready check
function onDocumentReady(callback) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', callback);
    } else {
        callback();
    }
}

// Page visibility API
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        Logger.info('Page hidden');
    } else {
        Logger.info('Page visible');
    }
});

// Prevent multiple form submissions
document.addEventListener('submit', (e) => {
    const form = e.target;
    const submitBtn = form.querySelector('[type="submit"]');
    
    if (submitBtn) {
        const originalText = submitBtn.textContent;
        const isDisabled = submitBtn.disabled;
        
        if (!isDisabled) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing...';
            
            setTimeout(() => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }
            }, 3000);
        }
    }
});

// Service worker registration (for future PWA support)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Uncomment when service worker is available
        // navigator.serviceWorker.register('/static/js/sw.js');
    });
}

// Export functions for global use
window.Attendance = {
    apiCall,
    formatDateTime,
    showNotification,
    confirmDialog,
    loadContent,
    handleFormSubmit,
    requestCameraPermission,
    isCameraAvailable,
    Storage,
    Logger,
    getUrlParameter,
    setUrlParameter,
    validateEmail
};