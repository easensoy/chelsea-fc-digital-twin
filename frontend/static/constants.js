window.CHELSEA_CONSTANTS = {
    POSITIONS: {
        'GK': 'Goalkeeper',
        'CB': 'Centre Back',
        'LB': 'Left Back',
        'RB': 'Right Back',
        'CDM': 'Centre Defensive Midfielder',
        'CM': 'Centre Midfielder',
        'CAM': 'Centre Attacking Midfielder',
        'LM': 'Left Midfielder',
        'RM': 'Right Midfielder',
        'LW': 'Left Winger',
        'RW': 'Right Winger',
        'ST': 'Striker'
    },

    POSITION_CATEGORIES: {
        'GOALKEEPER': ['GK'],
        'DEFENDER': ['CB', 'LB', 'RB'],
        'MIDFIELDER': ['CDM', 'CM', 'CAM', 'LM', 'RM'],
        'FORWARD': ['LW', 'RW', 'ST']
    },

    FORMATIONS: [
        '4-4-2', '4-3-3', '3-5-2', '5-3-2', 
        '4-2-3-1', '3-4-3', '5-4-1', '4-5-1'
    ],

    FORMATION_STYLES: {
        'ATTACKING': ['4-3-3', '3-4-3', '4-2-3-1'],
        'DEFENSIVE': ['5-3-2', '5-4-1', '5-2-3'],
        'BALANCED': ['4-4-2', '4-5-1'],
        'COUNTER_ATTACKING': ['3-5-2']
    },

    MATCH_TYPES: {
        'LEAGUE': 'Premier League',
        'UCL': 'UEFA Champions League',
        'UEL': 'UEFA Europa League',
        'FA': 'FA Cup',
        'CARABAO': 'Carabao Cup',
        'FRIENDLY': 'Friendly',
        'TRAINING': 'Training Match'
    },

    MATCH_STATUSES: {
        'SCHEDULED': 'Scheduled',
        'LIVE': 'Live',
        'HALF_TIME': 'Half Time',
        'FULL_TIME': 'Full Time',
        'COMPLETED': 'Completed',
        'CANCELLED': 'Cancelled'
    },

    MATCH_RESULTS: {
        'WIN': 'Win',
        'DRAW': 'Draw',
        'LOSS': 'Loss'
    },

    EVENT_TYPES: {
        'GOAL': 'Goal',
        'ASSIST': 'Assist',
        'YELLOW_CARD': 'Yellow Card',
        'RED_CARD': 'Red Card',
        'SUBSTITUTION': 'Substitution',
        'CORNER': 'Corner',
        'OFFSIDE': 'Offside',
        'FOUL': 'Foul',
        'PENALTY': 'Penalty',
        'SAVE': 'Save',
        'INJURY': 'Injury'
    },

    RATING_THRESHOLDS: {
        'EXCELLENT': 8.5,
        'VERY_GOOD': 7.5,
        'GOOD': 6.5,
        'AVERAGE': 5.5,
        'POOR': 4.5,
        'VERY_POOR': 0.0
    },

    FITNESS_LEVELS: {
        'EXCELLENT': { min: 90, max: 100 },
        'GOOD': { min: 80, max: 89 },
        'AVERAGE': { min: 70, max: 79 },
        'POOR': { min: 60, max: 69 },
        'CRITICAL': { min: 0, max: 59 }
    },

    ANALYTICS_TYPES: {
        'PLAYER_PERFORMANCE': 'Player Performance',
        'FORMATION_EFFECTIVENESS': 'Formation Effectiveness',
        'TACTICAL_ANALYSIS': 'Tactical Analysis',
        'OPPOSITION_ANALYSIS': 'Opposition Analysis',
        'TREND_ANALYSIS': 'Trend Analysis',
        'PREDICTION': 'Prediction'
    },

    CHART_TYPES: {
        'LINE': 'line',
        'BAR': 'bar',
        'PIE': 'pie',
        'DOUGHNUT': 'doughnut',
        'SCATTER': 'scatter',
        'RADAR': 'radar',
        'POLAR_AREA': 'polarArea'
    },

    COLOURS: {
        PRIMARY: '#1f4e79',
        SECONDARY: '#3d85c6',
        SUCCESS: '#28a745',
        WARNING: '#ffc107',
        DANGER: '#dc3545',
        INFO: '#17a2b8',
        LIGHT: '#f8f9fa',
        DARK: '#343a40',
        WHITE: '#ffffff',
        BLACK: '#000000'
    },

    CHART_COLOURS: [
        '#1f4e79', '#3d85c6', '#28a745', '#ffc107', 
        '#dc3545', '#17a2b8', '#9c27b0', '#ff9800',
        '#795548', '#607d8b'
    ],

    POSITION_COLOURS: {
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
    },

    EXPORT_FORMATS: {
        'CSV': 'csv',
        'EXCEL': 'xlsx',
        'JSON': 'json',
        'POWERBI': 'powerbi'
    },

    EXPORT_TYPES: {
        'ALL': 'all',
        'PLAYERS': 'players',
        'MATCHES': 'matches',
        'PERFORMANCE': 'performance',
        'FORMATIONS': 'formations',
        'ANALYTICS': 'analytics',
        'TEAM_STATS': 'team_stats'
    },

    CACHE_TIMEOUTS: {
        'DASHBOARD_WIDGETS': 300,
        'PLAYER_PERFORMANCE': 600,
        'FORMATION_ANALYSIS': 900,
        'MATCH_ANALYSIS': 1800,
        'LIVE_MATCH_DATA': 30,
        'CHARTS_DATA': 600
    },

    API_ENDPOINTS: {
        PLAYERS: '/api/players/',
        MATCHES: '/api/matches/',
        FORMATIONS: '/api/formations/',
        ANALYTICS: '/api/analytics/',
        LIVE_TRACKING: '/api/live-tracking/',
        DASHBOARD: '/api/dashboard/',
        EXPORTS: '/api/exports/'
    },

    PERFORMANCE_METRICS: [
        'goals', 'assists', 'passes_completed', 'passes_attempted',
        'distance_covered', 'sprints', 'tackles', 'interceptions',
        'shots_on_target', 'shots_off_target', 'fouls_committed', 'fouls_won'
    ],

    TEAM_METRICS: [
        'possession_percentage', 'pass_accuracy', 'shots_total',
        'corners', 'offsides', 'yellow_cards', 'red_cards'
    ],

    TACTICAL_CONCEPTS: {
        'HIGH_PRESS': 'High pressing intensity',
        'LOW_BLOCK': 'Defensive low block',
        'POSSESSION_BASED': 'Possession-based play',
        'COUNTER_ATTACK': 'Counter-attacking approach',
        'DIRECT_PLAY': 'Direct playing style',
        'WING_PLAY': 'Wide attacking play',
        'CENTRAL_FOCUS': 'Central area focus'
    },

    OPPOSITION_STYLES: {
        'ATTACKING': 'Attacking minded',
        'DEFENSIVE': 'Defensive minded',
        'BALANCED': 'Balanced approach',
        'COUNTER_ATTACKING': 'Counter-attacking',
        'POSSESSION': 'Possession based',
        'DIRECT': 'Direct style',
        'PHYSICAL': 'Physical approach',
        'TECHNICAL': 'Technical approach'
    },

    PERFORMANCE_BENCHMARKS: {
        'PASS_ACCURACY': {
            'EXCELLENT': 90,
            'GOOD': 85,
            'AVERAGE': 80,
            'POOR': 75
        },
        'SHOT_ACCURACY': {
            'EXCELLENT': 50,
            'GOOD': 40,
            'AVERAGE': 30,
            'POOR': 20
        },
        'TACKLE_SUCCESS': {
            'EXCELLENT': 80,
            'GOOD': 70,
            'AVERAGE': 60,
            'POOR': 50
        },
        'DISTANCE_COVERED': {
            'EXCELLENT': 12000,
            'GOOD': 10000,
            'AVERAGE': 8000,
            'POOR': 6000
        }
    },

    INJURY_CATEGORIES: {
        'MINOR': 'Minor injury (1-7 days)',
        'MODERATE': 'Moderate injury (1-4 weeks)',
        'MAJOR': 'Major injury (1-3 months)',
        'SEVERE': 'Severe injury (3+ months)'
    },

    TRAINING_INTENSITIES: {
        'LIGHT': 'Light training',
        'MODERATE': 'Moderate training',
        'INTENSE': 'Intense training',
        'MATCH_PREPARATION': 'Match preparation',
        'RECOVERY': 'Recovery session'
    },

    SEASON_PERIODS: {
        'PRE_SEASON': 'Pre-season',
        'EARLY_SEASON': 'Early season (Aug-Oct)',
        'MID_SEASON': 'Mid-season (Nov-Jan)',
        'LATE_SEASON': 'Late season (Feb-May)',
        'POST_SEASON': 'Post-season'
    },

    COMPETITION_PRIORITIES: {
        'LEAGUE': 1,
        'UCL': 1,
        'UEL': 2,
        'FA': 3,
        'CARABAO': 4,
        'FRIENDLY': 5
    },

    WEATHER_CONDITIONS: {
        'SUNNY': 'Sunny',
        'CLOUDY': 'Cloudy',
        'RAINY': 'Rainy',
        'SNOWY': 'Snowy',
        'WINDY': 'Windy',
        'HOT': 'Hot (25°C+)',
        'COLD': 'Cold (5°C-)',
        'HUMID': 'Humid'
    },

    ALERT_PRIORITIES: {
        'CRITICAL': 'critical',
        'HIGH': 'high',
        'MEDIUM': 'medium',
        'LOW': 'low',
        'INFO': 'info'
    },

    SYSTEM_LIMITS: {
        'MAX_PLAYERS_PER_SQUAD': 30,
        'MAX_SUBSTITUTIONS_PER_MATCH': 5,
        'MAX_MATCH_DURATION': 120,
        'MAX_EVENTS_PER_MATCH': 200,
        'MAX_ANALYTICS_PER_DAY': 100
    },

    DEFAULT_VALUES: {
        'PLAYER_RATING': 6.0,
        'FITNESS_LEVEL': 100,
        'POSSESSION_PERCENTAGE': 50.0,
        'PASS_ACCURACY': 80.0,
        'MATCH_ATTENDANCE': 40000
    },

    VALIDATION_PATTERNS: {
        'SQUAD_NUMBER': /^[1-9][0-9]?$/,
        'FORMATION_NAME': /^[0-9]-[0-9]-[0-9]$/,
        'SCORE': /^[0-9]+$/,
        'PERCENTAGE': /^([0-9]|[1-9][0-9]|100)$/,
        'TIME': /^([0-9]|[1-9][0-9]|1[0-1][0-9]|120)$/
    },

    DASHBOARD_REFRESH_INTERVALS: {
        'WIDGETS': 300000,
        'LIVE_MATCH': 30000,
        'CHARTS': 180000,
        'ALERTS': 120000
    },

    FILE_UPLOAD_LIMITS: {
        'MAX_SIZE_MB': 10,
        'ALLOWED_IMAGES': ['jpg', 'jpeg', 'png', 'webp'],
        'ALLOWED_DOCUMENTS': ['pdf', 'doc', 'docx', 'txt'],
        'ALLOWED_DATA': ['csv', 'xlsx', 'json']
    },

    FORMATION_COORDINATES: {
        '4-4-2': {
            'GK': { x: 50, y: 90 },
            'CB': [{ x: 35, y: 75 }, { x: 65, y: 75 }],
            'LB': { x: 15, y: 70 },
            'RB': { x: 85, y: 70 },
            'CM': [{ x: 35, y: 50 }, { x: 65, y: 50 }],
            'LM': { x: 20, y: 45 },
            'RM': { x: 80, y: 45 },
            'ST': [{ x: 40, y: 25 }, { x: 60, y: 25 }]
        },
        '4-3-3': {
            'GK': { x: 50, y: 90 },
            'CB': [{ x: 35, y: 75 }, { x: 65, y: 75 }],
            'LB': { x: 15, y: 70 },
            'RB': { x: 85, y: 70 },
            'CDM': { x: 50, y: 55 },
            'CM': [{ x: 30, y: 45 }, { x: 70, y: 45 }],
            'LW': { x: 20, y: 25 },
            'RW': { x: 80, y: 25 },
            'ST': { x: 50, y: 20 }
        },
        '3-5-2': {
            'GK': { x: 50, y: 90 },
            'CB': [{ x: 30, y: 75 }, { x: 50, y: 75 }, { x: 70, y: 75 }],
            'CDM': { x: 50, y: 60 },
            'CM': [{ x: 35, y: 45 }, { x: 65, y: 45 }],
            'LM': { x: 15, y: 40 },
            'RM': { x: 85, y: 40 },
            'ST': [{ x: 40, y: 25 }, { x: 60, y: 25 }]
        }
    },

    PITCH_DIMENSIONS: {
        'LENGTH': 105,
        'WIDTH': 68,
        'PENALTY_AREA_LENGTH': 16.5,
        'PENALTY_AREA_WIDTH': 40.3,
        'GOAL_AREA_LENGTH': 5.5,
        'GOAL_AREA_WIDTH': 18.32,
        'CENTRE_CIRCLE_RADIUS': 9.15
    },

    ERROR_MESSAGES: {
        'INVALID_FORMATION': 'Invalid formation configuration',
        'PLAYER_NOT_AVAILABLE': 'Player is not available for selection',
        'MATCH_NOT_FOUND': 'Match not found',
        'INSUFFICIENT_DATA': 'Insufficient data for analysis',
        'EXPORT_FAILED': 'Data export failed',
        'POWERBI_CONNECTION_FAILED': 'Power BI connection failed',
        'NETWORK_ERROR': 'Network connection error',
        'AUTHENTICATION_REQUIRED': 'Please log in to continue',
        'ACCESS_DENIED': 'Access denied',
        'SERVER_ERROR': 'Server error occurred'
    },

    SUCCESS_MESSAGES: {
        'DATA_EXPORTED': 'Data exported successfully',
        'FORMATION_SAVED': 'Formation saved successfully',
        'PLAYER_UPDATED': 'Player information updated',
        'MATCH_SAVED': 'Match information saved',
        'ANALYTICS_GENERATED': 'Analytics generated successfully',
        'LOGIN_SUCCESS': 'Login successful',
        'LOGOUT_SUCCESS': 'Logout successful'
    },

    UI_STATES: {
        'LOADING': 'loading',
        'SUCCESS': 'success',
        'ERROR': 'error',
        'WARNING': 'warning',
        'INFO': 'info'
    },

    BREAKPOINTS: {
        'MOBILE': 480,
        'TABLET': 768,
        'DESKTOP': 1024,
        'LARGE': 1200
    },

    ANIMATION_DURATIONS: {
        'FAST': 150,
        'NORMAL': 300,
        'SLOW': 500
    },

    TOOLTIP_DELAYS: {
        'SHOW': 500,
        'HIDE': 200
    }
};

window.getFormationCoordinates = function(formationName) {
    return window.CHELSEA_CONSTANTS.FORMATION_COORDINATES[formationName] || {};
};

window.getPositionColour = function(position) {
    return window.CHELSEA_CONSTANTS.POSITION_COLOURS[position] || '#f0f0f0';
};

window.validateSquadNumber = function(number) {
    return window.CHELSEA_CONSTANTS.VALIDATION_PATTERNS.SQUAD_NUMBER.test(number);
};

window.validateFormationName = function(name) {
    return window.CHELSEA_CONSTANTS.VALIDATION_PATTERNS.FORMATION_NAME.test(name);
};

window.getPerformanceBenchmark = function(metric, value) {
    const benchmarks = window.CHELSEA_CONSTANTS.PERFORMANCE_BENCHMARKS[metric];
    if (!benchmarks) return 'UNKNOWN';
    
    if (value >= benchmarks.EXCELLENT) return 'EXCELLENT';
    if (value >= benchmarks.GOOD) return 'GOOD';
    if (value >= benchmarks.AVERAGE) return 'AVERAGE';
    return 'POOR';
};

window.getFitnessCategory = function(level) {
    const levels = window.CHELSEA_CONSTANTS.FITNESS_LEVELS;
    
    for (const [category, range] of Object.entries(levels)) {
        if (level >= range.min && level <= range.max) {
            return category;
        }
    }
    return 'UNKNOWN';
};

window.getRatingCategory = function(rating) {
    const thresholds = window.CHELSEA_CONSTANTS.RATING_THRESHOLDS;
    
    if (rating >= thresholds.EXCELLENT) return 'EXCELLENT';
    if (rating >= thresholds.VERY_GOOD) return 'VERY_GOOD';
    if (rating >= thresholds.GOOD) return 'GOOD';
    if (rating >= thresholds.AVERAGE) return 'AVERAGE';
    if (rating >= thresholds.POOR) return 'POOR';
    return 'VERY_POOR';
};

window.isValidPosition = function(position) {
    return Object.keys(window.CHELSEA_CONSTANTS.POSITIONS).includes(position);
};

window.getPositionCategory = function(position) {
    const categories = window.CHELSEA_CONSTANTS.POSITION_CATEGORIES;
    
    for (const [category, positions] of Object.entries(categories)) {
        if (positions.includes(position)) {
            return category;
        }
    }
    return 'UNKNOWN';
};

window.getMatchTypePriority = function(matchType) {
    return window.CHELSEA_CONSTANTS.COMPETITION_PRIORITIES[matchType] || 5;
};

window.getFormationStyle = function(formationName) {
    const styles = window.CHELSEA_CONSTANTS.FORMATION_STYLES;
    
    for (const [style, formations] of Object.entries(styles)) {
        if (formations.includes(formationName)) {
            return style;
        }
    }
    return 'BALANCED';
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.CHELSEA_CONSTANTS;
}