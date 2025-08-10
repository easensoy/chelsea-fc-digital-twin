from django.db.models import Avg, Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
import logging

from .models import Player, PlayerStats, Match, TeamStats
from .exceptions import InsufficientDataError, ValidationError

logger = logging.getLogger('core.performance')

class PerformanceCalculator:
    
    def __init__(self):
        self.logger = logging.getLogger('core.performance')
        self.weight_factors = {
            'goals': 2.0,
            'assists': 1.5,
            'pass_accuracy': 0.8,
            'defensive_actions': 1.0,
            'distance_coverage': 0.3,
            'match_result': 0.5
        }
        
    def calculate_comprehensive_rating(self, player, days=30):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        recent_stats = PlayerStats.objects.filter(
            player=player,
            match__scheduled_datetime__gte=cutoff_date,
            match__status__in=['COMPLETED', 'FULL_TIME']
        ).select_related('match')
        
        if not recent_stats.exists():
            raise InsufficientDataError(f"No recent performance data available for {player.full_name}")
        
        rating_components = {
            'attacking_contribution': self._calculate_attacking_score(recent_stats),
            'passing_performance': self._calculate_passing_score(recent_stats),
            'defensive_contribution': self._calculate_defensive_score(recent_stats),
            'physical_performance': self._calculate_physical_score(recent_stats),
            'consistency_factor': self._calculate_consistency_factor(recent_stats),
            'match_impact_factor': self._calculate_match_impact_factor(recent_stats)
        }
        
        weighted_score = self._apply_position_weights(player.position, rating_components)
        final_rating = self._normalize_rating(weighted_score)
        
        return {
            'player_id': str(player.id),
            'player_name': player.full_name,
            'position': player.position,
            'calculation_period_days': days,
            'matches_analyzed': recent_stats.count(),
            'overall_rating': final_rating,
            'component_scores': rating_components,
            'rating_explanation': self._generate_rating_explanation(rating_components, final_rating),
            'performance_grade': self._assign_performance_grade(final_rating),
            'calculated_at': timezone.now().isoformat()
        }
    
    def calculate_team_performance_metrics(self, match):
        if not isinstance(match, Match):
            raise ValidationError("Invalid match object provided")
        
        try:
            team_stats = TeamStats.objects.get(match=match)
        except TeamStats.DoesNotExist:
            raise InsufficientDataError(f"No team statistics available for match {match}")
        
        player_stats = PlayerStats.objects.filter(match=match)
        
        metrics = {
            'match_info': {
                'match_id': str(match.id),
                'opponent': match.opponent.name,
                'result': match.result,
                'score': f"{match.chelsea_score}-{match.opponent_score}"
            },
            'attacking_efficiency': self._calculate_attacking_efficiency(team_stats, match),
            'possession_effectiveness': self._calculate_possession_effectiveness(team_stats, player_stats),
            'defensive_solidity': self._calculate_defensive_solidity(team_stats, match),
            'passing_metrics': self._calculate_team_passing_metrics(player_stats),
            'work_rate_analysis': self._calculate_work_rate_metrics(player_stats),
            'overall_team_rating': self._calculate_overall_team_rating(team_stats, match, player_stats)
        }
        
        return metrics
    
    def calculate_form_trajectory(self, player, matches=10):
        recent_stats = PlayerStats.objects.filter(
            player=player,
            match__status__in=['COMPLETED', 'FULL_TIME']
        ).select_related('match').order_by('-match__scheduled_datetime')[:matches]
        
        if recent_stats.count() < 3:
            raise InsufficientDataError(f"Insufficient data for form trajectory calculation: {recent_stats.count()} matches")
        
        ratings = [float(stat.rating) for stat in recent_stats]
        match_dates = [stat.match.scheduled_datetime for stat in recent_stats]
        
        trajectory_data = {
            'player_id': str(player.id),
            'player_name': player.full_name,
            'matches_analyzed': len(ratings),
            'current_form_rating': ratings[0] if ratings else 0,
            'average_form_rating': round(sum(ratings) / len(ratings), 2),
            'form_trend': self._calculate_trend(ratings),
            'form_consistency': self._calculate_form_consistency(ratings),
            'peak_performance': max(ratings),
            'lowest_performance': min(ratings),
            'performance_variance': self._calculate_variance(ratings),
            'trajectory_analysis': self._analyze_trajectory_pattern(ratings, match_dates)
        }
        
        return trajectory_data
    
    def _calculate_attacking_score(self, stats_queryset):
        totals = stats_queryset.aggregate(
            total_goals=Sum('goals'),
            total_assists=Sum('assists'),
            total_shots_on_target=Sum('shots_on_target'),
            total_shots_off_target=Sum('shots_off_target'),
            match_count=Count('id')
        )
        
        if totals['match_count'] == 0:
            return 0
        
        goals_per_match = (totals['total_goals'] or 0) / totals['match_count']
        assists_per_match = (totals['total_assists'] or 0) / totals['match_count']
        shot_accuracy = self._calculate_shot_accuracy(totals)
        
        attacking_score = (
            (goals_per_match * 25) +
            (assists_per_match * 15) +
            (shot_accuracy * 0.3)
        )
        
        return min(100, round(attacking_score, 2))
    
    def _calculate_passing_score(self, stats_queryset):
        totals = stats_queryset.aggregate(
            total_completed=Sum('passes_completed'),
            total_attempted=Sum('passes_attempted'),
            match_count=Count('id')
        )
        
        if totals['total_attempted'] == 0:
            return 50
        
        pass_accuracy = (totals['total_completed'] / totals['total_attempted']) * 100
        volume_factor = min(1.2, (totals['total_attempted'] / totals['match_count']) / 50)
        
        passing_score = pass_accuracy * volume_factor
        
        return min(100, round(passing_score, 2))
    
    def _calculate_defensive_score(self, stats_queryset):
        totals = stats_queryset.aggregate(
            total_tackles=Sum('tackles'),
            total_interceptions=Sum('interceptions'),
            total_clearances=Sum('clearances'),
            total_blocks=Sum('blocks'),
            match_count=Count('id')
        )
        
        if totals['match_count'] == 0:
            return 0
        
        defensive_actions_per_match = (
            (totals['total_tackles'] or 0) +
            (totals['total_interceptions'] or 0) +
            (totals['total_clearances'] or 0) +
            (totals['total_blocks'] or 0)
        ) / totals['match_count']
        
        defensive_score = min(100, defensive_actions_per_match * 5)
        
        return round(defensive_score, 2)
    
    def _calculate_physical_score(self, stats_queryset):
        totals = stats_queryset.aggregate(
            total_distance=Sum('distance_covered'),
            total_sprints=Sum('sprints'),
            total_minutes=Sum('minutes_played'),
            match_count=Count('id')
        )
        
        if totals['total_minutes'] == 0:
            return 0
        
        distance_per_minute = (totals['total_distance'] or 0) / totals['total_minutes']
        sprint_intensity = (totals['total_sprints'] or 0) / totals['match_count']
        
        physical_score = (distance_per_minute * 0.8) + (sprint_intensity * 2)
        
        return min(100, round(physical_score, 2))
    
    def _calculate_consistency_factor(self, stats_queryset):
        ratings = [float(stat.rating) for stat in stats_queryset]
        
        if len(ratings) < 3:
            return 50
        
        variance = self._calculate_variance(ratings)
        consistency_score = max(0, 100 - (variance * 20))
        
        return round(consistency_score, 2)
    
    def _calculate_match_impact_factor(self, stats_queryset):
        impact_score = 0
        total_matches = stats_queryset.count()
        
        if total_matches == 0:
            return 0
        
        for stat in stats_queryset:
            match_impact = 0
            
            if stat.match.result == 'WIN':
                match_impact += 5
            elif stat.match.result == 'DRAW':
                match_impact += 2
            
            if stat.goals > 0:
                match_impact += stat.goals * 10
            if stat.assists > 0:
                match_impact += stat.assists * 7
            
            if stat.rating >= 8.0:
                match_impact += 8
            elif stat.rating >= 7.0:
                match_impact += 4
            
            impact_score += match_impact
        
        average_impact = impact_score / total_matches
        normalized_impact = min(100, average_impact * 2)
        
        return round(normalized_impact, 2)
    
    def _apply_position_weights(self, position, components):
        position_weights = {
            'GK': {
                'attacking_contribution': 0.1,
                'passing_performance': 0.3,
                'defensive_contribution': 0.4,
                'physical_performance': 0.2,
                'consistency_factor': 0.3,
                'match_impact_factor': 0.3
            },
            'CB': {
                'attacking_contribution': 0.2,
                'passing_performance': 0.3,
                'defensive_contribution': 0.4,
                'physical_performance': 0.25,
                'consistency_factor': 0.3,
                'match_impact_factor': 0.25
            },
            'LB': {
                'attacking_contribution': 0.3,
                'passing_performance': 0.3,
                'defensive_contribution': 0.3,
                'physical_performance': 0.3,
                'consistency_factor': 0.25,
                'match_impact_factor': 0.25
            },
            'RB': {
                'attacking_contribution': 0.3,
                'passing_performance': 0.3,
                'defensive_contribution': 0.3,
                'physical_performance': 0.3,
                'consistency_factor': 0.25,
                'match_impact_factor': 0.25
            },
            'CDM': {
                'attacking_contribution': 0.25,
                'passing_performance': 0.4,
                'defensive_contribution': 0.35,
                'physical_performance': 0.3,
                'consistency_factor': 0.3,
                'match_impact_factor': 0.25
            },
            'CM': {
                'attacking_contribution': 0.35,
                'passing_performance': 0.4,
                'defensive_contribution': 0.25,
                'physical_performance': 0.3,
                'consistency_factor': 0.25,
                'match_impact_factor': 0.3
            },
            'CAM': {
                'attacking_contribution': 0.45,
                'passing_performance': 0.35,
                'defensive_contribution': 0.15,
                'physical_performance': 0.25,
                'consistency_factor': 0.25,
                'match_impact_factor': 0.35
            },
            'LW': {
                'attacking_contribution': 0.5,
                'passing_performance': 0.25,
                'defensive_contribution': 0.15,
                'physical_performance': 0.3,
                'consistency_factor': 0.2,
                'match_impact_factor': 0.4
            },
            'RW': {
                'attacking_contribution': 0.5,
                'passing_performance': 0.25,
                'defensive_contribution': 0.15,
                'physical_performance': 0.3,
                'consistency_factor': 0.2,
                'match_impact_factor': 0.4
            },
            'ST': {
                'attacking_contribution': 0.6,
                'passing_performance': 0.2,
                'defensive_contribution': 0.1,
                'physical_performance': 0.25,
                'consistency_factor': 0.2,
                'match_impact_factor': 0.45
            }
        }
        
        weights = position_weights.get(position, position_weights['CM'])
        
        weighted_score = sum(
            components[component] * weights[component]
            for component in components
        )
        
        return weighted_score
    
    def _normalize_rating(self, weighted_score):
        normalized = min(10, max(1, weighted_score / 10))
        return float(Decimal(str(normalized)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
    
    def _generate_rating_explanation(self, components, final_rating):
        explanations = []
        
        if components['attacking_contribution'] > 80:
            explanations.append("Excellent attacking output")
        elif components['attacking_contribution'] > 60:
            explanations.append("Good attacking contribution")
        elif components['attacking_contribution'] < 30:
            explanations.append("Limited attacking threat")
        
        if components['consistency_factor'] > 80:
            explanations.append("Highly consistent performances")
        elif components['consistency_factor'] < 50:
            explanations.append("Inconsistent performance levels")
        
        if components['match_impact_factor'] > 80:
            explanations.append("Significant match-winning contributions")
        
        if final_rating >= 8.0:
            explanations.append("Outstanding overall performance level")
        elif final_rating >= 7.0:
            explanations.append("Strong overall performance level")
        elif final_rating < 6.0:
            explanations.append("Performance below expectations")
        
        return explanations
    
    def _assign_performance_grade(self, rating):
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
    
    def _calculate_shot_accuracy(self, totals):
        total_shots = (totals['total_shots_on_target'] or 0) + (totals['total_shots_off_target'] or 0)
        if total_shots == 0:
            return 0
        return ((totals['total_shots_on_target'] or 0) / total_shots) * 100
    
    def _calculate_variance(self, values):
        if len(values) <= 1:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def _calculate_trend(self, ratings):
        if len(ratings) < 3:
            return 'insufficient_data'
        
        recent_avg = sum(ratings[:3]) / 3
        earlier_avg = sum(ratings[-3:]) / 3
        
        difference = recent_avg - earlier_avg
        
        if difference > 0.5:
            return 'improving'
        elif difference < -0.5:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_form_consistency(self, ratings):
        if len(ratings) < 3:
            return 0
        
        variance = self._calculate_variance(ratings)
        consistency_score = max(0, 100 - (variance * 15))
        
        return round(consistency_score, 2)
    
    def _analyze_trajectory_pattern(self, ratings, dates):
        if len(ratings) < 5:
            return 'insufficient_data_for_pattern_analysis'
        
        recent_third = ratings[:len(ratings)//3]
        middle_third = ratings[len(ratings)//3:2*len(ratings)//3]
        early_third = ratings[2*len(ratings)//3:]
        
        recent_avg = sum(recent_third) / len(recent_third)
        middle_avg = sum(middle_third) / len(middle_third)
        early_avg = sum(early_third) / len(early_third)
        
        if recent_avg > middle_avg > early_avg:
            return 'steady_improvement'
        elif recent_avg < middle_avg < early_avg:
            return 'steady_decline'
        elif recent_avg > early_avg and abs(recent_avg - middle_avg) < 0.3:
            return 'overall_positive_with_stability'
        else:
            return 'fluctuating_form'
    
    def _calculate_attacking_efficiency(self, team_stats, match):
        total_shots = team_stats.shots_on_target + team_stats.shots_off_target + team_stats.shots_blocked
        goals_scored = match.chelsea_score
        
        if total_shots == 0:
            return {'conversion_rate': 0, 'shots_per_goal': 0, 'efficiency_rating': 'Poor'}
        
        conversion_rate = (goals_scored / total_shots) * 100
        shots_per_goal = total_shots / max(goals_scored, 1)
        
        if conversion_rate >= 20:
            efficiency_rating = 'Excellent'
        elif conversion_rate >= 15:
            efficiency_rating = 'Good'
        elif conversion_rate >= 10:
            efficiency_rating = 'Average'
        else:
            efficiency_rating = 'Poor'
        
        return {
            'conversion_rate': round(conversion_rate, 2),
            'shots_per_goal': round(shots_per_goal, 2),
            'total_shots': total_shots,
            'efficiency_rating': efficiency_rating
        }
    
    def _calculate_possession_effectiveness(self, team_stats, player_stats):
        possession_pct = float(team_stats.possession_percentage or 50)
        
        total_passes = player_stats.aggregate(total=Sum('passes_attempted'))['total'] or 0
        completed_passes = player_stats.aggregate(total=Sum('passes_completed'))['total'] or 0
        
        pass_accuracy = (completed_passes / total_passes * 100) if total_passes > 0 else 0
        
        effectiveness_score = (possession_pct * 0.6) + (pass_accuracy * 0.4)
        
        return {
            'possession_percentage': possession_pct,
            'pass_accuracy': round(pass_accuracy, 2),
            'effectiveness_score': round(effectiveness_score, 2),
            'possession_quality': 'High' if effectiveness_score > 75 else 'Medium' if effectiveness_score > 60 else 'Low'
        }
    
    def _calculate_defensive_solidity(self, team_stats, match):
        goals_conceded = match.opponent_score
        
        if goals_conceded == 0:
            solidity_rating = 'Excellent'
            solidity_score = 100
        elif goals_conceded == 1:
            solidity_rating = 'Good'
            solidity_score = 80
        elif goals_conceded == 2:
            solidity_rating = 'Average'
            solidity_score = 60
        else:
            solidity_rating = 'Poor'
            solidity_score = max(20, 60 - (goals_conceded * 10))
        
        return {
            'goals_conceded': goals_conceded,
            'clean_sheet': goals_conceded == 0,
            'solidity_score': solidity_score,
            'solidity_rating': solidity_rating
        }
    
    def _calculate_team_passing_metrics(self, player_stats):
        totals = player_stats.aggregate(
            total_completed=Sum('passes_completed'),
            total_attempted=Sum('passes_attempted')
        )
        
        if totals['total_attempted'] == 0:
            return {'accuracy': 0, 'volume': 0, 'rating': 'No Data'}
        
        accuracy = (totals['total_completed'] / totals['total_attempted']) * 100
        volume = totals['total_attempted']
        
        rating = 'Excellent' if accuracy > 85 else 'Good' if accuracy > 75 else 'Average' if accuracy > 65 else 'Poor'
        
        return {
            'accuracy': round(accuracy, 2),
            'volume': volume,
            'completed_passes': totals['total_completed'],
            'rating': rating
        }
    
    def _calculate_work_rate_metrics(self, player_stats):
        totals = player_stats.aggregate(
            total_distance=Sum('distance_covered'),
            total_sprints=Sum('sprints'),
            player_count=Count('id')
        )
        
        if totals['player_count'] == 0:
            return {'average_distance': 0, 'average_sprints': 0, 'work_rate_assessment': 'No Data'}
        
        avg_distance = (totals['total_distance'] or 0) / totals['player_count']
        avg_sprints = (totals['total_sprints'] or 0) / totals['player_count']
        
        if avg_distance > 11000:
            work_rate_assessment = 'High Intensity'
        elif avg_distance > 9000:
            work_rate_assessment = 'Good Work Rate'
        else:
            work_rate_assessment = 'Below Average'
        
        return {
            'average_distance': round(avg_distance, 0),
            'average_sprints': round(avg_sprints, 1),
            'total_distance': totals['total_distance'] or 0,
            'work_rate_assessment': work_rate_assessment
        }
    
    def _calculate_overall_team_rating(self, team_stats, match, player_stats):
        result_score = 3 if match.result == 'WIN' else 1 if match.result == 'DRAW' else 0
        
        avg_player_rating = player_stats.aggregate(avg=Avg('rating'))['avg'] or 5
        
        attacking_metrics = self._calculate_attacking_efficiency(team_stats, match)
        possession_metrics = self._calculate_possession_effectiveness(team_stats, player_stats)
        defensive_metrics = self._calculate_defensive_solidity(team_stats, match)
        
        component_score = (
            (attacking_metrics['conversion_rate'] / 5) +
            (possession_metrics['effectiveness_score'] / 10) +
            (defensive_metrics['solidity_score'] / 10)
        )
        
        overall_rating = (
            (result_score * 0.3) +
            (avg_player_rating * 0.4) +
            (component_score * 0.3)
        )
        
        return round(min(10, max(1, overall_rating)), 1)