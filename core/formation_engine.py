from django.db.models import Q, Avg, Count
from django.conf import settings
from decimal import Decimal
import logging

from .models import Formation, FormationPosition, Player, Match, PlayerStats, MatchLineup

logger = logging.getLogger('core.performance')

class FormationEngine:
    
    def __init__(self):
        self.valid_formations = settings.FORMATION_CONFIG['VALID_FORMATIONS']
        self.max_players = settings.FORMATION_CONFIG['MAX_PLAYERS']
        self.positions = settings.FORMATION_CONFIG['POSITIONS']
        self.logger = logging.getLogger('core.performance')
    
    def validate_formation(self, formation_name, player_positions):
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        if formation_name not in self.valid_formations:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Formation {formation_name} is not recognised")
        
        if len(player_positions) != self.max_players:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Formation must contain exactly {self.max_players} players")
        
        position_counts = {}
        for position in player_positions:
            if position['position'] not in self.positions:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"Invalid position: {position['position']}")
            
            pos = position['position']
            position_counts[pos] = position_counts.get(pos, 0) + 1
        
        if position_counts.get('GK', 0) != 1:
            validation_result['is_valid'] = False
            validation_result['errors'].append("Formation must contain exactly one goalkeeper")
        
        self._validate_formation_structure(formation_name, position_counts, validation_result)
        self._validate_player_positions(player_positions, validation_result)
        
        return validation_result
    
    def _validate_formation_structure(self, formation_name, position_counts, validation_result):
        formation_structures = {
            '4-4-2': {'defenders': 4, 'midfielders': 4, 'forwards': 2},
            '4-3-3': {'defenders': 4, 'midfielders': 3, 'forwards': 3},
            '3-5-2': {'defenders': 3, 'midfielders': 5, 'forwards': 2},
            '5-3-2': {'defenders': 5, 'midfielders': 3, 'forwards': 2},
            '4-2-3-1': {'defenders': 4, 'midfielders': 5, 'forwards': 1},
            '3-4-3': {'defenders': 3, 'midfielders': 4, 'forwards': 3}
        }
        
        if formation_name in formation_structures:
            expected = formation_structures[formation_name]
            
            defenders = sum(position_counts.get(pos, 0) for pos in ['CB', 'LB', 'RB'])
            midfielders = sum(position_counts.get(pos, 0) for pos in ['CDM', 'CM', 'CAM', 'LM', 'RM'])
            forwards = sum(position_counts.get(pos, 0) for pos in ['LW', 'RW', 'ST'])
            
            if defenders != expected['defenders']:
                validation_result['warnings'].append(
                    f"Expected {expected['defenders']} defenders, found {defenders}"
                )
            
            if midfielders != expected['midfielders']:
                validation_result['warnings'].append(
                    f"Expected {expected['midfielders']} midfielders, found {midfielders}"
                )
            
            if forwards != expected['forwards']:
                validation_result['warnings'].append(
                    f"Expected {expected['forwards']} forwards, found {forwards}"
                )
    
    def _validate_player_positions(self, player_positions, validation_result):
        for position in player_positions:
            x, y = position.get('x_coordinate', 0), position.get('y_coordinate', 0)
            
            if not (0 <= x <= 100) or not (0 <= y <= 100):
                validation_result['warnings'].append(
                    f"Position coordinates for {position['position']} are outside valid range"
                )
    
    def calculate_formation_effectiveness(self, formation, opponent=None, match_type='LEAGUE'):
        recent_matches = self._get_formation_matches(formation, days=90)
        
        if not recent_matches:
            return self._default_effectiveness_score()
        
        effectiveness_data = {
            'formation_name': formation.name,
            'matches_analyzed': len(recent_matches),
            'win_rate': self._calculate_win_rate(recent_matches),
            'average_goals_scored': self._calculate_average_goals_scored(recent_matches),
            'average_goals_conceded': self._calculate_average_goals_conceded(recent_matches),
            'clean_sheet_rate': self._calculate_clean_sheet_rate(recent_matches),
            'possession_average': self._calculate_possession_average(recent_matches),
            'effectiveness_score': 0,
            'strengths': [],
            'weaknesses': [],
            'opponent_specific': None
        }
        
        effectiveness_data['effectiveness_score'] = self._calculate_overall_effectiveness(effectiveness_data)
        effectiveness_data['strengths'], effectiveness_data['weaknesses'] = self._identify_strengths_weaknesses(effectiveness_data)
        
        if opponent:
            effectiveness_data['opponent_specific'] = self._analyze_against_opponent(formation, opponent)
        
        self.logger.info(f"Formation effectiveness calculated for {formation.name}: {effectiveness_data['effectiveness_score']}")
        return effectiveness_data
    
    def _get_formation_matches(self, formation, days=90):
        from datetime import timedelta
        from django.utils import timezone
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        lineups = MatchLineup.objects.filter(
            formation=formation,
            match__status__in=['COMPLETED', 'FULL_TIME'],
            match__scheduled_datetime__gte=cutoff_date
        ).select_related('match')
        
        return [lineup.match for lineup in lineups]
    
    def _calculate_win_rate(self, matches):
        if not matches:
            return 0
        
        wins = sum(1 for match in matches if match.result == 'WIN')
        return round((wins / len(matches)) * 100, 2)
    
    def _calculate_average_goals_scored(self, matches):
        if not matches:
            return 0
        
        total_goals = sum(match.chelsea_score for match in matches)
        return round(total_goals / len(matches), 2)
    
    def _calculate_average_goals_conceded(self, matches):
        if not matches:
            return 0
        
        total_conceded = sum(match.opponent_score for match in matches)
        return round(total_conceded / len(matches), 2)
    
    def _calculate_clean_sheet_rate(self, matches):
        if not matches:
            return 0
        
        clean_sheets = sum(1 for match in matches if match.opponent_score == 0)
        return round((clean_sheets / len(matches)) * 100, 2)
    
    def _calculate_possession_average(self, matches):
        from .models import TeamStats
        
        if not matches:
            return 50
        
        possession_values = []
        for match in matches:
            try:
                team_stats = TeamStats.objects.get(match=match)
                possession_values.append(float(team_stats.possession_percentage))
            except TeamStats.DoesNotExist:
                continue
        
        if not possession_values:
            return 50
        
        return round(sum(possession_values) / len(possession_values), 2)
    
    def _calculate_overall_effectiveness(self, data):
        win_rate_score = data['win_rate']
        goal_difference = data['average_goals_scored'] - data['average_goals_conceded']
        goal_score = max(0, min(100, (goal_difference + 2) * 25))
        clean_sheet_score = data['clean_sheet_rate']
        
        possession_score = min(100, max(0, (data['possession_average'] - 30) * 2.5))
        
        overall_score = (
            win_rate_score * 0.4 +
            goal_score * 0.3 +
            clean_sheet_score * 0.2 +
            possession_score * 0.1
        )
        
        return round(overall_score, 2)
    
    def _identify_strengths_weaknesses(self, data):
        strengths = []
        weaknesses = []
        
        if data['win_rate'] >= 70:
            strengths.append("High win rate")
        elif data['win_rate'] <= 40:
            weaknesses.append("Low win rate")
        
        if data['average_goals_scored'] >= 2.0:
            strengths.append("Strong attacking output")
        elif data['average_goals_scored'] <= 1.0:
            weaknesses.append("Limited goal scoring")
        
        if data['average_goals_conceded'] <= 0.8:
            strengths.append("Solid defensive record")
        elif data['average_goals_conceded'] >= 1.5:
            weaknesses.append("Defensive vulnerabilities")
        
        if data['clean_sheet_rate'] >= 50:
            strengths.append("Excellent clean sheet record")
        elif data['clean_sheet_rate'] <= 20:
            weaknesses.append("Poor clean sheet record")
        
        if data['possession_average'] >= 60:
            strengths.append("Dominant possession")
        elif data['possession_average'] <= 40:
            weaknesses.append("Limited possession control")
        
        return strengths, weaknesses
    
    def _analyze_against_opponent(self, formation, opponent):
        opponent_matches = Match.objects.filter(
            opponent=opponent,
            status__in=['COMPLETED', 'FULL_TIME']
        ).order_by('-scheduled_datetime')[:5]
        
        formation_vs_opponent = []
        for match in opponent_matches:
            try:
                lineup = MatchLineup.objects.get(match=match, formation=formation)
                formation_vs_opponent.append(match)
            except MatchLineup.DoesNotExist:
                continue
        
        if not formation_vs_opponent:
            return {
                'matches_against': 0,
                'effectiveness': 'No historical data',
                'recommendation': 'Insufficient data for analysis'
            }
        
        wins = sum(1 for match in formation_vs_opponent if match.result == 'WIN')
        win_rate = (wins / len(formation_vs_opponent)) * 100
        
        avg_goals_scored = sum(match.chelsea_score for match in formation_vs_opponent) / len(formation_vs_opponent)
        avg_goals_conceded = sum(match.opponent_score for match in formation_vs_opponent) / len(formation_vs_opponent)
        
        effectiveness = 'Highly effective' if win_rate >= 70 else 'Moderately effective' if win_rate >= 50 else 'Less effective'
        
        return {
            'matches_against': len(formation_vs_opponent),
            'win_rate': round(win_rate, 2),
            'average_goals_scored': round(avg_goals_scored, 2),
            'average_goals_conceded': round(avg_goals_conceded, 2),
            'effectiveness': effectiveness,
            'recommendation': self._generate_opponent_recommendation(win_rate, avg_goals_scored, avg_goals_conceded)
        }
    
    def _generate_opponent_recommendation(self, win_rate, goals_scored, goals_conceded):
        if win_rate >= 70:
            return "Highly recommended against this opponent"
        elif win_rate >= 50:
            return "Suitable choice with some modifications"
        elif goals_scored > goals_conceded:
            return "Consider tactical adjustments to improve defensive solidity"
        elif goals_conceded > goals_scored:
            return "Focus on attacking improvements or consider alternative formation"
        else:
            return "Evaluate alternative formations for better results"
    
    def _default_effectiveness_score(self):
        return {
            'formation_name': 'Unknown',
            'matches_analyzed': 0,
            'win_rate': 0,
            'average_goals_scored': 0,
            'average_goals_conceded': 0,
            'clean_sheet_rate': 0,
            'possession_average': 50,
            'effectiveness_score': 50,
            'strengths': [],
            'weaknesses': ['Insufficient match data'],
            'opponent_specific': None
        }
    
    def get_optimal_formation_for_players(self, available_players):
        if len(available_players) < self.max_players:
            return None
        
        position_counts = {}
        for player in available_players:
            pos = player.position
            position_counts[pos] = position_counts.get(pos, 0) + 1
        
        formation_scores = {}
        for formation_name in self.valid_formations:
            score = self._score_formation_for_players(formation_name, position_counts)
            formation_scores[formation_name] = score
        
        optimal_formation = max(formation_scores, key=formation_scores.get)
        
        return {
            'recommended_formation': optimal_formation,
            'formation_score': formation_scores[optimal_formation],
            'all_scores': formation_scores,
            'player_fitness': self._calculate_squad_fitness(available_players)
        }
    
    def _score_formation_for_players(self, formation_name, position_counts):
        formation_requirements = {
            '4-4-2': {'CB': 2, 'LB': 1, 'RB': 1, 'CM': 2, 'LM': 1, 'RM': 1, 'ST': 2},
            '4-3-3': {'CB': 2, 'LB': 1, 'RB': 1, 'CDM': 1, 'CM': 2, 'LW': 1, 'RW': 1, 'ST': 1},
            '3-5-2': {'CB': 3, 'CDM': 1, 'CM': 2, 'LM': 1, 'RM': 1, 'ST': 2},
            '5-3-2': {'CB': 3, 'LB': 1, 'RB': 1, 'CDM': 1, 'CM': 2, 'ST': 2},
            '4-2-3-1': {'CB': 2, 'LB': 1, 'RB': 1, 'CDM': 2, 'CAM': 1, 'LM': 1, 'RM': 1, 'ST': 1},
            '3-4-3': {'CB': 3, 'CDM': 1, 'CM': 2, 'CAM': 1, 'LW': 1, 'RW': 1, 'ST': 1}
        }
        
        if formation_name not in formation_requirements:
            return 0
        
        required = formation_requirements[formation_name]
        score = 0
        
        for position, needed in required.items():
            available = position_counts.get(position, 0)
            if available >= needed:
                score += needed * 10
            else:
                score += available * 5
        
        return score
    
    def _calculate_squad_fitness(self, players):
        if not players:
            return 0
        
        total_fitness = sum(player.fitness_level for player in players)
        return round(total_fitness / len(players), 2)