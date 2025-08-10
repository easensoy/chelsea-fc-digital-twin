from django.db.models import Avg, Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging

from .models import Player, PlayerStats, Match, Formation, MatchLineup, TeamStats
from .exceptions import ValidationError, InsufficientDataError

logger = logging.getLogger('core.performance')

class ComparisonEngine:
    
    def __init__(self):
        self.logger = logging.getLogger('core.performance')
        self.comparison_periods = {
            'recent': 30,
            'season': 180,
            'extended': 365
        }
    
    def compare_players(self, player1, player2, period='recent'):
        if not all(isinstance(p, Player) for p in [player1, player2]):
            raise ValidationError("Invalid player objects provided for comparison")
        
        days = self.comparison_periods.get(period, 30)
        cutoff_date = timezone.now() - timedelta(days=days)
        
        player1_stats = PlayerStats.objects.filter(
            player=player1,
            match__scheduled_datetime__gte=cutoff_date,
            match__status__in=['COMPLETED', 'FULL_TIME']
        )
        
        player2_stats = PlayerStats.objects.filter(
            player=player2,
            match__scheduled_datetime__gte=cutoff_date,
            match__status__in=['COMPLETED', 'FULL_TIME']
        )
        
        if not player1_stats.exists() or not player2_stats.exists():
            raise InsufficientDataError("Insufficient data for player comparison")
        
        comparison = {
            'comparison_period': period,
            'days_analyzed': days,
            'player1': self._extract_player_comparison_data(player1, player1_stats),
            'player2': self._extract_player_comparison_data(player2, player2_stats),
            'head_to_head_metrics': self._calculate_head_to_head_metrics(player1_stats, player2_stats),
            'position_context': self._analyze_position_context(player1, player2),
            'performance_categories': self._categorize_performance_comparison(player1_stats, player2_stats),
            'recommendations': self._generate_comparison_recommendations(player1, player2, player1_stats, player2_stats)
        }
        
        self.logger.info(f"Player comparison completed: {player1.full_name} vs {player2.full_name}")
        return comparison
    
    def compare_formations(self, formation1, formation2, days=90):
        if not all(isinstance(f, Formation) for f in [formation1, formation2]):
            raise ValidationError("Invalid formation objects provided for comparison")
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        formation1_matches = self._get_formation_matches(formation1, cutoff_date)
        formation2_matches = self._get_formation_matches(formation2, cutoff_date)
        
        if formation1_matches.count() < 2 or formation2_matches.count() < 2:
            raise InsufficientDataError("Insufficient matches for formation comparison")
        
        comparison = {
            'analysis_period': days,
            'formation1': self._extract_formation_comparison_data(formation1, formation1_matches),
            'formation2': self._extract_formation_comparison_data(formation2, formation2_matches),
            'effectiveness_comparison': self._compare_formation_effectiveness(formation1_matches, formation2_matches),
            'tactical_analysis': self._analyze_tactical_differences(formation1, formation2, formation1_matches, formation2_matches),
            'situational_recommendations': self._generate_formation_recommendations(formation1, formation2, formation1_matches, formation2_matches)
        }
        
        return comparison
    
    def compare_match_performances(self, match1, match2):
        if not all(isinstance(m, Match) for m in [match1, match2]):
            raise ValidationError("Invalid match objects provided for comparison")
        
        match1_data = self._extract_match_comparison_data(match1)
        match2_data = self._extract_match_comparison_data(match2)
        
        comparison = {
            'match1': match1_data,
            'match2': match2_data,
            'performance_differential': self._calculate_performance_differential(match1_data, match2_data),
            'tactical_comparison': self._compare_match_tactics(match1, match2),
            'lessons_learned': self._extract_comparative_lessons(match1_data, match2_data)
        }
        
        return comparison
    
    def compare_opponent_records(self, opponent1, opponent2, days=365):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        opponent1_matches = Match.objects.filter(
            opponent=opponent1,
            scheduled_datetime__gte=cutoff_date,
            status__in=['COMPLETED', 'FULL_TIME']
        )
        
        opponent2_matches = Match.objects.filter(
            opponent=opponent2,
            scheduled_datetime__gte=cutoff_date,
            status__in=['COMPLETED', 'FULL_TIME']
        )
        
        comparison = {
            'analysis_period': days,
            'opponent1': self._extract_opponent_comparison_data(opponent1, opponent1_matches),
            'opponent2': self._extract_opponent_comparison_data(opponent2, opponent2_matches),
            'difficulty_assessment': self._assess_opponent_difficulty(opponent1_matches, opponent2_matches),
            'preparation_insights': self._generate_opponent_preparation_insights(opponent1, opponent2, opponent1_matches, opponent2_matches)
        }
        
        return comparison
    
    def _extract_player_comparison_data(self, player, stats):
        matches_played = stats.count()
        
        aggregated_stats = stats.aggregate(
            total_goals=Sum('goals'),
            total_assists=Sum('assists'),
            total_minutes=Sum('minutes_played'),
            avg_rating=Avg('rating'),
            total_passes_completed=Sum('passes_completed'),
            total_passes_attempted=Sum('passes_attempted'),
            total_tackles=Sum('tackles'),
            total_interceptions=Sum('interceptions'),
            total_distance=Sum('distance_covered')
        )
        
        return {
            'player_id': str(player.id),
            'player_name': player.full_name,
            'position': player.position,
            'matches_played': matches_played,
            'total_minutes': aggregated_stats['total_minutes'] or 0,
            'goals': aggregated_stats['total_goals'] or 0,
            'assists': aggregated_stats['total_assists'] or 0,
            'goals_per_match': round((aggregated_stats['total_goals'] or 0) / max(matches_played, 1), 2),
            'assists_per_match': round((aggregated_stats['total_assists'] or 0) / max(matches_played, 1), 2),
            'average_rating': round(aggregated_stats['avg_rating'] or 0, 2),
            'pass_accuracy': self._calculate_pass_accuracy(aggregated_stats),
            'defensive_actions_per_match': round(((aggregated_stats['total_tackles'] or 0) + (aggregated_stats['total_interceptions'] or 0)) / max(matches_played, 1), 2),
            'distance_per_match': round((aggregated_stats['total_distance'] or 0) / max(matches_played, 1), 0)
        }
    
    def _calculate_head_to_head_metrics(self, player1_stats, player2_stats):
        p1_data = self._extract_comparative_metrics(player1_stats)
        p2_data = self._extract_comparative_metrics(player2_stats)
        
        metrics = {}
        
        for metric in ['goals_per_match', 'assists_per_match', 'average_rating', 'pass_accuracy']:
            p1_value = p1_data.get(metric, 0)
            p2_value = p2_data.get(metric, 0)
            
            if p1_value > p2_value:
                advantage = 'player1'
                margin = round(((p1_value - p2_value) / max(p2_value, 0.1)) * 100, 1)
            elif p2_value > p1_value:
                advantage = 'player2'
                margin = round(((p2_value - p1_value) / max(p1_value, 0.1)) * 100, 1)
            else:
                advantage = 'equal'
                margin = 0
            
            metrics[metric] = {
                'player1_value': p1_value,
                'player2_value': p2_value,
                'advantage': advantage,
                'margin_percentage': margin
            }
        
        return metrics
    
    def _analyze_position_context(self, player1, player2):
        position_compatibility = {
            'same_position': player1.position == player2.position,
            'position_category_match': self._get_position_category(player1.position) == self._get_position_category(player2.position),
            'comparison_validity': self._assess_comparison_validity(player1.position, player2.position)
        }
        
        if not position_compatibility['same_position']:
            position_compatibility['context_note'] = f"Comparing {player1.position} vs {player2.position} - different role expectations"
        
        return position_compatibility
    
    def _categorize_performance_comparison(self, player1_stats, player2_stats):
        p1_metrics = self._extract_comparative_metrics(player1_stats)
        p2_metrics = self._extract_comparative_metrics(player2_stats)
        
        categories = {
            'attacking': self._compare_attacking_performance(p1_metrics, p2_metrics),
            'creativity': self._compare_creative_performance(p1_metrics, p2_metrics),
            'defensive': self._compare_defensive_performance(p1_metrics, p2_metrics),
            'consistency': self._compare_consistency(player1_stats, player2_stats),
            'physical': self._compare_physical_performance(p1_metrics, p2_metrics)
        }
        
        return categories
    
    def _generate_comparison_recommendations(self, player1, player2, player1_stats, player2_stats):
        recommendations = []
        
        p1_metrics = self._extract_comparative_metrics(player1_stats)
        p2_metrics = self._extract_comparative_metrics(player2_stats)
        
        if p1_metrics['goals_per_match'] > p2_metrics['goals_per_match'] * 1.5:
            recommendations.append({
                'area': 'Goal Scoring',
                'recommendation': f"{player1.full_name} offers significantly better goal threat",
                'priority': 'High'
            })
        
        if p2_metrics['pass_accuracy'] > p1_metrics['pass_accuracy'] + 10:
            recommendations.append({
                'area': 'Ball Retention',
                'recommendation': f"{player2.full_name} provides superior passing reliability",
                'priority': 'Medium'
            })
        
        consistency1 = self._calculate_player_consistency(player1_stats)
        consistency2 = self._calculate_player_consistency(player2_stats)
        
        if abs(consistency1 - consistency2) > 15:
            more_consistent = player1 if consistency1 > consistency2 else player2
            recommendations.append({
                'area': 'Consistency',
                'recommendation': f"{more_consistent.full_name} offers more reliable performances",
                'priority': 'Medium'
            })
        
        return recommendations
    
    def _get_formation_matches(self, formation, cutoff_date):
        return Match.objects.filter(
            lineups__formation=formation,
            lineups__is_starting_eleven=True,
            scheduled_datetime__gte=cutoff_date,
            status__in=['COMPLETED', 'FULL_TIME']
        ).distinct()
    
    def _extract_formation_comparison_data(self, formation, matches):
        total_matches = matches.count()
        wins = matches.filter(result='WIN').count()
        draws = matches.filter(result='DRAW').count()
        losses = matches.filter(result='LOSS').count()
        
        goals_scored = sum(match.chelsea_score for match in matches)
        goals_conceded = sum(match.opponent_score for match in matches)
        
        return {
            'formation_name': formation.name,
            'formation_id': str(formation.id),
            'matches_played': total_matches,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'win_rate': round((wins / total_matches) * 100, 2) if total_matches > 0 else 0,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'goals_per_match': round(goals_scored / total_matches, 2) if total_matches > 0 else 0,
            'goals_conceded_per_match': round(goals_conceded / total_matches, 2) if total_matches > 0 else 0,
            'goal_difference': goals_scored - goals_conceded,
            'clean_sheets': matches.filter(opponent_score=0).count(),
            'points_per_match': round(((wins * 3) + draws) / total_matches, 2) if total_matches > 0 else 0
        }
    
    def _compare_formation_effectiveness(self, formation1_matches, formation2_matches):
        f1_wins = formation1_matches.filter(result='WIN').count()
        f1_total = formation1_matches.count()
        f2_wins = formation2_matches.filter(result='WIN').count()
        f2_total = formation2_matches.count()
        
        f1_win_rate = (f1_wins / f1_total) * 100 if f1_total > 0 else 0
        f2_win_rate = (f2_wins / f2_total) * 100 if f2_total > 0 else 0
        
        f1_goals = sum(match.chelsea_score for match in formation1_matches)
        f1_conceded = sum(match.opponent_score for match in formation1_matches)
        f2_goals = sum(match.chelsea_score for match in formation2_matches)
        f2_conceded = sum(match.opponent_score for match in formation2_matches)
        
        return {
            'win_rate_comparison': {
                'formation1_win_rate': round(f1_win_rate, 2),
                'formation2_win_rate': round(f2_win_rate, 2),
                'advantage': 'formation1' if f1_win_rate > f2_win_rate else 'formation2' if f2_win_rate > f1_win_rate else 'equal'
            },
            'attacking_comparison': {
                'formation1_goals_per_match': round(f1_goals / f1_total, 2) if f1_total > 0 else 0,
                'formation2_goals_per_match': round(f2_goals / f2_total, 2) if f2_total > 0 else 0,
                'attacking_advantage': 'formation1' if (f1_goals / f1_total) > (f2_goals / f2_total) else 'formation2'
            },
            'defensive_comparison': {
                'formation1_conceded_per_match': round(f1_conceded / f1_total, 2) if f1_total > 0 else 0,
                'formation2_conceded_per_match': round(f2_conceded / f2_total, 2) if f2_total > 0 else 0,
                'defensive_advantage': 'formation1' if (f1_conceded / f1_total) < (f2_conceded / f2_total) else 'formation2'
            }
        }
    
    def _analyze_tactical_differences(self, formation1, formation2, formation1_matches, formation2_matches):
        f1_style = self._analyze_formation_style(formation1, formation1_matches)
        f2_style = self._analyze_formation_style(formation2, formation2_matches)
        
        return {
            'formation1_style': f1_style,
            'formation2_style': f2_style,
            'key_differences': self._identify_tactical_differences(f1_style, f2_style),
            'situational_suitability': self._assess_situational_suitability(formation1, formation2)
        }
    
    def _generate_formation_recommendations(self, formation1, formation2, formation1_matches, formation2_matches):
        recommendations = []
        
        f1_effectiveness = self._calculate_formation_effectiveness_score(formation1_matches)
        f2_effectiveness = self._calculate_formation_effectiveness_score(formation2_matches)
        
        if f1_effectiveness > f2_effectiveness + 10:
            recommendations.append({
                'preference': formation1.name,
                'reason': f"Higher overall effectiveness ({f1_effectiveness:.1f} vs {f2_effectiveness:.1f})",
                'confidence': 'High'
            })
        elif f2_effectiveness > f1_effectiveness + 10:
            recommendations.append({
                'preference': formation2.name,
                'reason': f"Higher overall effectiveness ({f2_effectiveness:.1f} vs {f1_effectiveness:.1f})",
                'confidence': 'High'
            })
        
        f1_attacking = sum(match.chelsea_score for match in formation1_matches) / formation1_matches.count()
        f2_attacking = sum(match.chelsea_score for match in formation2_matches) / formation2_matches.count()
        
        if f1_attacking > f2_attacking + 0.5:
            recommendations.append({
                'situation': 'Attacking priority matches',
                'recommendation': f"Use {formation1.name} for better goal output",
                'expected_benefit': f"Additional {f1_attacking - f2_attacking:.1f} goals per match"
            })
        
        return recommendations
    
    def _extract_match_comparison_data(self, match):
        try:
            team_stats = TeamStats.objects.get(match=match)
        except TeamStats.DoesNotExist:
            team_stats = None
        
        player_stats = PlayerStats.objects.filter(match=match)
        
        data = {
            'match_id': str(match.id),
            'opponent': match.opponent.name,
            'result': match.result,
            'score': f"{match.chelsea_score}-{match.opponent_score}",
            'date': match.scheduled_datetime.strftime('%d/%m/%Y'),
            'venue': 'Home' if match.is_home else 'Away',
            'goals_scored': match.chelsea_score,
            'goals_conceded': match.opponent_score
        }
        
        if team_stats:
            data.update({
                'possession': float(team_stats.possession_percentage or 50),
                'shots_on_target': team_stats.shots_on_target,
                'shots_off_target': team_stats.shots_off_target,
                'corners': team_stats.corners,
                'offsides': team_stats.offsides
            })
        
        if player_stats.exists():
            data.update({
                'team_average_rating': round(player_stats.aggregate(avg=Avg('rating'))['avg'], 2),
                'total_distance_covered': player_stats.aggregate(total=Sum('distance_covered'))['total'] or 0,
                'team_pass_accuracy': self._calculate_team_pass_accuracy(player_stats)
            })
        
        return data
    
    def _calculate_performance_differential(self, match1_data, match2_data):
        differentials = {}
        
        numeric_metrics = ['goals_scored', 'goals_conceded', 'possession', 'shots_on_target', 'team_average_rating']
        
        for metric in numeric_metrics:
            if metric in match1_data and metric in match2_data:
                m1_value = match1_data[metric]
                m2_value = match2_data[metric]
                
                if metric == 'goals_conceded':
                    better_match = 'match1' if m1_value < m2_value else 'match2' if m2_value < m1_value else 'equal'
                else:
                    better_match = 'match1' if m1_value > m2_value else 'match2' if m2_value > m1_value else 'equal'
                
                differentials[metric] = {
                    'match1_value': m1_value,
                    'match2_value': m2_value,
                    'difference': round(abs(m1_value - m2_value), 2),
                    'better_performance': better_match
                }
        
        return differentials
    
    def _compare_match_tactics(self, match1, match2):
        match1_lineup = MatchLineup.objects.filter(match=match1, is_starting_eleven=True).first()
        match2_lineup = MatchLineup.objects.filter(match=match2, is_starting_eleven=True).first()
        
        tactical_comparison = {
            'formation_comparison': 'N/A',
            'tactical_notes': []
        }
        
        if match1_lineup and match2_lineup:
            tactical_comparison['formation_comparison'] = f"{match1_lineup.formation.name} vs {match2_lineup.formation.name}"
            
            if match1_lineup.formation != match2_lineup.formation:
                tactical_comparison['tactical_notes'].append("Different formations used - tactical approach varied")
        
        return tactical_comparison
    
    def _extract_comparative_lessons(self, match1_data, match2_data):
        lessons = []
        
        if match1_data['result'] == 'WIN' and match2_data['result'] != 'WIN':
            lessons.append(f"Match 1 success factors: Better result achieved against {match1_data['opponent']}")
        
        if 'possession' in match1_data and 'possession' in match2_data:
            poss_diff = abs(match1_data['possession'] - match2_data['possession'])
            if poss_diff > 15:
                higher_poss_match = 'Match 1' if match1_data['possession'] > match2_data['possession'] else 'Match 2'
                lessons.append(f"{higher_poss_match} had significantly higher possession control")
        
        if 'team_average_rating' in match1_data and 'team_average_rating' in match2_data:
            rating_diff = abs(match1_data['team_average_rating'] - match2_data['team_average_rating'])
            if rating_diff > 1:
                better_performance = 'Match 1' if match1_data['team_average_rating'] > match2_data['team_average_rating'] else 'Match 2'
                lessons.append(f"{better_performance} featured significantly better individual performances")
        
        return lessons
    
    def _extract_opponent_comparison_data(self, opponent, matches):
        if not matches.exists():
            return {'insufficient_data': True}
        
        total_matches = matches.count()
        chelsea_wins = matches.filter(result='WIN').count()
        draws = matches.filter(result='DRAW').count()
        chelsea_losses = matches.filter(result='LOSS').count()
        
        goals_scored_against = sum(match.chelsea_score for match in matches)
        goals_conceded_to = sum(match.opponent_score for match in matches)
        
        return {
            'opponent_name': opponent.name,
            'total_matches': total_matches,
            'chelsea_wins': chelsea_wins,
            'draws': draws,
            'chelsea_losses': chelsea_losses,
            'chelsea_win_rate': round((chelsea_wins / total_matches) * 100, 2),
            'goals_scored_against_them': goals_scored_against,
            'goals_conceded_to_them': goals_conceded_to,
            'average_goals_scored': round(goals_scored_against / total_matches, 2),
            'average_goals_conceded': round(goals_conceded_to / total_matches, 2),
            'difficulty_indicator': self._calculate_opponent_difficulty(matches)
        }
    
    def _assess_opponent_difficulty(self, opponent1_matches, opponent2_matches):
        if not opponent1_matches.exists() or not opponent2_matches.exists():
            return {'insufficient_data': True}
        
        opp1_win_rate = (opponent1_matches.filter(result='WIN').count() / opponent1_matches.count()) * 100
        opp2_win_rate = (opponent2_matches.filter(result='WIN').count() / opponent2_matches.count()) * 100
        
        opp1_goals_conceded = sum(match.opponent_score for match in opponent1_matches) / opponent1_matches.count()
        opp2_goals_conceded = sum(match.opponent_score for match in opponent2_matches) / opponent2_matches.count()
        
        if opp1_win_rate > opp2_win_rate + 20:
            easier_opponent = 'opponent1'
        elif opp2_win_rate > opp1_win_rate + 20:
            easier_opponent = 'opponent2'
        else:
            easier_opponent = 'similar_difficulty'
        
        return {
            'easier_opponent': easier_opponent,
            'opponent1_win_rate': round(opp1_win_rate, 2),
            'opponent2_win_rate': round(opp2_win_rate, 2),
            'opponent1_threat_level': 'Low' if opp1_goals_conceded < 1 else 'Medium' if opp1_goals_conceded < 2 else 'High',
            'opponent2_threat_level': 'Low' if opp2_goals_conceded < 1 else 'Medium' if opp2_goals_conceded < 2 else 'High'
        }
    
    def _generate_opponent_preparation_insights(self, opponent1, opponent2, opponent1_matches, opponent2_matches):
        insights = []
        
        opp1_difficulty = self._calculate_opponent_difficulty(opponent1_matches)
        opp2_difficulty = self._calculate_opponent_difficulty(opponent2_matches)
        
        if opp1_difficulty > opp2_difficulty + 15:
            insights.append(f"{opponent1.name} requires more intensive preparation - historically more challenging")
        elif opp2_difficulty > opp1_difficulty + 15:
            insights.append(f"{opponent2.name} requires more intensive preparation - historically more challenging")
        
        opp1_recent = opponent1_matches.order_by('-scheduled_datetime')[:3]
        opp2_recent = opponent2_matches.order_by('-scheduled_datetime')[:3]
        
        if opp1_recent.exists() and opp1_recent.filter(result='WIN').count() == 0:
            insights.append(f"Recent struggles against {opponent1.name} - tactical review recommended")
        
        if opp2_recent.exists() and opp2_recent.filter(result='WIN').count() == 0:
            insights.append(f"Recent struggles against {opponent2.name} - tactical review recommended")
        
        return insights
    
    def _extract_comparative_metrics(self, stats):
        if not stats.exists():
            return {}
        
        matches_played = stats.count()
        aggregated = stats.aggregate(
            total_goals=Sum('goals'),
            total_assists=Sum('assists'),
            avg_rating=Avg('rating'),
            total_passes_completed=Sum('passes_completed'),
            total_passes_attempted=Sum('passes_attempted'),
            total_tackles=Sum('tackles'),
            total_interceptions=Sum('interceptions'),
            total_distance=Sum('distance_covered')
        )
        
        return {
            'goals_per_match': round((aggregated['total_goals'] or 0) / matches_played, 2),
            'assists_per_match': round((aggregated['total_assists'] or 0) / matches_played, 2),
            'average_rating': round(aggregated['avg_rating'] or 0, 2),
            'pass_accuracy': self._calculate_pass_accuracy(aggregated),
            'defensive_actions_per_match': round(((aggregated['total_tackles'] or 0) + (aggregated['total_interceptions'] or 0)) / matches_played, 2),
            'distance_per_match': round((aggregated['total_distance'] or 0) / matches_played, 0)
        }
    
    def _calculate_pass_accuracy(self, aggregated_stats):
        completed = aggregated_stats.get('total_passes_completed', 0) or 0
        attempted = aggregated_stats.get('total_passes_attempted', 0) or 0
        
        if attempted == 0:
            return 0
        
        return round((completed / attempted) * 100, 2)
    
    def _get_position_category(self, position):
        categories = {
            'GK': 'Goalkeeper',
            'CB': 'Defender', 'LB': 'Defender', 'RB': 'Defender',
            'CDM': 'Midfielder', 'CM': 'Midfielder', 'CAM': 'Midfielder', 'LM': 'Midfielder', 'RM': 'Midfielder',
            'LW': 'Forward', 'RW': 'Forward', 'ST': 'Forward'
        }
        return categories.get(position, 'Unknown')
    
    def _assess_comparison_validity(self, pos1, pos2):
        same_category = self._get_position_category(pos1) == self._get_position_category(pos2)
        
        if pos1 == pos2:
            return 'Highly Valid'
        elif same_category:
            return 'Valid'
        else:
            return 'Limited Validity'
    
    def _compare_attacking_performance(self, p1_metrics, p2_metrics):
        p1_attacking = p1_metrics.get('goals_per_match', 0) + (p1_metrics.get('assists_per_match', 0) * 0.7)
        p2_attacking = p2_metrics.get('goals_per_match', 0) + (p2_metrics.get('assists_per_match', 0) * 0.7)
        
        if p1_attacking > p2_attacking * 1.2:
            return 'Player 1 significantly better'
        elif p2_attacking > p1_attacking * 1.2:
            return 'Player 2 significantly better'
        elif p1_attacking > p2_attacking:
            return 'Player 1 slightly better'
        elif p2_attacking > p1_attacking:
            return 'Player 2 slightly better'
        else:
            return 'Similar attacking output'
    
    def _compare_creative_performance(self, p1_metrics, p2_metrics):
        p1_creative = p1_metrics.get('assists_per_match', 0)
        p2_creative = p2_metrics.get('assists_per_match', 0)
        
        if abs(p1_creative - p2_creative) < 0.1:
            return 'Similar creativity levels'
        else:
            return 'Player 1 more creative' if p1_creative > p2_creative else 'Player 2 more creative'
    
    def _compare_defensive_performance(self, p1_metrics, p2_metrics):
        p1_defensive = p1_metrics.get('defensive_actions_per_match', 0)
        p2_defensive = p2_metrics.get('defensive_actions_per_match', 0)
        
        if abs(p1_defensive - p2_defensive) < 1:
            return 'Similar defensive contribution'
        else:
            return 'Player 1 more defensive' if p1_defensive > p2_defensive else 'Player 2 more defensive'
    
    def _compare_consistency(self, player1_stats, player2_stats):
        p1_consistency = self._calculate_player_consistency(player1_stats)
        p2_consistency = self._calculate_player_consistency(player2_stats)
        
        if abs(p1_consistency - p2_consistency) < 10:
            return 'Similar consistency levels'
        else:
            return 'Player 1 more consistent' if p1_consistency > p2_consistency else 'Player 2 more consistent'
    
    def _compare_physical_performance(self, p1_metrics, p2_metrics):
        p1_physical = p1_metrics.get('distance_per_match', 0)
        p2_physical = p2_metrics.get('distance_per_match', 0)
        
        if abs(p1_physical - p2_physical) < 500:
            return 'Similar work rate'
        else:
            return 'Player 1 higher work rate' if p1_physical > p2_physical else 'Player 2 higher work rate'
    
    def _calculate_player_consistency(self, stats):
        ratings = [float(stat.rating) for stat in stats]
        
        if len(ratings) < 3:
            return 50
        
        mean_rating = sum(ratings) / len(ratings)
        variance = sum((r - mean_rating) ** 2 for r in ratings) / len(ratings)
        std_dev = variance ** 0.5
        
        consistency_score = max(0, 100 - (std_dev * 20))
        return round(consistency_score, 2)
    
    def _analyze_formation_style(self, formation, matches):
        total_goals = sum(match.chelsea_score for match in matches)
        total_conceded = sum(match.opponent_score for match in matches)
        matches_count = matches.count()
        
        attacking_avg = total_goals / matches_count if matches_count > 0 else 0
        defensive_avg = total_conceded / matches_count if matches_count > 0 else 0
        
        if attacking_avg > 2.5:
            attacking_style = 'High attacking output'
        elif attacking_avg > 1.5:
            attacking_style = 'Moderate attacking output'
        else:
            attacking_style = 'Conservative attacking output'
        
        if defensive_avg < 1:
            defensive_style = 'Solid defensive record'
        elif defensive_avg < 1.5:
            defensive_style = 'Reasonable defensive record'
        else:
            defensive_style = 'Vulnerable defensive record'
        
        return {
            'attacking_style': attacking_style,
            'defensive_style': defensive_style,
            'goals_per_match': round(attacking_avg, 2),
            'goals_conceded_per_match': round(defensive_avg, 2)
        }
    
    def _identify_tactical_differences(self, f1_style, f2_style):
        differences = []
        
        goals_diff = abs(f1_style['goals_per_match'] - f2_style['goals_per_match'])
        if goals_diff > 0.5:
            more_attacking = 'Formation 1' if f1_style['goals_per_match'] > f2_style['goals_per_match'] else 'Formation 2'
            differences.append(f"{more_attacking} is more attacking-oriented")
        
        defensive_diff = abs(f1_style['goals_conceded_per_match'] - f2_style['goals_conceded_per_match'])
        if defensive_diff > 0.3:
            more_solid = 'Formation 1' if f1_style['goals_conceded_per_match'] < f2_style['goals_conceded_per_match'] else 'Formation 2'
            differences.append(f"{more_solid} provides better defensive stability")
        
        return differences
    
    def _assess_situational_suitability(self, formation1, formation2):
        suitability = {}
        
        if '3' in formation1.name and '4' in formation2.name:
            suitability['attacking_situations'] = f"{formation1.name} - three at the back allows more attacking freedom"
            suitability['defensive_situations'] = f"{formation2.name} - four at the back provides more defensive cover"
        
        if '5' in formation1.name or '5' in formation2.name:
            five_back = formation1 if '5' in formation1.name else formation2
            other = formation2 if five_back == formation1 else formation1
            suitability['counter_attacking'] = f"{five_back.name} - suited for counter-attacking approach"
            suitability['possession_play'] = f"{other.name} - better for possession-based play"
        
        return suitability
    
    def _calculate_formation_effectiveness_score(self, matches):
        if not matches.exists():
            return 0
        
        wins = matches.filter(result='WIN').count()
        draws = matches.filter(result='DRAW').count()
        total = matches.count()
        
        points = (wins * 3) + draws
        points_per_match = points / total
        
        goals_scored = sum(match.chelsea_score for match in matches)
        goals_conceded = sum(match.opponent_score for match in matches)
        
        goal_difference = goals_scored - goals_conceded
        goal_difference_per_match = goal_difference / total
        
        effectiveness_score = (points_per_match * 30) + (goal_difference_per_match * 10)
        
        return round(min(100, max(0, effectiveness_score)), 1)
    
    def _calculate_team_pass_accuracy(self, player_stats):
        total_completed = player_stats.aggregate(total=Sum('passes_completed'))['total'] or 0
        total_attempted = player_stats.aggregate(total=Sum('passes_attempted'))['total'] or 0
        
        if total_attempted == 0:
            return 0
        
        return round((total_completed / total_attempted) * 100, 2)
    
    def _calculate_opponent_difficulty(self, matches):
        if not matches.exists():
            return 50
        
        chelsea_wins = matches.filter(result='WIN').count()
        total_matches = matches.count()
        win_rate = (chelsea_wins / total_matches) * 100
        
        goals_conceded = sum(match.opponent_score for match in matches)
        avg_goals_conceded = goals_conceded / total_matches
        
        difficulty_score = (100 - win_rate) + (avg_goals_conceded * 20)
        
        return round(min(100, max(0, difficulty_score)), 1)