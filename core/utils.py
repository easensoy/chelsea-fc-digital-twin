from django.utils import timezone
from django.db.models import Avg, Sum, Count, Q
from datetime import timedelta, datetime
from decimal import Decimal, ROUND_HALF_UP
import re
import logging

logger = logging.getLogger('core.performance')

def calculate_age(birth_date):
    today = timezone.now().date()
    return (today - birth_date).days // 365

def calculate_pass_accuracy(passes_completed, passes_attempted):
    if passes_attempted == 0:
        return 0
    return round((passes_completed / passes_attempted) * 100, 2)

def calculate_shot_accuracy(shots_on_target, shots_off_target):
    total_shots = shots_on_target + shots_off_target
    if total_shots == 0:
        return 0
    return round((shots_on_target / total_shots) * 100, 2)

def calculate_conversion_rate(goals, shots_total):
    if shots_total == 0:
        return 0
    return round((goals / shots_total) * 100, 2)

def calculate_win_rate(wins, total_matches):
    if total_matches == 0:
        return 0
    return round((wins / total_matches) * 100, 2)

def calculate_points_per_match(wins, draws, total_matches):
    if total_matches == 0:
        return 0
    points = (wins * 3) + draws
    return round(points / total_matches, 2)

def calculate_variance(values):
    if len(values) <= 1:
        return 0
    
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return variance ** 0.5

def calculate_z_score(value, mean, std_dev):
    if std_dev == 0:
        return 0
    return (value - mean) / std_dev

def normalize_rating(rating, min_rating=1, max_rating=10):
    return max(min_rating, min(max_rating, rating))

def calculate_fitness_category(fitness_level):
    if fitness_level >= 95:
        return 'Excellent'
    elif fitness_level >= 85:
        return 'Good'
    elif fitness_level >= 75:
        return 'Average'
    elif fitness_level >= 65:
        return 'Poor'
    else:
        return 'Critical'

def calculate_performance_grade(rating):
    if rating >= 9.0:
        return 'A+'
    elif rating >= 8.5:
        return 'A'
    elif rating >= 8.0:
        return 'A-'
    elif rating >= 7.5:
        return 'B+'
    elif rating >= 7.0:
        return 'B'
    elif rating >= 6.5:
        return 'B-'
    elif rating >= 6.0:
        return 'C+'
    elif rating >= 5.5:
        return 'C'
    elif rating >= 5.0:
        return 'C-'
    else:
        return 'D'

def format_duration(minutes):
    if minutes < 60:
        return f"{minutes}m"
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        return f"{hours}h {remaining_minutes}m"

def format_distance(meters):
    if meters >= 1000:
        kilometers = meters / 1000
        return f"{kilometers:.1f}km"
    else:
        return f"{meters}m"

def format_percentage(value, decimal_places=1):
    return f"{value:.{decimal_places}f}%"

def format_currency(amount, currency='£'):
    if amount >= 1000000:
        return f"{currency}{amount/1000000:.1f}M"
    elif amount >= 1000:
        return f"{currency}{amount/1000:.0f}K"
    else:
        return f"{currency}{amount:.0f}"

def validate_squad_number(squad_number):
    return 1 <= squad_number <= 99

def validate_formation_name(formation_name):
    pattern = r'^\d{1}-\d{1}-\d{1}$|^\d{1}-\d{1}-\d{1}-\d{1}$'
    return bool(re.match(pattern, formation_name))

def validate_rating(rating):
    return 1.0 <= rating <= 10.0

def validate_fitness_level(fitness_level):
    return 0 <= fitness_level <= 100

def validate_percentage(percentage):
    return 0 <= percentage <= 100

def get_season_start_date(date=None):
    if not date:
        date = timezone.now().date()
    
    if date.month >= 8:
        return datetime(date.year, 8, 1).date()
    else:
        return datetime(date.year - 1, 8, 1).date()

def get_season_end_date(date=None):
    if not date:
        date = timezone.now().date()
    
    if date.month >= 8:
        return datetime(date.year + 1, 7, 31).date()
    else:
        return datetime(date.year, 7, 31).date()

def get_season_label(date=None):
    start_date = get_season_start_date(date)
    end_date = get_season_end_date(date)
    return f"{start_date.year}/{end_date.year}"

def determine_position_category(position):
    position_categories = {
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
    }
    return position_categories.get(position, 'Unknown')

def get_position_priorities():
    return {
        'GK': ['Reflexes', 'Distribution', 'Positioning'],
        'CB': ['Defending', 'Heading', 'Passing'],
        'LB': ['Defending', 'Pace', 'Crossing'],
        'RB': ['Defending', 'Pace', 'Crossing'],
        'CDM': ['Tackling', 'Passing', 'Positioning'],
        'CM': ['Passing', 'Vision', 'Work Rate'],
        'CAM': ['Creativity', 'Shooting', 'Passing'],
        'LM': ['Pace', 'Crossing', 'Dribbling'],
        'RM': ['Pace', 'Crossing', 'Dribbling'],
        'LW': ['Pace', 'Dribbling', 'Shooting'],
        'RW': ['Pace', 'Dribbling', 'Shooting'],
        'ST': ['Shooting', 'Movement', 'Finishing']
    }

def calculate_formation_balance(formation_name):
    if not validate_formation_name(formation_name):
        return None
    
    parts = formation_name.split('-')
    
    if len(parts) == 3:
        defenders, midfielders, forwards = map(int, parts)
        balance_score = abs(defenders - midfielders) + abs(midfielders - forwards)
        
        if balance_score <= 2:
            return 'Balanced'
        elif balance_score <= 4:
            return 'Moderate'
        else:
            return 'Unbalanced'
    
    return 'Unknown'

def determine_formation_style(formation_name):
    if not validate_formation_name(formation_name):
        return 'Unknown'
    
    parts = formation_name.split('-')
    
    if len(parts) >= 3:
        defenders = int(parts[0])
        forwards = int(parts[-1])
        
        if defenders >= 5:
            return 'Defensive'
        elif forwards >= 3:
            return 'Attacking'
        else:
            return 'Balanced'
    
    return 'Unknown'

def calculate_player_impact_score(goals, assists, rating, minutes_played):
    if minutes_played == 0:
        return 0
    
    goal_impact = goals * 3
    assist_impact = assists * 2
    rating_impact = (rating - 5) * 0.5
    time_factor = min(1.0, minutes_played / 90)
    
    impact_score = (goal_impact + assist_impact + rating_impact) * time_factor
    return round(max(0, impact_score), 2)

def calculate_defensive_contribution(tackles, interceptions, clearances, blocks):
    return tackles + interceptions + (clearances * 0.5) + (blocks * 0.7)

def calculate_attacking_contribution(goals, assists, shots_on_target, key_passes=0):
    return (goals * 3) + (assists * 2) + (shots_on_target * 0.5) + (key_passes * 0.3)

def calculate_consistency_score(ratings):
    if len(ratings) < 3:
        return 0
    
    variance = calculate_variance(ratings)
    consistency_score = max(0, 100 - (variance * 20))
    return round(consistency_score, 2)

def calculate_form_indicator(recent_results, weight_recent=True):
    if not recent_results:
        return 0
    
    points_mapping = {'WIN': 3, 'DRAW': 1, 'LOSS': 0}
    
    if weight_recent:
        weights = [i + 1 for i in range(len(recent_results))]
        weighted_points = sum(points_mapping.get(result, 0) * weight 
                            for result, weight in zip(recent_results, weights))
        total_weight = sum(weights)
        form_score = (weighted_points / (total_weight * 3)) * 100
    else:
        total_points = sum(points_mapping.get(result, 0) for result in recent_results)
        max_points = len(recent_results) * 3
        form_score = (total_points / max_points) * 100
    
    return round(form_score, 2)

def calculate_match_importance(match_type, league_position=None, cup_stage=None):
    importance_scores = {
        'LEAGUE': 70,
        'UCL': 95,
        'UEL': 85,
        'FA': 75,
        'CARABAO': 65,
        'FRIENDLY': 30,
        'TRAINING': 10
    }
    
    base_score = importance_scores.get(match_type, 50)
    
    if match_type == 'LEAGUE' and league_position:
        if league_position <= 4:
            base_score += 10
        elif league_position >= 17:
            base_score += 15
    
    if match_type in ['UCL', 'UEL', 'FA', 'CARABAO'] and cup_stage:
        cup_multipliers = {
            'final': 1.5,
            'semi-final': 1.3,
            'quarter-final': 1.2,
            'round-of-16': 1.1
        }
        multiplier = cup_multipliers.get(cup_stage.lower(), 1.0)
        base_score = int(base_score * multiplier)
    
    return min(100, base_score)

def generate_performance_summary(stats_dict):
    summary = []
    
    rating = stats_dict.get('rating', 0)
    if rating >= 8.0:
        summary.append("Outstanding performance")
    elif rating >= 7.0:
        summary.append("Good performance")
    elif rating < 6.0:
        summary.append("Below par performance")
    
    goals = stats_dict.get('goals', 0)
    assists = stats_dict.get('assists', 0)
    
    if goals > 0:
        summary.append(f"{goals} goal{'s' if goals > 1 else ''}")
    
    if assists > 0:
        summary.append(f"{assists} assist{'s' if assists > 1 else ''}")
    
    pass_accuracy = stats_dict.get('pass_accuracy', 0)
    if pass_accuracy > 90:
        summary.append("Excellent passing")
    elif pass_accuracy < 70:
        summary.append("Poor passing accuracy")
    
    return "; ".join(summary) if summary else "Standard performance"

def calculate_risk_factor(fitness_level, recent_injuries, minutes_played_recent):
    risk_score = 0
    
    if fitness_level < 80:
        risk_score += 30
    elif fitness_level < 90:
        risk_score += 15
    
    if recent_injuries > 0:
        risk_score += recent_injuries * 20
    
    if minutes_played_recent > 270:  # More than 3 full matches
        risk_score += 25
    elif minutes_played_recent > 180:
        risk_score += 10
    
    risk_level = min(100, risk_score)
    
    if risk_level > 70:
        return 'High'
    elif risk_level > 40:
        return 'Medium'
    else:
        return 'Low'

def format_match_result(chelsea_score, opponent_score, opponent_name):
    result = "Win" if chelsea_score > opponent_score else "Loss" if chelsea_score < opponent_score else "Draw"
    return f"Chelsea {chelsea_score}-{opponent_score} {opponent_name} ({result})"

def calculate_goal_involvement(goals, assists, team_goals):
    if team_goals == 0:
        return 0
    involvement = goals + assists
    return round((involvement / team_goals) * 100, 1)

def determine_player_role(position, formation_name):
    role_mappings = {
        '4-4-2': {
            'GK': 'Goalkeeper',
            'CB': 'Centre Back',
            'LB': 'Left Back',
            'RB': 'Right Back',
            'LM': 'Left Midfielder',
            'RM': 'Right Midfielder',
            'CM': 'Central Midfielder',
            'ST': 'Striker'
        },
        '4-3-3': {
            'GK': 'Goalkeeper',
            'CB': 'Centre Back',
            'LB': 'Left Back',
            'RB': 'Right Back',
            'CDM': 'Defensive Midfielder',
            'CM': 'Central Midfielder',
            'LW': 'Left Winger',
            'RW': 'Right Winger',
            'ST': 'Central Forward'
        },
        '3-5-2': {
            'GK': 'Goalkeeper',
            'CB': 'Centre Back',
            'LM': 'Left Wing Back',
            'RM': 'Right Wing Back',
            'CDM': 'Defensive Midfielder',
            'CM': 'Central Midfielder',
            'CAM': 'Attacking Midfielder',
            'ST': 'Striker'
        }
    }
    
    formation_roles = role_mappings.get(formation_name, {})
    return formation_roles.get(position, f"{position} Player")

def calculate_workload_score(minutes_played, distance_covered, sprints):
    if minutes_played == 0:
        return 0
    
    distance_per_minute = distance_covered / minutes_played
    sprint_intensity = sprints / (minutes_played / 10)  # Sprints per 10 minutes
    
    workload_score = (distance_per_minute * 50) + (sprint_intensity * 20)
    return round(min(100, workload_score), 1)

def get_tactical_recommendation(formation_analysis):
    recommendations = []
    
    effectiveness = formation_analysis.get('effectiveness', 0)
    
    if effectiveness > 80:
        recommendations.append("Continue with current tactical approach")
    elif effectiveness > 60:
        recommendations.append("Minor tactical adjustments may improve effectiveness")
    else:
        recommendations.append("Consider significant tactical changes")
    
    attacking_efficiency = formation_analysis.get('attacking_efficiency', 0)
    if attacking_efficiency < 50:
        recommendations.append("Focus on improving attacking patterns")
    
    defensive_solidity = formation_analysis.get('defensive_solidity', 0)
    if defensive_solidity < 60:
        recommendations.append("Strengthen defensive organization")
    
    return recommendations

def calculate_prediction_confidence(data_points, consistency_score, recent_form):
    base_confidence = min(80, data_points * 5)
    
    consistency_bonus = consistency_score * 0.2
    
    form_adjustment = 0
    if recent_form > 80:
        form_adjustment = 10
    elif recent_form < 40:
        form_adjustment = -10
    
    total_confidence = base_confidence + consistency_bonus + form_adjustment
    return round(min(100, max(10, total_confidence)), 1)

def safe_divide(numerator, denominator, default=0):
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default

def safe_percentage(part, total, decimal_places=1):
    if total == 0:
        return 0
    return round((part / total) * 100, decimal_places)

def clamp_value(value, min_value, max_value):
    return max(min_value, min(max_value, value))

def round_to_precision(value, precision=2):
    if isinstance(value, Decimal):
        return value.quantize(Decimal('0.' + '0' * precision), rounding=ROUND_HALF_UP)
    return round(value, precision)

def parse_match_time(minute_string):
    try:
        if '+' in minute_string:
            base_time, added_time = minute_string.split('+')
            return int(base_time) + int(added_time)
        else:
            return int(minute_string)
    except (ValueError, AttributeError):
        return 0

def generate_unique_filename(base_name, extension, timestamp=None):
    if not timestamp:
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    
    return f"{base_name}_{timestamp}.{extension}"

def clean_text_input(text):
    if not text:
        return ""
    
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\-\.]', '', text)
    
    return text

def validate_date_range(start_date, end_date):
    if start_date > end_date:
        return False, "Start date cannot be after end date"
    
    max_range = timedelta(days=730)  # 2 years
    if (end_date - start_date) > max_range:
        return False, "Date range cannot exceed 2 years"
    
    return True, "Valid date range"

def calculate_momentum(recent_results, weight_factor=0.8):
    if not recent_results:
        return 0
    
    points_map = {'WIN': 3, 'DRAW': 1, 'LOSS': 0}
    momentum_score = 0
    
    for i, result in enumerate(recent_results):
        weight = weight_factor ** i
        points = points_map.get(result, 0)
        momentum_score += points * weight
    
    max_possible = sum(3 * (weight_factor ** i) for i in range(len(recent_results)))
    
    if max_possible == 0:
        return 0
    
    return round((momentum_score / max_possible) * 100, 1)