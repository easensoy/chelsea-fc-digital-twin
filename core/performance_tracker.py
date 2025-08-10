from django.db.models import Avg, Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging

from .models import Player, PlayerStats, Match, MatchEvent

logger = logging.getLogger('core.performance')

class PerformanceTracker:
    
    def __init__(self):
        self.logger = logging.getLogger('core.performance')
    
    def get_player_performance(self, player, days=30):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        recent_matches = Match.objects.filter(
            scheduled_datetime__date__range=[start_date, end_date],
            status__in=['COMPLETED', 'FULL_TIME']
        )
        
        stats = PlayerStats.objects.filter(
            player=player,
            match__in=recent_matches
        )
        
        if not stats.exists():
            return self._empty_performance_data()
        
        performance_data = {
            'player_id': str(player.id),
            'player_name': player.full_name,
            'position': player.position,
            'period_days': days,
            'matches_played': stats.count(),
            'total_minutes': stats.aggregate(total=Sum('minutes_played'))['total'] or 0,
            'goals': stats.aggregate(total=Sum('goals'))['total'] or 0,
            'assists': stats.aggregate(total=Sum('assists'))['total'] or 0,
            'average_rating': round(stats.aggregate(avg=Avg('rating'))['avg'] or 0, 2),
            'pass_accuracy': self._calculate_pass_accuracy(stats),
            'distance_covered': stats.aggregate(total=Sum('distance_covered'))['total'] or 0,
            'performance_trends': self._calculate_performance_trends(player, days),
            'key_metrics': self._calculate_key_metrics(stats),
            'fitness_indicator': self._calculate_fitness_indicator(player, stats)
        }
        
        self.logger.info(f"Performance calculated for {player.full_name}: rating {performance_data['average_rating']}")
        return performance_data
    
    def _calculate_pass_accuracy(self, stats):
        total_completed = stats.aggregate(total=Sum('passes_completed'))['total'] or 0
        total_attempted = stats.aggregate(total=Sum('passes_attempted'))['total'] or 0
        
        if total_attempted == 0:
            return 0
        
        return round((total_completed / total_attempted) * 100, 2)
    
    def _calculate_performance_trends(self, player, days=30):
        matches = Match.objects.filter(
            scheduled_datetime__date__gte=timezone.now().date() - timedelta(days=days),
            status__in=['COMPLETED', 'FULL_TIME']
        ).order_by('scheduled_datetime')
        
        trend_data = []
        for match in matches:
            try:
                stats = PlayerStats.objects.get(player=player, match=match)
                trend_data.append({
                    'match_date': match.scheduled_datetime.date().isoformat(),
                    'opponent': match.opponent.name,
                    'rating': float(stats.rating),
                    'goals': stats.goals,
                    'assists': stats.assists,
                    'minutes_played': stats.minutes_played
                })
            except PlayerStats.DoesNotExist:
                continue
        
        return trend_data
    
    def _calculate_key_metrics(self, stats):
        total_shots = stats.aggregate(
            on_target=Sum('shots_on_target'),
            off_target=Sum('shots_off_target')
        )
        
        total_tackles = stats.aggregate(
            won=Sum('tackles_won'),
            attempted=Sum('tackles_attempted')
        )
        
        return {
            'shot_accuracy': self._calculate_percentage(
                total_shots['on_target'] or 0,
                (total_shots['on_target'] or 0) + (total_shots['off_target'] or 0)
            ),
            'tackle_success_rate': self._calculate_percentage(
                total_tackles['won'] or 0,
                total_tackles['attempted'] or 0
            ),
            'goals_per_match': round(
                (stats.aggregate(total=Sum('goals'))['total'] or 0) / max(stats.count(), 1), 2
            ),
            'assists_per_match': round(
                (stats.aggregate(total=Sum('assists'))['total'] or 0) / max(stats.count(), 1), 2
            )
        }
    
    def _calculate_fitness_indicator(self, player, stats):
        if not stats.exists():
            return player.fitness_level
        
        recent_distance = stats.aggregate(avg=Avg('distance_covered'))['avg'] or 0
        recent_sprints = stats.aggregate(avg=Avg('sprints'))['avg'] or 0
        
        historical_distance = PlayerStats.objects.filter(
            player=player
        ).aggregate(avg=Avg('distance_covered'))['avg'] or recent_distance
        
        historical_sprints = PlayerStats.objects.filter(
            player=player
        ).aggregate(avg=Avg('sprints'))['avg'] or recent_sprints
        
        distance_ratio = recent_distance / max(historical_distance, 1)
        sprint_ratio = recent_sprints / max(historical_sprints, 1)
        
        fitness_score = min(100, int((distance_ratio + sprint_ratio) / 2 * player.fitness_level))
        return max(0, fitness_score)
    
    def _calculate_percentage(self, numerator, denominator):
        if denominator == 0:
            return 0
        return round((numerator / denominator) * 100, 2)
    
    def _empty_performance_data(self):
        return {
            'matches_played': 0,
            'total_minutes': 0,
            'goals': 0,
            'assists': 0,
            'average_rating': 0,
            'pass_accuracy': 0,
            'distance_covered': 0,
            'performance_trends': [],
            'key_metrics': {
                'shot_accuracy': 0,
                'tackle_success_rate': 0,
                'goals_per_match': 0,
                'assists_per_match': 0
            },
            'fitness_indicator': 0
        }
    
    def get_performance_trends(self, player, periods=5):
        trends = []
        for i in range(periods):
            start_period = (i + 1) * 7
            end_period = i * 7
            
            start_date = timezone.now().date() - timedelta(days=start_period)
            end_date = timezone.now().date() - timedelta(days=end_period)
            
            period_stats = PlayerStats.objects.filter(
                player=player,
                match__scheduled_datetime__date__range=[start_date, end_date],
                match__status__in=['COMPLETED', 'FULL_TIME']
            )
            
            if period_stats.exists():
                avg_rating = period_stats.aggregate(avg=Avg('rating'))['avg'] or 0
                trends.append({
                    'period': f"Week {periods - i}",
                    'average_rating': round(avg_rating, 2),
                    'matches': period_stats.count()
                })
            else:
                trends.append({
                    'period': f"Week {periods - i}",
                    'average_rating': 0,
                    'matches': 0
                })
        
        return trends
    
    def calculate_player_impact_score(self, player, match):
        try:
            stats = PlayerStats.objects.get(player=player, match=match)
        except PlayerStats.DoesNotExist:
            return 0
        
        position_weights = {
            'GK': {'goals': 0, 'assists': 0, 'saves': 10, 'clean_sheet': 15},
            'CB': {'goals': 8, 'assists': 5, 'tackles': 3, 'clearances': 2, 'interceptions': 3},
            'LB': {'goals': 6, 'assists': 8, 'tackles': 3, 'crosses': 2},
            'RB': {'goals': 6, 'assists': 8, 'tackles': 3, 'crosses': 2},
            'CDM': {'goals': 5, 'assists': 6, 'tackles': 4, 'interceptions': 4, 'passes': 1},
            'CM': {'goals': 6, 'assists': 8, 'tackles': 2, 'passes': 2},
            'CAM': {'goals': 8, 'assists': 10, 'shots': 2, 'passes': 1},
            'LM': {'goals': 7, 'assists': 9, 'crosses': 3, 'shots': 2},
            'RM': {'goals': 7, 'assists': 9, 'crosses': 3, 'shots': 2},
            'LW': {'goals': 9, 'assists': 8, 'shots': 3, 'crosses': 2},
            'RW': {'goals': 9, 'assists': 8, 'shots': 3, 'crosses': 2},
            'ST': {'goals': 15, 'assists': 6, 'shots': 2}
        }
        
        weights = position_weights.get(player.position, position_weights['CM'])
        
        impact_score = 0
        impact_score += stats.goals * weights.get('goals', 10)
        impact_score += stats.assists * weights.get('assists', 8)
        impact_score += stats.tackles_won * weights.get('tackles', 2)
        impact_score += stats.interceptions * weights.get('interceptions', 2)
        impact_score += stats.clearances * weights.get('clearances', 1)
        impact_score += (stats.shots_on_target + stats.shots_off_target) * weights.get('shots', 1)
        impact_score += stats.crosses_completed * weights.get('crosses', 1)
        impact_score += (stats.passes_completed / 10) * weights.get('passes', 1)
        
        return round(impact_score, 2)
    
    def get_team_performance_summary(self, match):
        team_stats = PlayerStats.objects.filter(match=match)
        
        if not team_stats.exists():
            return {}
        
        summary = {
            'total_players': team_stats.count(),
            'average_rating': round(team_stats.aggregate(avg=Avg('rating'))['avg'] or 0, 2),
            'total_goals': team_stats.aggregate(total=Sum('goals'))['total'] or 0,
            'total_assists': team_stats.aggregate(total=Sum('assists'))['total'] or 0,
            'team_pass_accuracy': self._calculate_pass_accuracy(team_stats),
            'total_distance': round(team_stats.aggregate(total=Sum('distance_covered'))['total'] or 0, 2),
            'top_performers': self._get_top_performers(team_stats),
            'position_analysis': self._analyze_by_position(team_stats)
        }
        
        return summary
    
    def _get_top_performers(self, team_stats):
        top_performers = team_stats.order_by('-rating')[:3]
        return [
            {
                'player_name': stats.player.full_name,
                'position': stats.player.position,
                'rating': float(stats.rating),
                'goals': stats.goals,
                'assists': stats.assists
            }
            for stats in top_performers
        ]
    
    def _analyze_by_position(self, team_stats):
        position_analysis = {}
        
        for position in ['GK', 'CB', 'LB', 'RB', 'CDM', 'CM', 'CAM', 'LM', 'RM', 'LW', 'RW', 'ST']:
            position_stats = team_stats.filter(player__position=position)
            if position_stats.exists():
                position_analysis[position] = {
                    'players': position_stats.count(),
                    'average_rating': round(position_stats.aggregate(avg=Avg('rating'))['avg'] or 0, 2),
                    'total_goals': position_stats.aggregate(total=Sum('goals'))['total'] or 0,
                    'total_assists': position_stats.aggregate(total=Sum('assists'))['total'] or 0
                }
        
        return position_analysis