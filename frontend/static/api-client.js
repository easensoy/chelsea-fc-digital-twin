/**
 * Chelsea FC Digital Twin - API Client
 * Handles all API communication with the Django backend
 */

class APIClient {
    constructor() {
        this.baseURL = '/api';
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        };
        
        // Setup axios interceptors
        this.setupInterceptors();
    }

    setupInterceptors() {
        // Request interceptor to add CSRF token
        axios.interceptors.request.use(
            (config) => {
                const csrfToken = this.getCSRFToken();
                if (csrfToken) {
                    config.headers['X-CSRFToken'] = csrfToken;
                }
                return config;
            },
            (error) => {
                return Promise.reject(error);
            }
        );

        // Response interceptor for error handling
        axios.interceptors.response.use(
            (response) => {
                return response;
            },
            (error) => {
                this.handleAPIError(error);
                return Promise.reject(error);
            }
        );
    }

    getCSRFToken() {
        const name = 'csrftoken';
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

    handleAPIError(error) {
        if (error.response) {
            const status = error.response.status;
            const message = error.response.data?.message || error.response.data?.error || 'API request failed';
            
            switch (status) {
                case 401:
                    console.error('Authentication required');
                    if (window.location.pathname !== '/login/') {
                        window.location.href = '/login/';
                    }
                    break;
                case 403:
                    console.error('Access forbidden');
                    showToast('Access denied', 'error');
                    break;
                case 404:
                    console.error('Resource not found');
                    showToast('Resource not found', 'error');
                    break;
                case 500:
                    console.error('Server error');
                    showToast('Server error occurred', 'error');
                    break;
                default:
                    console.error('API Error:', message);
                    showToast(message, 'error');
            }
        } else if (error.request) {
            console.error('Network error');
            showToast('Network connection error', 'error');
        } else {
            console.error('Request setup error:', error.message);
            showToast('Request failed', 'error');
        }
    }

    // Generic HTTP methods
    async get(endpoint, params = {}) {
        try {
            const url = `${this.baseURL}${endpoint}`;
            const response = await axios.get(url, { 
                params,
                headers: this.defaultHeaders 
            });
            return response;
        } catch (error) {
            throw error;
        }
    }

    async post(endpoint, data = {}) {
        try {
            const url = `${this.baseURL}${endpoint}`;
            const response = await axios.post(url, data, {
                headers: this.defaultHeaders
            });
            return response;
        } catch (error) {
            throw error;
        }
    }

    async put(endpoint, data = {}) {
        try {
            const url = `${this.baseURL}${endpoint}`;
            const response = await axios.put(url, data, {
                headers: this.defaultHeaders
            });
            return response;
        } catch (error) {
            throw error;
        }
    }

    async patch(endpoint, data = {}) {
        try {
            const url = `${this.baseURL}${endpoint}`;
            const response = await axios.patch(url, data, {
                headers: this.defaultHeaders
            });
            return response;
        } catch (error) {
            throw error;
        }
    }

    async delete(endpoint) {
        try {
            const url = `${this.baseURL}${endpoint}`;
            const response = await axios.delete(url, {
                headers: this.defaultHeaders
            });
            return response;
        } catch (error) {
            throw error;
        }
    }

    // Player API methods
    async getPlayers(params = {}) {
        return this.get('/players/', params);
    }

    async getPlayer(playerId) {
        return this.get(`/players/${playerId}/`);
    }

    async updatePlayer(playerId, data) {
        return this.patch(`/players/${playerId}/`, data);
    }

    async getPlayerPerformance(playerId, params = {}) {
        return this.get(`/players/${playerId}/performance/`, params);
    }

    async getPlayerFitness(playerId) {
        return this.get(`/players/${playerId}/fitness/`);
    }

    // Match API methods
    async getMatches(params = {}) {
        return this.get('/matches/', params);
    }

    async getMatch(matchId) {
        return this.get(`/matches/${matchId}/`);
    }

    async updateMatch(matchId, data) {
        return this.patch(`/matches/${matchId}/`, data);
    }

    async getMatchAnalysis(matchId) {
        return this.get(`/matches/${matchId}/analysis/`);
    }

    async updateLiveMatch(matchId, data) {
        return this.post(`/matches/${matchId}/update_live/`, data);
    }

    async getMatchEvents(matchId) {
        return this.get(`/match/${matchId}/events/`);
    }

    async addMatchEvent(matchId, eventData) {
        return this.post(`/match/${matchId}/events/`, eventData);
    }

    async getMatchLineup(matchId) {
        return this.get(`/match/${matchId}/lineup/`);
    }

    // Formation API methods
    async getFormations(params = {}) {
        return this.get('/formations/', params);
    }

    async getFormation(formationId) {
        return this.get(`/formations/${formationId}/`);
    }

    async createFormation(data) {
        return this.post('/formations/', data);
    }

    async updateFormation(formationId, data) {
        return this.patch(`/formations/${formationId}/`, data);
    }

    async getFormationEffectiveness(formationId) {
        return this.get(`/formations/${formationId}/effectiveness/`);
    }

    async getFormationRecommendations(params = {}) {
        return this.get('/formation-recommendations/', params);
    }

    // Analytics API methods
    async getAnalytics(params = {}) {
        return this.get('/analytics/', params);
    }

    async createAnalytics(data) {
        return this.post('/analytics/', data);
    }

    async getTacticalInsights() {
        return this.get('/tactical-insights/');
    }

    async getPerformanceTrends(params = {}) {
        return this.get('/performance-trends/', params);
    }

    // Live tracking API methods
    async getLiveTracking() {
        return this.get('/live-tracking/');
    }

    async recordLiveEvent(data) {
        return this.post('/live-tracking/', data);
    }

    async updateLiveMatchData(matchId, data) {
        return this.post(`/match/${matchId}/live-update/`, data);
    }

    // Dashboard API methods
    async getDashboardWidgets() {
        return this.get('/dashboard/widgets/');
    }

    async getDashboardCharts(params = {}) {
        return this.get('/dashboard/charts/', params);
    }

    // Export API methods
    async exportToPowerBI(data) {
        return this.post('/exports/powerbi/', data);
    }

    async exportToCSV(data) {
        return this.post('/exports/csv/', data);
    }

    async exportToExcel(data) {
        return this.post('/exports/excel/', data);
    }

    async scheduleExport(data) {
        return this.post('/exports/schedule/', data);
    }

    // Player stats API methods
    async getPlayerStats(params = {}) {
        return this.get('/player-stats/', params);
    }

    async updatePlayerStats(statsId, data) {
        return this.patch(`/player-stats/${statsId}/`, data);
    }

    // Team stats API methods
    async getTeamStats(params = {}) {
        return this.get('/team-stats/', params);
    }

    async updateTeamStats(statsId, data) {
        return this.patch(`/team-stats/${statsId}/`, data);
    }

    // Opponent API methods
    async getOpponents(params = {}) {
        return this.get('/opponents/', params);
    }

    async getOpponent(opponentId) {
        return this.get(`/opponents/${opponentId}/`);
    }

    async getOpponentScoutReport(opponentId) {
        return this.get(`/opponents/${opponentId}/scout_report/`);
    }

    // Utility methods for file downloads
    async downloadFile(endpoint, filename) {
        try {
            const response = await axios({
                method: 'POST',
                url: `${this.baseURL}${endpoint}`,
                headers: {
                    ...this.defaultHeaders,
                    'X-CSRFToken': this.getCSRFToken()
                },
                responseType: 'blob'
            });

            // Create blob link to download
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            return { success: true };
        } catch (error) {
            throw error;
        }
    }

    // Upload methods
    async uploadFile(endpoint, file, onProgress = null) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const config = {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'X-CSRFToken': this.getCSRFToken()
                }
            };

            if (onProgress) {
                config.onUploadProgress = (progressEvent) => {
                    const percentCompleted = Math.round(
                        (progressEvent.loaded * 100) / progressEvent.total
                    );
                    onProgress(percentCompleted);
                };
            }

            const response = await axios.post(
                `${this.baseURL}${endpoint}`,
                formData,
                config
            );

            return response;
        } catch (error) {
            throw error;
        }
    }

    // Bulk operations
    async bulkUpdatePlayers(updates) {
        return this.post('/players/bulk_update/', { updates });
    }

    async bulkUpdateStats(updates) {
        return this.post('/player-stats/bulk_update/', { updates });
    }

    // Search and filtering
    async searchPlayers(query, filters = {}) {
        const params = { search: query, ...filters };
        return this.get('/players/', params);
    }

    async searchMatches(query, filters = {}) {
        const params = { search: query, ...filters };
        return this.get('/matches/', params);
    }

    // Real-time data polling
    startPolling(endpoint, callback, interval = 30000) {
        const poll = async () => {
            try {
                const response = await this.get(endpoint);
                callback(response.data);
            } catch (error) {
                console.error('Polling error:', error);
            }
        };

        // Initial call
        poll();

        // Set up interval
        const intervalId = setInterval(poll, interval);

        // Return function to stop polling
        return () => clearInterval(intervalId);
    }

    // Cache management
    clearCache() {
        // Clear any cached data if using local storage
        if (typeof(Storage) !== 'undefined') {
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith('chelsea_fc_cache_')) {
                    localStorage.removeItem(key);
                }
            });
        }
    }

    // Health check
    async healthCheck() {
        try {
            const response = await this.get('/health/');
            return response.data;
        } catch (error) {
            return { status: 'error', message: 'API not responding' };
        }
    }

    // Authentication helpers
    async login(username, password) {
        try {
            const response = await axios.post('/login/', {
                username,
                password
            }, {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            return response;
        } catch (error) {
            throw error;
        }
    }

    async logout() {
        try {
            const response = await axios.post('/logout/', {}, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            return response;
        } catch (error) {
            throw error;
        }
    }
}

// Create global API client instance
const apiClient = new APIClient();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIClient;
}