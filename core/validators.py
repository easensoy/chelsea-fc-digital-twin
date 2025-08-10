from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
import re

def validate_squad_number(value):
    if not isinstance(value, int) or value < 1 or value > 99:
        raise ValidationError('Squad number must be between 1 and 99.')

def validate_player_rating(value):
    if not isinstance(value, (int, float)) or value < 1.0 or value > 10.0:
        raise ValidationError('Player rating must be between 1.0 and 10.0.')

def validate_fitness_level(value):
    if not isinstance(value, int) or value < 0 or value > 100:
        raise ValidationError('Fitness level must be between 0 and 100.')

def validate_percentage(value):
    if not isinstance(value, (int, float)) or value < 0 or value > 100:
        raise ValidationError('Percentage must be between 0 and 100.')

def validate_formation_name(value):
    pattern = r'^\d{1}-\d{1}-\d{1}$|^\d{1}-\d{1}-\d{1}-\d{1}$'
    if not re.match(pattern, value):
        raise ValidationError('Formation name must be in format like "4-4-2" or "4-2-3-1".')

def validate_formation_positions(value):
    if not value:
        raise ValidationError('Formation must have at least one position defined.')
    
    if not isinstance(value, list):
        raise ValidationError('Formation positions must be a list.')
    
    required_positions = ['GK']
    goalkeeper_count = sum(1 for pos in value if pos.get('position') == 'GK')
    
    if goalkeeper_count != 1:
        raise ValidationError('Formation must have exactly one goalkeeper.')
    
    total_outfield = len(value) - 1
    if total_outfield != 10:
        raise ValidationError('Formation must have exactly 10 outfield players.')

def validate_match_score(value):
    if not isinstance(value, int) or value < 0 or value > 20:
        raise ValidationError('Match score must be between 0 and 20.')

def validate_match_minute(value):
    if not isinstance(value, int) or value < 0 or value > 120:
        raise ValidationError('Match minute must be between 0 and 120.')

def validate_future_date(value):
    if value <= timezone.now().date():
        raise ValidationError('Date must be in the future.')

def validate_past_or_present_date(value):
    if value > timezone.now().date():
        raise ValidationError('Date cannot be in the future.')

def validate_birth_date(value):
    if value > timezone.now().date():
        raise ValidationError('Birth date cannot be in the future.')
    
    min_birth_date = timezone.now().date() - timedelta(days=50 * 365)
    if value < min_birth_date:
        raise ValidationError('Birth date cannot be more than 50 years ago.')
    
    min_age_date = timezone.now().date() - timedelta(days=16 * 365)
    if value > min_age_date:
        raise ValidationError('Player must be at least 16 years old.')

def validate_contract_expiry(value):
    if value < timezone.now().date():
        raise ValidationError('Contract expiry date cannot be in the past.')
    
    max_contract_date = timezone.now().date() + timedelta(days=10 * 365)
    if value > max_contract_date:
        raise ValidationError('Contract cannot be longer than 10 years.')

def validate_player_height(value):
    if not isinstance(value, int) or value < 150 or value > 220:
        raise ValidationError('Player height must be between 150cm and 220cm.')

def validate_player_weight(value):
    if not isinstance(value, int) or value < 50 or value > 120:
        raise ValidationError('Player weight must be between 50kg and 120kg.')

def validate_market_value(value):
    if not isinstance(value, (int, float)) or value < 0 or value > 500:
        raise ValidationError('Market value must be between £0M and £500M.')

def validate_distance_covered(value):
    if not isinstance(value, (int, float)) or value < 0 or value > 20000:
        raise ValidationError('Distance covered must be between 0m and 20,000m.')

def validate_sprint_count(value):
    if not isinstance(value, int) or value < 0 or value > 100:
        raise ValidationError('Sprint count must be between 0 and 100.')

def validate_minutes_played(value):
    if not isinstance(value, int) or value < 0 or value > 120:
        raise ValidationError('Minutes played must be between 0 and 120.')

def validate_passes_completed(value):
    if not isinstance(value, int) or value < 0 or value > 200:
        raise ValidationError('Passes completed must be between 0 and 200.')

def validate_passes_attempted(value):
    if not isinstance(value, int) or value < 0 or value > 200:
        raise ValidationError('Passes attempted must be between 0 and 200.')

def validate_passes_consistency(passes_completed, passes_attempted):
    if passes_completed > passes_attempted:
        raise ValidationError('Passes completed cannot exceed passes attempted.')

def validate_shots_count(value):
    if not isinstance(value, int) or value < 0 or value > 30:
        raise ValidationError('Shots count must be between 0 and 30.')

def validate_goals_count(value):
    if not isinstance(value, int) or value < 0 or value > 10:
        raise ValidationError('Goals count must be between 0 and 10.')

def validate_assists_count(value):
    if not isinstance(value, int) or value < 0 or value > 10:
        raise ValidationError('Assists count must be between 0 and 10.')

def validate_tackles_count(value):
    if not isinstance(value, int) or value < 0 or value > 20:
        raise ValidationError('Tackles count must be between 0 and 20.')

def validate_interceptions_count(value):
    if not isinstance(value, int) or value < 0 or value > 20:
        raise ValidationError('Interceptions count must be between 0 and 20.')

def validate_clearances_count(value):
    if not isinstance(value, int) or value < 0 or value > 30:
        raise ValidationError('Clearances count must be between 0 and 30.')

def validate_blocks_count(value):
    if not isinstance(value, int) or value < 0 or value > 15:
        raise ValidationError('Blocks count must be between 0 and 15.')

def validate_fouls_count(value):
    if not isinstance(value, int) or value < 0 or value > 10:
        raise ValidationError('Fouls count must be between 0 and 10.')

def validate_cards_count(value):
    if not isinstance(value, int) or value < 0 or value > 5:
        raise ValidationError('Cards count must be between 0 and 5.')

def validate_offsides_count(value):
    if not isinstance(value, int) or value < 0 or value > 10:
        raise ValidationError('Offsides count must be between 0 and 10.')

def validate_corners_count(value):
    if not isinstance(value, int) or value < 0 or value > 20:
        raise ValidationError('Corners count must be between 0 and 20.')

def validate_coordinate(value):
    if not isinstance(value, (int, float)) or value < 0 or value > 100:
        raise ValidationError('Coordinate must be between 0 and 100.')

def validate_possession_percentage(value):
    if not isinstance(value, (int, float)) or value < 0 or value > 100:
        raise ValidationError('Possession percentage must be between 0 and 100.')

def validate_confidence_score(value):
    if not isinstance(value, (int, float)) or value < 0 or value > 100:
        raise ValidationError('Confidence score must be between 0 and 100.')

def validate_json_field(value):
    if value is None:
        return
    
    if not isinstance(value, (dict, list)):
        raise ValidationError('JSON field must be a valid dictionary or list.')

def validate_analytics_insights(value):
    if not isinstance(value, list):
        raise ValidationError('Insights must be a list.')
    
    if len(value) > 50:
        raise ValidationError('Maximum 50 insights allowed.')
    
    for insight in value:
        if not isinstance(insight, str) or len(insight) > 500:
            raise ValidationError('Each insight must be a string with maximum 500 characters.')

def validate_analytics_recommendations(value):
    if not isinstance(value, list):
        raise ValidationError('Recommendations must be a list.')
    
    if len(value) > 20:
        raise ValidationError('Maximum 20 recommendations allowed.')
    
    for recommendation in value:
        if not isinstance(recommendation, str) or len(recommendation) > 300:
            raise ValidationError('Each recommendation must be a string with maximum 300 characters.')

def validate_analytics_data_points(value):
    if not isinstance(value, dict):
        raise ValidationError('Data points must be a dictionary.')
    
    if len(value) > 100:
        raise ValidationError('Maximum 100 data points allowed.')

def validate_venue_name(value):
    if not value or len(value.strip()) < 3:
        raise ValidationError('Venue name must be at least 3 characters long.')
    
    if len(value) > 100:
        raise ValidationError('Venue name cannot exceed 100 characters.')

def validate_attendance(value):
    if not isinstance(value, int) or value < 0 or value > 100000:
        raise ValidationError('Attendance must be between 0 and 100,000.')

def validate_weather_conditions(value):
    if value and len(value) > 100:
        raise ValidationError('Weather conditions cannot exceed 100 characters.')

def validate_referee_name(value):
    if value and len(value) > 100:
        raise ValidationError('Referee name cannot exceed 100 characters.')

def validate_opponent_name(value):
    if not value or len(value.strip()) < 2:
        raise ValidationError('Opponent name must be at least 2 characters long.')
    
    if len(value) > 100:
        raise ValidationError('Opponent name cannot exceed 100 characters.')

def validate_league_name(value):
    if not value or len(value.strip()) < 2:
        raise ValidationError('League name must be at least 2 characters long.')
    
    if len(value) > 50:
        raise ValidationError('League name cannot exceed 50 characters.')

def validate_country_name(value):
    if not value or len(value.strip()) < 2:
        raise ValidationError('Country name must be at least 2 characters long.')
    
    if len(value) > 50:
        raise ValidationError('Country name cannot exceed 50 characters.')

def validate_playing_style(value):
    if value and len(value) > 500:
        raise ValidationError('Playing style description cannot exceed 500 characters.')

def validate_event_description(value):
    if value and len(value) > 500:
        raise ValidationError('Event description cannot exceed 500 characters.')

def validate_analytics_title(value):
    if not value or len(value.strip()) < 3:
        raise ValidationError('Analytics title must be at least 3 characters long.')
    
    if len(value) > 200:
        raise ValidationError('Analytics title cannot exceed 200 characters.')

def validate_analytics_description(value):
    if not value or len(value.strip()) < 10:
        raise ValidationError('Analytics description must be at least 10 characters long.')
    
    if len(value) > 1000:
        raise ValidationError('Analytics description cannot exceed 1000 characters.')

def validate_formation_description(value):
    if value and len(value) > 500:
        raise ValidationError('Formation description cannot exceed 500 characters.')

def validate_player_name(value):
    if not value or len(value.strip()) < 2:
        raise ValidationError('Player name must be at least 2 characters long.')
    
    if len(value) > 50:
        raise ValidationError('Player name cannot exceed 50 characters.')
    
    if not re.match(r'^[a-zA-Z\s\-\'\.]+$', value):
        raise ValidationError('Player name can only contain letters, spaces, hyphens, apostrophes, and periods.')

def validate_unique_squad_number(squad_number, player_id=None):
    from .models import Player
    
    players_with_number = Player.objects.filter(squad_number=squad_number, is_active=True)
    
    if player_id:
        players_with_number = players_with_number.exclude(id=player_id)
    
    if players_with_number.exists():
        raise ValidationError(f'Squad number {squad_number} is already taken by another active player.')

def validate_match_datetime(value):
    if not value:
        raise ValidationError('Match datetime is required.')
    
    min_date = timezone.now() - timedelta(days=365 * 2)
    max_date = timezone.now() + timedelta(days=365)
    
    if value < min_date:
        raise ValidationError('Match date cannot be more than 2 years in the past.')
    
    if value > max_date:
        raise ValidationError('Match date cannot be more than 1 year in the future.')

def validate_formation_total_players(defensive_line, midfield_line, attacking_line):
    total = defensive_line + midfield_line + attacking_line
    if total != 10:
        raise ValidationError(f'Formation must have exactly 10 outfield players. Current total: {total}')

def validate_formation_line_count(value, line_type):
    min_players = 1
    max_players = 7
    
    if line_type == 'defensive':
        max_players = 6
    elif line_type == 'midfield':
        max_players = 6
    elif line_type == 'attacking':
        max_players = 4
    
    if not isinstance(value, int) or value < min_players or value > max_players:
        raise ValidationError(f'{line_type.title()} line must have between {min_players} and {max_players} players.')

def validate_position_coordinates(x_coordinate, y_coordinate):
    if x_coordinate is not None and y_coordinate is not None:
        if not (0 <= x_coordinate <= 100) or not (0 <= y_coordinate <= 100):
            raise ValidationError('Position coordinates must be between 0 and 100.')

def validate_player_stats_consistency(stats_data):
    passes_completed = stats_data.get('passes_completed', 0)
    passes_attempted = stats_data.get('passes_attempted', 0)
    
    if passes_completed > passes_attempted:
        raise ValidationError('Passes completed cannot exceed passes attempted.')
    
    goals = stats_data.get('goals', 0)
    shots_on_target = stats_data.get('shots_on_target', 0)
    
    if goals > shots_on_target:
        raise ValidationError('Goals cannot exceed shots on target.')
    
    minutes_played = stats_data.get('minutes_played', 0)
    if minutes_played == 0 and any(stats_data.get(key, 0) > 0 for key in ['goals', 'assists', 'passes_completed']):
        raise ValidationError('Player cannot have statistics without playing any minutes.')

def validate_team_stats_consistency(team_stats_data):
    possession = team_stats_data.get('possession_percentage')
    if possession is not None and not (0 <= possession <= 100):
        raise ValidationError('Possession percentage must be between 0 and 100.')
    
    shots_on_target = team_stats_data.get('shots_on_target', 0)
    shots_off_target = team_stats_data.get('shots_off_target', 0)
    shots_blocked = team_stats_data.get('shots_blocked', 0)
    
    total_shots = shots_on_target + shots_off_target + shots_blocked
    if total_shots > 50:
        raise ValidationError('Total shots (on target + off target + blocked) cannot exceed 50.')

def validate_match_result_consistency(chelsea_score, opponent_score, result):
    calculated_result = 'WIN' if chelsea_score > opponent_score else 'LOSS' if chelsea_score < opponent_score else 'DRAW'
    
    if result != calculated_result:
        raise ValidationError(f'Result "{result}" does not match the score {chelsea_score}-{opponent_score}.')

def validate_lineup_player_uniqueness(lineup_players):
    player_ids = [player.get('player_id') for player in lineup_players if player.get('player_id')]
    
    if len(player_ids) != len(set(player_ids)):
        raise ValidationError('Each player can only appear once in a lineup.')

def validate_starting_eleven_count(lineup_players, is_starting_eleven):
    if is_starting_eleven and len(lineup_players) != 11:
        raise ValidationError('Starting eleven must have exactly 11 players.')
    
    if not is_starting_eleven and len(lineup_players) > 7:
        raise ValidationError('Substitute lineup cannot have more than 7 players.')

def validate_event_timing_consistency(minute, event_type, match_status):
    if minute < 0:
        raise ValidationError('Event minute cannot be negative.')
    
    if match_status in ['SCHEDULED', 'CANCELLED'] and minute > 0:
        raise ValidationError('Events cannot have occurred in scheduled or cancelled matches.')
    
    if event_type in ['HALF_TIME'] and minute != 45:
        raise ValidationError('Half time event must occur at minute 45.')

def validate_analytics_relationship_consistency(related_match, related_player, related_formation, analysis_type):
    if analysis_type == 'PLAYER_PERFORMANCE' and not related_player:
        raise ValidationError('Player performance analytics must have a related player.')
    
    if analysis_type == 'FORMATION_EFFECTIVENESS' and not related_formation:
        raise ValidationError('Formation effectiveness analytics must have a related formation.')
    
    if analysis_type == 'TACTICAL_ANALYSIS' and not related_match:
        raise ValidationError('Tactical analysis must have a related match.')

def validate_bulk_data_size(data_list, max_size=1000):
    if not isinstance(data_list, list):
        raise ValidationError('Bulk data must be a list.')
    
    if len(data_list) > max_size:
        raise ValidationError(f'Bulk operation cannot exceed {max_size} items.')
    
    if len(data_list) == 0:
        raise ValidationError('Bulk operation must contain at least one item.')

def validate_export_date_range(start_date, end_date):
    if start_date > end_date:
        raise ValidationError('Start date cannot be after end date.')
    
    max_range = timedelta(days=730)  # 2 years
    if (end_date - start_date) > max_range:
        raise ValidationError('Export date range cannot exceed 2 years.')
    
    min_date = timezone.now().date() - timedelta(days=365 * 5)  # 5 years back
    if start_date < min_date:
        raise ValidationError('Export start date cannot be more than 5 years in the past.')

def validate_prediction_parameters(days_analysis, confidence_threshold):
    if not isinstance(days_analysis, int) or days_analysis < 7 or days_analysis > 730:
        raise ValidationError('Analysis period must be between 7 and 730 days.')
    
    if not isinstance(confidence_threshold, (int, float)) or confidence_threshold < 0.1 or confidence_threshold > 1.0:
        raise ValidationError('Confidence threshold must be between 0.1 and 1.0.')

def validate_report_parameters(report_type, date_range, player_count):
    valid_report_types = ['season', 'match', 'player', 'tactical', 'monthly']
    if report_type not in valid_report_types:
        raise ValidationError(f'Report type must be one of: {", ".join(valid_report_types)}')
    
    if date_range and len(date_range) != 2:
        raise ValidationError('Date range must contain exactly two dates (start and end).')
    
    if player_count is not None and (not isinstance(player_count, int) or player_count < 1 or player_count > 50):
        raise ValidationError('Player count must be between 1 and 50.')