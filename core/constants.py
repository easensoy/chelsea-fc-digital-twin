# Player position constants
PLAYER_POSITIONS = {
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
}

POSITION_CATEGORIES = {
    'GOALKEEPER': ['GK'],
    'DEFENDER': ['CB', 'LB', 'RB'],
    'MIDFIELDER': ['CDM', 'CM', 'CAM', 'LM', 'RM'],
    'FORWARD': ['LW', 'RW', 'ST']
}

# Formation constants
VALID_FORMATIONS = [
    '4-4-2', '4-3-3', '3-5-2', '5-3-2', 
    '4-2-3-1', '3-4-3', '5-4-1', '4-5-1'
]

FORMATION_STYLES = {
    'ATTACKING': ['4-3-3', '3-4-3', '4-2-3-1'],
    'DEFENSIVE': ['5-3-2', '5-4-1', '5-2-3'],
    'BALANCED': ['4-4-2', '4-5-1'],
    'COUNTER_ATTACKING': ['3-5-2']
}

FORMATION_REQUIREMENTS = {
    '4-4-2': {
        'GK': 1, 'CB': 2, 'LB': 1, 'RB': 1, 
        'CM': 2, 'LM': 1, 'RM': 1, 'ST': 2
    },
    '4-3-3': {
        'GK': 1, 'CB': 2, 'LB': 1, 'RB': 1, 
        'CDM': 1, 'CM': 2, 'LW': 1, 'RW': 1, 'ST': 1
    },
    '3-5-2': {
        'GK': 1, 'CB': 3, 'CDM': 1, 'CM': 2, 
        'LM': 1, 'RM': 1, 'ST': 2
    },
    '5-3-2': {
        'GK': 1, 'CB': 3, 'LB': 1, 'RB': 1, 
        'CDM': 1, 'CM': 2, 'ST': 2
    },
    '4-2-3-1': {
        'GK': 1, 'CB': 2, 'LB': 1, 'RB': 1, 
        'CDM': 2, 'CAM': 1, 'LM': 1, 'RM': 1, 'ST': 1
    },
    '3-4-3': {
        'GK': 1, 'CB': 3, 'CDM': 1, 'CM': 2, 
        'CAM': 1, 'LW': 1, 'RW': 1, 'ST': 1
    }
}

# Match constants
MATCH_TYPES = {
    'LEAGUE': 'Premier League',
    'UCL': 'UEFA Champions League',
    'UEL': 'UEFA Europa League',
    'FA': 'FA Cup',
    'CARABAO': 'Carabao Cup',
    'FRIENDLY': 'Friendly',
    'TRAINING': 'Training Match'
}

MATCH_STATUSES = {
    'SCHEDULED': 'Scheduled',
    'LIVE': 'Live',
    'HALF_TIME': 'Half Time',
    'FULL_TIME': 'Full Time',
    'COMPLETED': 'Completed',
    'CANCELLED': 'Cancelled'
}

MATCH_RESULTS = {
    'WIN': 'Win',
    'DRAW': 'Draw',
    'LOSS': 'Loss'
}

# Event types
EVENT_TYPES = {
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
}

# Performance metrics
PERFORMANCE_METRICS = {
    'PLAYER_STATS': [
        'goals', 'assists', 'passes_completed', 'passes_attempted',
        'distance_covered', 'sprints', 'tackles', 'interceptions',
        'shots_on_target', 'shots_off_target', 'fouls_committed', 'fouls_won'
    ],
    'TEAM_STATS': [
        'possession_percentage', 'pass_accuracy', 'shots_total',
        'corners', 'offsides', 'yellow_cards', 'red_cards'
    ]
}

# Rating thresholds
RATING_THRESHOLDS = {
    'EXCELLENT': 8.5,
    'VERY_GOOD': 7.5,
    'GOOD': 6.5,
    'AVERAGE': 5.5,
    'POOR': 4.5,
    'VERY_POOR': 0.0
}

RATING_DESCRIPTIONS = {
    'EXCELLENT': 'Excellent performance',
    'VERY_GOOD': 'Very good performance',
    'GOOD': 'Good performance',
    'AVERAGE': 'Average performance',
    'POOR': 'Poor performance',
    'VERY_POOR': 'Very poor performance'
}

# Fitness levels
FITNESS_LEVELS = {
    'EXCELLENT': (90, 100),
    'GOOD': (80, 89),
    'AVERAGE': (70, 79),
    'POOR': (60, 69),
    'CRITICAL': (0, 59)
}

FITNESS_DESCRIPTIONS = {
    'EXCELLENT': 'Excellent fitness - ready for full match',
    'GOOD': 'Good fitness - suitable for most situations',
    'AVERAGE': 'Average fitness - monitor during match',
    'POOR': 'Poor fitness - limited playing time recommended',
    'CRITICAL': 'Critical fitness - rest required'
}

# Analytics types
ANALYTICS_TYPES = {
    'PLAYER_PERFORMANCE': 'Player Performance',
    'FORMATION_EFFECTIVENESS': 'Formation Effectiveness',
    'TACTICAL_ANALYSIS': 'Tactical Analysis',
    'OPPOSITION_ANALYSIS': 'Opposition Analysis',
    'TREND_ANALYSIS': 'Trend Analysis',
    'PREDICTION': 'Prediction'
}

# Dashboard constants
DASHBOARD_WIDGETS = {
    'OVERVIEW_STATS': 'overview_stats',
    'RECENT_MATCHES': 'recent_matches',
    'TOP_PERFORMERS': 'top_performers',
    'FORMATION_SUMMARY': 'formation_summary',
    'LIVE_MATCH_STATUS': 'live_match_status',
    'FITNESS_OVERVIEW': 'fitness_overview',
    'UPCOMING_FIXTURES': 'upcoming_fixtures',
    'PERFORMANCE_ALERTS': 'performance_alerts',
    'TACTICAL_INSIGHTS': 'tactical_insights',
    'SQUAD_AVAILABILITY': 'squad_availability'
}

# Chart types
CHART_TYPES = {
    'LINE': 'line',
    'BAR': 'bar',
    'PIE': 'pie',
    'DOUGHNUT': 'doughnut',
    'SCATTER': 'scatter',
    'RADAR': 'radar',
    'POLAR_AREA': 'polarArea'
}

# Colour schemes
COLOUR_SCHEMES = {
    'CHELSEA_BLUE': '#1f4e79',
    'LIGHT_BLUE': '#3d85c6',
    'SUCCESS_GREEN': '#34a853',
    'WARNING_YELLOW': '#fbbc04',
    'DANGER_RED': '#ea4335',
    'INFO_BLUE': '#4285f4',
    'LIGHT_GREY': '#f8f9fa',
    'DARK_GREY': '#343a40',
    'WHITE': '#ffffff',
    'BLACK': '#000000'
}

CHART_COLOUR_PALETTE = [
    '#1f4e79', '#3d85c6', '#34a853', '#fbbc04', 
    '#ea4335', '#4285f4', '#9c27b0', '#ff9800',
    '#795548', '#607d8b'
]

# Export formats
EXPORT_FORMATS = {
    'CSV': 'csv',
    'EXCEL': 'xlsx',
    'JSON': 'json',
    'POWERBI': 'powerbi'
}

EXPORT_TYPES = {
    'ALL': 'all',
    'PLAYERS': 'players',
    'MATCHES': 'matches',
    'PERFORMANCE': 'performance',
    'FORMATIONS': 'formations',
    'ANALYTICS': 'analytics',
    'TEAM_STATS': 'team_stats'
}

# Cache timeouts (in seconds)
CACHE_TIMEOUTS = {
    'DASHBOARD_WIDGETS': 300,      # 5 minutes
    'PLAYER_PERFORMANCE': 600,     # 10 minutes
    'FORMATION_ANALYSIS': 900,     # 15 minutes
    'MATCH_ANALYSIS': 1800,        # 30 minutes
    'LIVE_MATCH_DATA': 30,         # 30 seconds
    'CHARTS_DATA': 600,            # 10 minutes
    'POWERBI_TOKEN': 3300          # 55 minutes (expires in 1 hour)
}

# API pagination
API_PAGINATION = {
    'DEFAULT_PAGE_SIZE': 50,
    'MAX_PAGE_SIZE': 200,
    'PAGE_SIZE_QUERY_PARAM': 'page_size'
}

# File upload constraints
FILE_UPLOAD_CONSTRAINTS = {
    'MAX_FILE_SIZE': 10 * 1024 * 1024,  # 10MB
    'ALLOWED_IMAGE_FORMATS': ['jpg', 'jpeg', 'png', 'webp'],
    'ALLOWED_DOCUMENT_FORMATS': ['pdf', 'doc', 'docx', 'txt'],
    'ALLOWED_DATA_FORMATS': ['csv', 'xlsx', 'json']
}

# Tactical constants
TACTICAL_CONCEPTS = {
    'HIGH_PRESS': 'High pressing intensity',
    'LOW_BLOCK': 'Defensive low block',
    'POSSESSION_BASED': 'Possession-based play',
    'COUNTER_ATTACK': 'Counter-attacking approach',
    'DIRECT_PLAY': 'Direct playing style',
    'WING_PLAY': 'Wide attacking play',
    'CENTRAL_FOCUS': 'Central area focus'
}

TACTICAL_PHASES = {
    'ATTACK': 'Attacking phase',
    'DEFENCE': 'Defensive phase',
    'TRANSITION_TO_ATTACK': 'Transition to attack',
    'TRANSITION_TO_DEFENCE': 'Transition to defence',
    'SET_PIECES': 'Set pieces',
    'PRESSING': 'Pressing phase'
}

# Opposition analysis
OPPOSITION_STYLES = {
    'ATTACKING': 'Attacking minded',
    'DEFENSIVE': 'Defensive minded',
    'BALANCED': 'Balanced approach',
    'COUNTER_ATTACKING': 'Counter-attacking',
    'POSSESSION': 'Possession based',
    'DIRECT': 'Direct style',
    'PHYSICAL': 'Physical approach',
    'TECHNICAL': 'Technical approach'
}

# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
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
        'EXCELLENT': 12000,  # metres per match
        'GOOD': 10000,
        'AVERAGE': 8000,
        'POOR': 6000
    }
}

# Injury categories
INJURY_CATEGORIES = {
    'MINOR': 'Minor injury (1-7 days)',
    'MODERATE': 'Moderate injury (1-4 weeks)',
    'MAJOR': 'Major injury (1-3 months)',
    'SEVERE': 'Severe injury (3+ months)'
}

# Training intensities
TRAINING_INTENSITIES = {
    'LIGHT': 'Light training',
    'MODERATE': 'Moderate training',
    'INTENSE': 'Intense training',
    'MATCH_PREPARATION': 'Match preparation',
    'RECOVERY': 'Recovery session'
}

# Season periods
SEASON_PERIODS = {
    'PRE_SEASON': 'Pre-season',
    'EARLY_SEASON': 'Early season (Aug-Oct)',
    'MID_SEASON': 'Mid-season (Nov-Jan)',
    'LATE_SEASON': 'Late season (Feb-May)',
    'POST_SEASON': 'Post-season'
}

# Competition priorities
COMPETITION_PRIORITIES = {
    'LEAGUE': 1,
    'UCL': 1,
    'UEL': 2,
    'FA': 3,
    'CARABAO': 4,
    'FRIENDLY': 5
}

# Weather conditions
WEATHER_CONDITIONS = {
    'SUNNY': 'Sunny',
    'CLOUDY': 'Cloudy',
    'RAINY': 'Rainy',
    'SNOWY': 'Snowy',
    'WINDY': 'Windy',
    'HOT': 'Hot (25°C+)',
    'COLD': 'Cold (5°C-)',
    'HUMID': 'Humid'
}

# Pitch conditions
PITCH_CONDITIONS = {
    'EXCELLENT': 'Excellent',
    'GOOD': 'Good',
    'FAIR': 'Fair',
    'POOR': 'Poor',
    'WET': 'Wet',
    'FROZEN': 'Frozen'
}

# Data quality indicators
DATA_QUALITY_THRESHOLDS = {
    'EXCELLENT': 95,
    'GOOD': 85,
    'FAIR': 75,
    'POOR': 65,
    'CRITICAL': 0
}

# Alert priorities
ALERT_PRIORITIES = {
    'CRITICAL': 'critical',
    'HIGH': 'high',
    'MEDIUM': 'medium',
    'LOW': 'low',
    'INFO': 'info'
}

# System limits
SYSTEM_LIMITS = {
    'MAX_PLAYERS_PER_SQUAD': 30,
    'MAX_SUBSTITUTIONS_PER_MATCH': 5,
    'MAX_MATCH_DURATION': 120,  # minutes including extra time
    'MAX_EVENTS_PER_MATCH': 200,
    'MAX_ANALYTICS_PER_DAY': 100
}

# Default values
DEFAULT_VALUES = {
    'PLAYER_RATING': 6.0,
    'FITNESS_LEVEL': 100,
    'POSSESSION_PERCENTAGE': 50.0,
    'PASS_ACCURACY': 80.0,
    'MATCH_ATTENDANCE': 40000
}

# API rate limits
API_RATE_LIMITS = {
    'REQUESTS_PER_MINUTE': 60,
    'REQUESTS_PER_HOUR': 1000,
    'REQUESTS_PER_DAY': 10000
}

# Validation patterns
VALIDATION_PATTERNS = {
    'SQUAD_NUMBER': r'^[1-9][0-9]?$',  # 1-99
    'FORMATION_NAME': r'^[0-9]-[0-9]-[0-9]$',  # e.g., 4-3-3
    'SCORE': r'^[0-9]+$',  # Non-negative integers
    'PERCENTAGE': r'^([0-9]|[1-9][0-9]|100)$',  # 0-100
    'TIME': r'^([0-9]|[1-9][0-9]|1[0-1][0-9]|120)$'  # 0-120 minutes
}

# Error messages
ERROR_MESSAGES = {
    'INVALID_FORMATION': 'Invalid formation configuration',
    'PLAYER_NOT_AVAILABLE': 'Player is not available for selection',
    'MATCH_NOT_FOUND': 'Match not found',
    'INSUFFICIENT_DATA': 'Insufficient data for analysis',
    'EXPORT_FAILED': 'Data export failed',
    'POWERBI_CONNECTION_FAILED': 'Power BI connection failed'
}

# Success messages
SUCCESS_MESSAGES = {
    'DATA_EXPORTED': 'Data exported successfully',
    'FORMATION_SAVED': 'Formation saved successfully',
    'PLAYER_UPDATED': 'Player information updated',
    'MATCH_SAVED': 'Match information saved',
    'ANALYTICS_GENERATED': 'Analytics generated successfully'
}