/**
 * Chelsea FC Digital Twin - Utility Functions
 * Common utility functions used across the application
 */

// Global utility functions
window.utils = {
    
    // Date and time utilities
    formatDate: function(dateString, format = 'dd/mm/yyyy') {
        const date = new Date(dateString);
        
        if (isNaN(date.getTime())) {
            return 'Invalid Date';
        }
        
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        
        switch (format) {
            case 'dd/mm/yyyy':
                return `${day}/${month}/${year}`;
            case 'mm/dd/yyyy':
                return `${month}/${day}/${year}`;
            case 'yyyy-mm-dd':
                return `${year}-${month}-${day}`;
            case 'dd/mm/yyyy hh:mm':
                return `${day}/${month}/${year} ${hours}:${minutes}`;
            case 'relative':
                return this.getRelativeTime(date);
            default:
                return date.toLocaleDateString('en-GB');
        }
    },
    
    getRelativeTime: function(date) {
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        const diffHours = Math.ceil(diffTime / (1000 * 60 * 60));
        const diffMinutes = Math.ceil(diffTime / (1000 * 60));
        
        if (diffMinutes < 60) {
            return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
        } else if (diffHours < 24) {
            return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
        } else if (diffDays < 7) {
            return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
        } else {
            return this.formatDate(date);
        }
    },
    
    // Number formatting utilities
    formatNumber: function(number, decimals = 0) {
        if (typeof number !== 'number') {
            return '0';
        }
        
        return number.toLocaleString('en-GB', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    },
    
    formatPercentage: function(value, decimals = 1) {
        if (typeof value !== 'number') {
            return '0%';
        }
        
        return `${value.toFixed(decimals)}%`;
    },
    
    formatCurrency: function(amount, currency = 'GBP') {
        if (typeof amount !== 'number') {
            return '£0';
        }
        
        return new Intl.NumberFormat('en-GB', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },
    
    formatRating: function(rating) {
        if (typeof rating !== 'number') {
            return '0.0';
        }
        
        return rating.toFixed(1);
    },
    
    // Position and formation utilities
    getPositionCategory: function(position) {
        const categories = {
            'GK': 'Goalkeeper',
            'CB': 'Defender',
            'LB': 'Defender',
            'RB': 'Defender',
            'CDM': 'Midfielder',
            'CM': 'Midfielder',
            'CAM': 'Midfielder',
            'LM': 'Midfielder',
            'RM': 'Midfielder',
            'LW': 'Forward',
            'RW': 'Forward',
            'ST': 'Forward'
        };
        
        return categories[position] || 'Unknown';
    },
    
    getPositionColour: function(position) {
        const colours = {
            'GK': '#ffb347',
            'CB': '#87ceeb',
            'LB': '#87ceeb',
            'RB': '#87ceeb',
            'CDM': '#98fb98',
            'CM': '#98fb98',
            'CAM': '#98fb98',
            'LM': '#98fb98',
            'RM': '#98fb98',
            'LW': '#ffb6c1',
            'RW': '#ffb6c1',
            'ST': '#ffb6c1'
        };
        
        return colours[position] || '#f0f0f0';
    },
    
    // Rating and performance utilities
    getRatingColour: function(rating) {
        if (rating >= 8.5) return '#28a745'; // Excellent - Green
        if (rating >= 7.5) return '#17a2b8'; // Very Good - Blue
        if (rating >= 6.5) return '#ffc107'; // Good - Yellow
        if (rating >= 5.5) return '#fd7e14'; // Average - Orange
        return '#dc3545'; // Poor - Red
    },
    
    getRatingDescription: function(rating) {
        if (rating >= 8.5) return 'Excellent';
        if (rating >= 7.5) return 'Very Good';
        if (rating >= 6.5) return 'Good';
        if (rating >= 5.5) return 'Average';
        return 'Poor';
    },
    
    getFitnessColour: function(fitness) {
        if (fitness >= 90) return '#28a745'; // Excellent
        if (fitness >= 80) return '#17a2b8'; // Good
        if (fitness >= 70) return '#ffc107'; // Average
        if (fitness >= 60) return '#fd7e14'; // Poor
        return '#dc3545'; // Critical
    },
    
    getFitnessDescription: function(fitness) {
        if (fitness >= 90) return 'Excellent';
        if (fitness >= 80) return 'Good';
        if (fitness >= 70) return 'Average';
        if (fitness >= 60) return 'Poor';
        return 'Critical';
    },
    
    // Form and result utilities
    getResultColour: function(result) {
        switch (result) {
            case 'WIN': return '#28a745';
            case 'DRAW': return '#ffc107';
            case 'LOSS': return '#dc3545';
            default: return '#6c757d';
        }
    },
    
    getResultIcon: function(result) {
        switch (result) {
            case 'WIN': return 'fas fa-check-circle';
            case 'DRAW': return 'fas fa-minus-circle';
            case 'LOSS': return 'fas fa-times-circle';
            default: return 'fas fa-question-circle';
        }
    },
    
    parseForm: function(formString) {
        // Parse form string like "WWDLW" into array with colours
        return formString.split('').map(result => ({
            result: result,
            colour: this.getResultColour(result === 'W' ? 'WIN' : result === 'D' ? 'DRAW' : 'LOSS'),
            icon: this.getResultIcon(result === 'W' ? 'WIN' : result === 'D' ? 'DRAW' : 'LOSS')
        }));
    },
    
    // Data validation utilities
    isValidEmail: function(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },
    
    isValidSquadNumber: function(number) {
        return number >= 1 && number <= 99;
    },
    
    isValidRating: function(rating) {
        return rating >= 0 && rating <= 10;
    },
    
    isValidPercentage: function(value) {
        return value >= 0 && value <= 100;
    },
    
    // String utilities
    capitalize: function(str) {
        if (typeof str !== 'string') return '';
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    },
    
    truncateText: function(text, maxLength = 100) {
        if (typeof text !== 'string') return '';
        if (text.length <= maxLength) return text;
        return text.substr(0, maxLength) + '...';
    },
    
    slugify: function(text) {
        return text
            .toString()
            .toLowerCase()
            .trim()
            .replace(/\s+/g, '-')
            .replace(/[^\w\-]+/g, '')
            .replace(/\-\-+/g, '-');
    },
    
    // Array utilities
    groupBy: function(array, key) {
        return array.reduce((groups, item) => {
            const group = item[key];
            if (!groups[group]) {
                groups[group] = [];
            }
            groups[group].push(item);
            return groups;
        }, {});
    },
    
    sortBy: function(array, key, direction = 'asc') {
        return array.sort((a, b) => {
            const aValue = a[key];
            const bValue = b[key];
            
            if (direction === 'asc') {
                return aValue > bValue ? 1 : -1;
            } else {
                return aValue < bValue ? 1 : -1;
            }
        });
    },
    
    // Chart utilities
    generateChartColours: function(count) {
        const baseColours = [
            '#1f4e79', '#3d85c6', '#34a853', '#fbbc04', 
            '#ea4335', '#4285f4', '#9c27b0', '#ff9800',
            '#795548', '#607d8b'
        ];
        
        const colours = [];
        for (let i = 0; i < count; i++) {
            colours.push(baseColours[i % baseColours.length]);
        }
        return colours;
    },
    
    createGradient: function(ctx, colour1, colour2) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, colour1);
        gradient.addColorStop(1, colour2);
        return gradient;
    },
    
    // Local storage utilities
    saveToStorage: function(key, data) {
        try {
            localStorage.setItem(`chelsea_fc_${key}`, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('Failed to save to storage:', error);
            return false;
        }
    },
    
    loadFromStorage: function(key) {
        try {
            const data = localStorage.getItem(`chelsea_fc_${key}`);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Failed to load from storage:', error);
            return null;
        }
    },
    
    removeFromStorage: function(key) {
        try {
            localStorage.removeItem(`chelsea_fc_${key}`);
            return true;
        } catch (error) {
            console.error('Failed to remove from storage:', error);
            return false;
        }
    },
    
    // URL utilities
    getQueryParam: function(param) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param);
    },
    
    setQueryParam: function(param, value) {
        const url = new URL(window.location);
        url.searchParams.set(param, value);
        window.history.pushState({}, '', url);
    },
    
    removeQueryParam: function(param) {
        const url = new URL(window.location);
        url.searchParams.delete(param);
        window.history.pushState({}, '', url);
    },
    
    // File utilities
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    downloadFile: function(data, filename, type = 'text/plain') {
        const blob = new Blob([data], { type });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    },
    
    // Performance utilities
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // Animation utilities
    fadeIn: function(element, duration = 300) {
        element.style.opacity = 0;
        element.style.display = 'block';
        
        const start = performance.now();
        
        function animate(currentTime) {
            const elapsed = currentTime - start;
            const progress = elapsed / duration;
            
            if (progress < 1) {
                element.style.opacity = progress;
                requestAnimationFrame(animate);
            } else {
                element.style.opacity = 1;
            }
        }
        
        requestAnimationFrame(animate);
    },
    
    fadeOut: function(element, duration = 300, callback = null) {
        const start = performance.now();
        const initialOpacity = parseFloat(window.getComputedStyle(element).opacity);
        
        function animate(currentTime) {
            const elapsed = currentTime - start;
            const progress = elapsed / duration;
            
            if (progress < 1) {
                element.style.opacity = initialOpacity * (1 - progress);
                requestAnimationFrame(animate);
            } else {
                element.style.opacity = 0;
                element.style.display = 'none';
                if (callback) callback();
            }
        }
        
        requestAnimationFrame(animate);
    },
    
    // Mathematical utilities
    calculateAverage: function(numbers) {
        if (!Array.isArray(numbers) || numbers.length === 0) return 0;
        const sum = numbers.reduce((acc, num) => acc + num, 0);
        return sum / numbers.length;
    },
    
    calculatePercentageChange: function(oldValue, newValue) {
        if (oldValue === 0) return newValue > 0 ? 100 : 0;
        return ((newValue - oldValue) / oldValue) * 100;
    },
    
    clamp: function(value, min, max) {
        return Math.min(Math.max(value, min), max);
    },
    
    // Tactical utilities
    getFormationDescription: function(formation) {
        const descriptions = {
            '4-4-2': 'Balanced formation with solid midfield and dual strikers',
            '4-3-3': 'Attacking formation with wide forwards and midfield control',
            '3-5-2': 'Defensive formation with wing-backs providing width',
            '5-3-2': 'Ultra-defensive formation prioritising clean sheets',
            '4-2-3-1': 'Possession-based formation with creative midfield',
            '3-4-3': 'High-pressing attacking formation with width'
        };
        
        return descriptions[formation] || 'Custom tactical formation';
    },
    
    calculateFormationEffectiveness: function(wins, draws, losses) {
        const totalMatches = wins + draws + losses;
        if (totalMatches === 0) return 0;
        
        const points = (wins * 3) + draws;
        const maxPoints = totalMatches * 3;
        
        return (points / maxPoints) * 100;
    },
    
    // Browser compatibility utilities
    isModernBrowser: function() {
        return 'fetch' in window && 'Promise' in window && 'localStorage' in window;
    },
    
    isMobileDevice: function() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    },
    
    isTouchDevice: function() {
        return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    },
    
    // Error handling utilities
    createErrorMessage: function(error) {
        if (typeof error === 'string') {
            return error;
        }
        
        if (error.response && error.response.data) {
            return error.response.data.message || error.response.data.error || 'An error occurred';
        }
        
        if (error.message) {
            return error.message;
        }
        
        return 'An unexpected error occurred';
    },
    
    // Validation utilities
    validateFormData: function(data, rules) {
        const errors = {};
        
        for (const field in rules) {
            const value = data[field];
            const fieldRules = rules[field];
            
            if (fieldRules.required && (!value || value.toString().trim() === '')) {
                errors[field] = `${field} is required`;
                continue;
            }
            
            if (value && fieldRules.minLength && value.toString().length < fieldRules.minLength) {
                errors[field] = `${field} must be at least ${fieldRules.minLength} characters`;
                continue;
            }
            
            if (value && fieldRules.maxLength && value.toString().length > fieldRules.maxLength) {
                errors[field] = `${field} must be no more than ${fieldRules.maxLength} characters`;
                continue;
            }
            
            if (value && fieldRules.pattern && !fieldRules.pattern.test(value)) {
                errors[field] = fieldRules.message || `${field} format is invalid`;
                continue;
            }
            
            if (value && fieldRules.custom && !fieldRules.custom(value)) {
                errors[field] = fieldRules.message || `${field} is invalid`;
            }
        }
        
        return {
            isValid: Object.keys(errors).length === 0,
            errors: errors
        };
    },
    
    // Cookie utilities
    setCookie: function(name, value, days = 7) {
        const expires = new Date();
        expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
        document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
    },
    
    getCookie: function(name) {
        const nameEQ = name + '=';
        const ca = document.cookie.split(';');
        
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        
        return null;
    },
    
    deleteCookie: function(name) {
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
    }
};

// Export utils for global use
window.getCookie = window.utils.getCookie;
window.formatDate = window.utils.formatDate;
window.formatNumber = window.utils.formatNumber;
window.formatPercentage = window.utils.formatPercentage;