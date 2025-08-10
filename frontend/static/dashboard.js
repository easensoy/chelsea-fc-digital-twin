/**
 * Chelsea FC Digital Twin - Dashboard JavaScript
 * Handles dashboard functionality, widgets, and real-time updates
 */

class DashboardManager {
    constructor() {
        this.charts = {};
        this.widgets = {};
        this.refreshInterval = null;
        this.liveMatchInterval = null;
        this.updateTimers = new Map();
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.startAutoRefresh();
        this.checkLiveMatches();
    }
    
    setupEventListeners() {
        // Widget refresh buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.widget-action') || e.target.closest('.widget-action')) {
                e.preventDefault();
                const button = e.target.closest('.widget-action');
                const widget = button.closest('.widget');
                this.refreshWidget(widget.id);
            }
        });
        
        // Chart period selector
        const chartPeriodSelect = document.getElementById('chartPeriod');
        if (chartPeriodSelect) {
            chartPeriodSelect.addEventListener('change', () => {
                this.updatePerformanceChart();
            });
        }
        
        // Visibility change handling for auto-refresh
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAutoRefresh();
            } else {
                this.resumeAutoRefresh();
            }
        });
        
        // Window focus/blur for performance optimization
        window.addEventListener('focus', () => {
            this.resumeAutoRefresh();
            this.loadDashboardData();
        });
        
        window.addEventListener('blur', () => {
            this.pauseAutoRefresh();
        });
    }
    
    async loadDashboardData() {
        try {
            showLoading('Loading dashboard data...');
            
            const response = await apiClient.getDashboardWidgets();
            const widgetsData = response.data.widgets;
            
            // Update all widgets
            this.updateHeroStats(widgetsData.overview_stats);
            this.updateLiveMatchWidget(widgetsData.live_match_status);
            this.updateRecentMatchesWidget(widgetsData.recent_matches);
            this.updateTopPerformersWidget(widgetsData.top_performers);
            this.updateFormationWidget(widgetsData.formation_summary);
            this.updateFitnessWidget(widgetsData.fitness_overview);
            this.updateAlertsWidget(widgetsData.performance_alerts);
            this.updateTacticalWidget(widgetsData.tactical_insights);
            
            // Load charts
            await this.loadChartData();
            
            hideLoading();
            
            // Update last refresh time
            this.updateLastRefreshTime();
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            hideLoading();
            showToast('Failed to load dashboard data', 'error');
        }
    }
    
    async loadChartData() {
        try {
            const period = document.getElementById('chartPeriod')?.value || '30';
            const response = await apiClient.getDashboardCharts({ period });
            const chartsData = response.data.charts;
            
            this.updatePerformanceChart(chartsData.performance_overview);
            
        } catch (error) {
            console.error('Error loading chart data:', error);
        }
    }
    
    updateHeroStats(overviewStats) {
        if (!overviewStats || !overviewStats.stats) return;
        
        const stats = overviewStats.stats;
        
        this.animateCountUp('seasonWins', stats.wins || 0);
        this.animateCountUp('winRate', stats.win_rate || 0, '%');
        this.animateCountUp('goalsScored', stats.goals_scored || 0);
        this.animateCountUp('cleanSheets', stats.clean_sheets || 0);
    }
    
    updateLiveMatchWidget(liveMatchData) {
        const content = document.getElementById('liveMatchContent');
        if (!content) return;
        
        if (liveMatchData && liveMatchData.status === 'live') {
            const match = liveMatchData.match;
            content.innerHTML = this.renderLiveMatchContent(match);
            this.showLiveMatchBanner(match);
            this.startLiveMatchUpdates();
        } else if (liveMatchData && liveMatchData.status === 'upcoming') {
            content.innerHTML = this.renderUpcomingMatchContent(liveMatchData.match);
            this.hideLiveMatchBanner();
        } else {
            content.innerHTML = this.renderNoMatchContent();
            this.hideLiveMatchBanner();
        }
    }
    
    renderLiveMatchContent(match) {
        return `
            <div class="live-match-info">
                <div class="match-header">
                    <span class="live-indicator">
                        <i class="fas fa-circle" style="animation: blink 1s infinite;"></i>
                        LIVE
                    </span>
                    <span class="match-time">${match.match_time}'</span>
                </div>
                <div class="match-score">
                    <span class="team">Chelsea</span>
                    <span class="score">${match.score}</span>
                    <span class="team">${match.opponent}</span>
                </div>
                <div class="match-details">
                    <p><strong>Formation:</strong> ${match.formation}</p>
                    <p><strong>Status:</strong> ${match.status}</p>
                    <p><strong>Venue:</strong> ${match.venue}</p>
                </div>
                ${match.recent_events && match.recent_events.length > 0 ? `
                    <div class="recent-events">
                        <h4>Recent Events</h4>
                        ${match.recent_events.slice(0, 3).map(event => `
                            <div class="event-item">
                                <span class="event-time">${event.minute}'</span>
                                <span class="event-text">
                                    <i class="fas fa-${this.getEventIcon(event.event_type)}"></i>
                                    ${event.description || event.player_name}
                                </span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    renderUpcomingMatchContent(match) {
        const kickoffTime = new Date(match.datetime);
        const hoursUntil = Math.round((kickoffTime - new Date()) / (1000 * 60 * 60));
        
        return `
            <div class="no-live-match">
                <i class="fas fa-clock" style="font-size: 2rem; color: #6c757d; margin-bottom: 1rem;"></i>
                <div class="next-match">
                    <h4>Next Match</h4>
                    <p><strong>${match.opponent}</strong></p>
                    <p>${formatDate(match.datetime, 'dd/mm/yyyy hh:mm')}</p>
                    <p>${match.venue}</p>
                    <p style="color: var(--chelsea-blue); font-weight: 600;">
                        ${hoursUntil > 0 ? `In ${hoursUntil} hours` : 'Starting soon'}
                    </p>
                </div>
            </div>
        `;
    }
    
    renderNoMatchContent() {
        return `
            <div class="no-live-match">
                <i class="fas fa-calendar-alt" style="font-size: 2rem; color: #6c757d; margin-bottom: 1rem;"></i>
                <p>No matches scheduled</p>
                <p style="font-size: 0.9rem; color: #6c757d;">Check back later for upcoming fixtures</p>
            </div>
        `;
    }
    
    updateRecentMatchesWidget(recentMatchesData) {
        const content = document.getElementById('recentMatchesContent');
        if (!content) return;
        
        if (!recentMatchesData || !recentMatchesData.matches || recentMatchesData.matches.length === 0) {
            content.innerHTML = '<p style="text-align: center; color: #6c757d;">No recent matches available</p>';
            return;
        }
        
        const matchesList = recentMatchesData.matches.map(match => {
            const resultClass = match.result.toLowerCase();
            const resultIcon = utils.getResultIcon(match.result);
            
            return `
                <li class="match-item ${resultClass}">
                    <div>
                        <div class="match-opponent">
                            <i class="fas fa-${match.is_home ? 'home' : 'plane'}"></i>
                            ${match.is_home ? 'vs' : 'at'} ${match.opponent}
                        </div>
                        <div class="match-date">${match.date}</div>
                        <div class="match-venue">${match.venue}</div>
                    </div>
                    <div style="text-align: right;">
                        <div class="match-score">${match.score}</div>
                        <div style="margin-top: 0.25rem;">
                            <i class="${resultIcon}" style="color: ${utils.getResultColour(match.result)};"></i>
                        </div>
                    </div>
                </li>
            `;
        }).join('');
        
        content.innerHTML = `<ul class="match-list">${matchesList}</ul>`;
    }
    
    updateTopPerformersWidget(topPerformersData) {
        const content = document.getElementById('topPerformersContent');
        if (!content) return;
        
        if (!topPerformersData || !topPerformersData.performers || topPerformersData.performers.length === 0) {
            content.innerHTML = '<p style="text-align: center; color: #6c757d;">No performance data available</p>';
            return;
        }
        
        const performersList = topPerformersData.performers.map((performer, index) => {
            const ratingClass = this.getRatingClass(performer.average_rating);
            
            return `
                <li class="performer-item">
                    <div class="performer-info">
                        <div class="performer-number">${performer.squad_number}</div>
                        <div class="performer-details">
                            <div class="performer-name">${performer.name}</div>
                            <div class="performer-position">${performer.position}</div>
                            <div class="performer-stats">
                                <span class="performer-stat">
                                    <i class="fas fa-futbol"></i> ${performer.goals}
                                </span>
                                <span class="performer-stat">
                                    <i class="fas fa-hands-helping"></i> ${performer.assists}
                                </span>
                                <span class="performer-stat">
                                    ${performer.matches_played} matches
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="performer-rating ${ratingClass}">${performer.average_rating}</div>
                </li>
            `;
        }).join('');
        
        content.innerHTML = `<ul class="performer-list">${performersList}</ul>`;
    }
    
    updateFormationWidget(formationData) {
        const content = document.getElementById('formationContent');
        if (!content) return;
        
        if (!formationData || !formationData.summary) {
            content.innerHTML = '<p style="text-align: center; color: #6c757d;">No formation data available</p>';
            return;
        }
        
        const summary = formationData.summary;
        content.innerHTML = `
            <div class="formation-summary">
                <div class="formation-preview">
                    <div class="formation-stat">
                        <span class="formation-stat-value">${summary.most_used_formation || 'N/A'}</span>
                        <span class="formation-stat-label">Most Used</span>
                    </div>
                    <div class="formation-stat">
                        <span class="formation-stat-value">${summary.most_used_count || 0}</span>
                        <span class="formation-stat-label">Times Used</span>
                    </div>
                    <div class="formation-stat">
                        <span class="formation-stat-value">${summary.most_effective_win_rate || 0}%</span>
                        <span class="formation-stat-label">Best Win Rate</span>
                    </div>
                </div>
                <div style="margin-top: 1rem; text-align: center;">
                    <p><strong>Most Effective:</strong> ${summary.most_effective_formation || 'N/A'}</p>
                    <p style="font-size: 0.9rem; color: #6c757d; margin-top: 0.5rem;">
                        ${summary.total_formations_used || 0} formations analysed
                    </p>
                </div>
            </div>
        `;
    }
    
    updateFitnessWidget(fitnessData) {
        const content = document.getElementById('fitnessContent');
        if (!content) return;
        
        if (!fitnessData || !fitnessData.summary) {
            content.innerHTML = '<p style="text-align: center; color: #6c757d;">No fitness data available</p>';
            return;
        }
        
        const summary = fitnessData.summary;
        const availabilityColour = summary.availability_percentage >= 90 ? 'var(--success-green)' :
                                  summary.availability_percentage >= 80 ? 'var(--warning-yellow)' :
                                  'var(--danger-red)';
        
        content.innerHTML = `
            <div class="fitness-summary">
                <div class="stats-grid">
                    <div class="stat-card">
                        <span class="stat-value">${summary.total_players}</span>
                        <span class="stat-label">Total Squad</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value" style="color: var(--success-green);">${summary.available_players}</span>
                        <span class="stat-label">Available</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value" style="color: var(--danger-red);">${summary.injured_players}</span>
                        <span class="stat-label">Injured</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value" style="color: ${availabilityColour};">${summary.availability_percentage}%</span>
                        <span class="stat-label">Availability</span>
                    </div>
                </div>
                ${fitnessData.alerts && (fitnessData.alerts.injured_players.length > 0 || fitnessData.alerts.low_fitness_players.length > 0) ? `
                    <div style="margin-top: 1rem;">
                        ${fitnessData.alerts.injured_players.length > 0 ? `
                            <h4 style="color: var(--danger-red); font-size: 0.9rem; margin-bottom: 0.5rem;">
                                <i class="fas fa-exclamation-triangle"></i> Injured Players
                            </h4>
                            <ul style="list-style: none; padding: 0; margin-bottom: 1rem;">
                                ${fitnessData.alerts.injured_players.slice(0, 3).map(player => `
                                    <li style="padding: 0.25rem 0; color: var(--danger-red); font-size: 0.85rem;">
                                        <i class="fas fa-user-injured"></i>
                                        ${player.name} (${player.position})
                                    </li>
                                `).join('')}
                            </ul>
                        ` : ''}
                        ${fitnessData.alerts.low_fitness_players.length > 0 ? `
                            <h4 style="color: var(--warning-yellow); font-size: 0.9rem; margin-bottom: 0.5rem;">
                                <i class="fas fa-battery-quarter"></i> Low Fitness
                            </h4>
                            <ul style="list-style: none; padding: 0;">
                                ${fitnessData.alerts.low_fitness_players.slice(0, 2).map(player => `
                                    <li style="padding: 0.25rem 0; color: var(--warning-yellow); font-size: 0.85rem;">
                                        <i class="fas fa-battery-quarter"></i>
                                        ${player.name} (${player.fitness_level}%)
                                    </li>
                                `).join('')}
                            </ul>
                        ` : ''}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    updateAlertsWidget(alertsData) {
        const content = document.getElementById('alertsContent');
        if (!content) return;
        
        if (!alertsData || !alertsData.alerts || alertsData.alerts.length === 0) {
            content.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--success-green);">
                    <i class="fas fa-check-circle" style="font-size: 2rem; margin-bottom: 0.5rem;"></i>
                    <p>No active alerts</p>
                    <p style="font-size: 0.9rem; color: #6c757d;">All systems operating normally</p>
                </div>
            `;
            return;
        }
        
        const alertsList = alertsData.alerts.slice(0, 5).map(alert => {
            const alertIcon = this.getAlertIcon(alert.type, alert.priority);
            
            return `
                <li class="alert-item ${alert.priority}">
                    <div style="display: flex; align-items: flex-start; gap: 0.5rem;">
                        <i class="fas fa-${alertIcon}" style="margin-top: 0.125rem; flex-shrink: 0;"></i>
                        <div style="flex: 1;">
                            <div class="alert-message">${alert.message}</div>
                            ${alert.player ? `
                                <div class="alert-details">Player: ${alert.player}</div>
                            ` : ''}
                            ${alert.formation ? `
                                <div class="alert-details">Formation: ${alert.formation}</div>
                            ` : ''}
                        </div>
                    </div>
                </li>
            `;
        }).join('');
        
        const totalAlertsText = alertsData.total_alerts > 5 ? 
            `<p style="text-align: center; margin-top: 0.5rem; font-size: 0.85rem; color: #6c757d;">
                ${alertsData.total_alerts - 5} more alerts...
            </p>` : '';
        
        content.innerHTML = `
            <ul class="alert-list">${alertsList}</ul>
            ${totalAlertsText}
        `;
    }
    
    updateTacticalWidget(tacticalData) {
        const content = document.getElementById('tacticalContent');
        if (!content) return;
        
        if (!tacticalData || !tacticalData.insights || tacticalData.insights.length === 0) {
            content.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: #6c757d;">
                    <i class="fas fa-lightbulb" style="font-size: 2rem; margin-bottom: 0.5rem;"></i>
                    <p>No tactical insights available</p>
                    <p style="font-size: 0.9rem;">Insights will appear after match analysis</p>
                </div>
            `;
            return;
        }
        
        const insightsList = tacticalData.insights.map(insight => {
            const insightIcon = this.getTacticalInsightIcon(insight.category);
            
            return `
                <div style="margin-bottom: 1rem; padding: 0.75rem; background: var(--background-grey); border-radius: 6px; border-left: 4px solid var(--chelsea-blue);">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <i class="fas fa-${insightIcon}" style="color: var(--chelsea-blue);"></i>
                        <div style="font-weight: 600; color: var(--chelsea-blue);">
                            ${insight.category}
                        </div>
                    </div>
                    <div style="font-size: 0.9rem; color: #495057; line-height: 1.4;">
                        ${insight.insight}
                    </div>
                    ${insight.type ? `
                        <div style="margin-top: 0.5rem;">
                            <span class="badge badge-${this.getInsightTypeBadge(insight.type)}">${insight.type.replace('_', ' ')}</span>
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
        
        content.innerHTML = insightsList;
    }
    
    updatePerformanceChart(chartData = null) {
        const canvas = document.getElementById('performanceChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart
        if (this.charts.performance) {
            this.charts.performance.destroy();
        }
        
        if (chartData) {
            this.charts.performance = new Chart(ctx, {
                type: 'line',
                data: chartData.data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: chartData.options.plugins.title.text || 'Performance Overview'
                        },
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Goals'
                            }
                        }
                    },
                    elements: {
                        point: {
                            radius: 4,
                            hoverRadius: 6
                        },
                        line: {
                            tension: 0.4
                        }
                    }
                }
            });
        } else {
            // Load chart data if not provided
            this.loadChartData();
        }
    }
    
    // Utility methods
    animateCountUp(elementId, endValue, suffix = '') {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const startValue = parseInt(element.textContent) || 0;
        const duration = 1000;
        const stepTime = 50;
        const steps = duration / stepTime;
        const increment = (endValue - startValue) / steps;
        
        let currentValue = startValue;
        let step = 0;
        
        const timer = setInterval(() => {
            step++;
            currentValue += increment;
            
            if (step >= steps) {
                currentValue = endValue;
                clearInterval(timer);
            }
            
            element.textContent = Math.round(currentValue) + suffix;
        }, stepTime);
    }
    
    getRatingClass(rating) {
        if (rating >= 8.5) return 'excellent';
        if (rating >= 7.5) return 'good';
        if (rating >= 6.5) return 'average';
        return 'poor';
    }
    
    getEventIcon(eventType) {
        const icons = {
            'GOAL': 'futbol',
            'ASSIST': 'hands-helping',
            'YELLOW_CARD': 'square',
            'RED_CARD': 'stop',
            'SUBSTITUTION': 'exchange-alt',
            'CORNER': 'flag',
            'PENALTY': 'crosshairs',
            'SAVE': 'hand-paper',
            'INJURY': 'band-aid'
        };
        return icons[eventType] || 'circle';
    }
    
    getAlertIcon(type, priority) {
        const icons = {
            'performance_concern': 'chart-line-down',
            'injury': 'user-injured',
            'fitness_concern': 'battery-quarter',
            'formation_concern': 'chess-board'
        };
        
        if (priority === 'high' || priority === 'critical') {
            return icons[type] || 'exclamation-triangle';
        }
        return icons[type] || 'exclamation-circle';
    }
    
    getTacticalInsightIcon(category) {
        const icons = {
            'Formation Usage': 'chess-board',
            'Home/Away Performance': 'home',
            'Attacking Performance': 'arrow-up',
            'Defensive Performance': 'shield-alt',
            'Player Performance': 'user',
            'Tactical Analysis': 'brain'
        };
        return icons[category] || 'lightbulb';
    }
    
    getInsightTypeBadge(type) {
        const badges = {
            'pattern_analysis': 'info',
            'performance_concern': 'warning',
            'positive_trend': 'success',
            'tactical_pattern': 'primary'
        };
        return badges[type] || 'secondary';
    }
    
    showLiveMatchBanner(match) {
        const banner = document.getElementById('liveMatchBanner');
        const text = document.getElementById('liveMatchText');
        
        if (banner && text) {
            text.textContent = `LIVE: Chelsea vs ${match.opponent} - ${match.match_time}'`;
            banner.style.display = 'flex';
        }
    }
    
    hideLiveMatchBanner() {
        const banner = document.getElementById('liveMatchBanner');
        if (banner) {
            banner.style.display = 'none';
        }
    }
    
    // Auto-refresh functionality
    startAutoRefresh() {
        // Refresh dashboard every 5 minutes
        this.refreshInterval = setInterval(() => {
            if (!document.hidden) {
                this.loadDashboardData();
            }
        }, 300000); // 5 minutes
    }
    
    pauseAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
        if (this.liveMatchInterval) {
            clearInterval(this.liveMatchInterval);
            this.liveMatchInterval = null;
        }
    }
    
    resumeAutoRefresh() {
        if (!this.refreshInterval) {
            this.startAutoRefresh();
        }
        this.checkLiveMatches();
    }
    
    startLiveMatchUpdates() {
        // Update live match data every 30 seconds
        if (this.liveMatchInterval) {
            clearInterval(this.liveMatchInterval);
        }
        
        this.liveMatchInterval = setInterval(async () => {
            try {
                const response = await apiClient.getLiveTracking();
                const liveMatches = response.data.matches;
                
                if (liveMatches.length > 0) {
                    const liveMatch = liveMatches[0];
                    this.updateLiveMatchWidget({ status: 'live', match: liveMatch });
                } else {
                    this.hideLiveMatchBanner();
                    clearInterval(this.liveMatchInterval);
                    this.liveMatchInterval = null;
                }
            } catch (error) {
                console.error('Error updating live match:', error);
            }
        }, 30000); // 30 seconds
    }
    
    async checkLiveMatches() {
        try {
            const response = await apiClient.getLiveTracking();
            const liveMatches = response.data.matches;
            
            if (liveMatches.length > 0) {
                const liveMatch = liveMatches[0];
                this.showLiveMatchBanner(liveMatch);
                this.startLiveMatchUpdates();
            }
        } catch (error) {
            console.error('Error checking live matches:', error);
        }
    }
    
    updateLastRefreshTime() {
        const updateTime = document.getElementById('updateTime');
        if (updateTime) {
            updateTime.textContent = new Date().toLocaleTimeString('en-GB');
        }
    }
    
    // Widget refresh functionality
    async refreshWidget(widgetId) {
        try {
            const refreshButton = document.querySelector(`#${widgetId} .widget-action`);
            if (refreshButton) {
                refreshButton.style.transform = 'rotate(180deg)';
                setTimeout(() => {
                    refreshButton.style.transform = '';
                }, 300);
            }
            
            switch(widgetId) {
                case 'performanceChart':
                    await this.loadChartData();
                    break;
                default:
                    await this.loadDashboardData();
                    break;
            }
            
            showToast('Widget refreshed successfully', 'success');
            
        } catch (error) {
            console.error('Error refreshing widget:', error);
            showToast('Failed to refresh widget', 'error');
        }
    }
    
    // Cleanup
    destroy() {
        this.pauseAutoRefresh();
        
        // Destroy all charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        // Clear all timers
        this.updateTimers.forEach(timer => clearTimeout(timer));
        this.updateTimers.clear();
    }
}

// Global functions for template use
window.refreshWidget = function(widgetId) {
    if (window.dashboardManager) {
        window.dashboardManager.refreshWidget(widgetId);
    }
};

window.updatePerformanceChart = function() {
    if (window.dashboardManager) {
        window.dashboardManager.updatePerformanceChart();
    }
};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('heroStats')) {
        window.dashboardManager = new DashboardManager();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.dashboardManager) {
        window.dashboardManager.destroy();
    }
});