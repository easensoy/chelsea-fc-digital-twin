from django.db.models import Avg, Sum, Count, Max, Min
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging

from .models import Player, PlayerStats, Match, MatchEvent
from .exceptions import PlayerNotFoundError, InsufficientDataError

logger = logging.getLogger('core.performance')

class CareerAnalyzer:
    
    def __init__(self):
        self.logger = logging.getLogger('core.performance')
    
    def get_career_overview(self, player):
        if not isinstance(player, Player):
            raise PlayerNotFoundError("Invalid player object provided")
        
        career_stats = PlayerStats.objects.filter(player=player)
        
        if not career_stats.exists():
            raise InsufficientDataError(f"No career data available for {player.full_name}")
        
        total_matches = career_stats.count()
        total_minutes = career_stats.aggregate(total=Sum('minutes_played'))['total'] or 0
        
        overview = {
            'player_id': str(player.id),
            'player_name': player.full_name,
            'position': player.position,
            'career_statistics': self._calculate_career_statistics(career_stats, total_matches),
            'performance_analysis': self._analyze_performance_trajectory(career_stats),
            'milestones': self._identify_career_milestones(player, career_stats),
            'consistency_metrics': self._calculate_consistency_metrics(career_stats),
            'career_highlights': self._extract_career_highlights(player, career_stats),
            'development_trajectory': self._analyze_development_trajectory(career_stats)
        }
        
        self.logger.info(f"Career analysis completed for {player.full_name}: {total_matches} matches analyzed")
        return overview
    
    def _calculate_career_statistics(self, career_stats, total_matches):
        return {
            'total_matches': total_matches,
            'total_minutes': career_stats.aggregate(total=Sum('minutes_played'))['total'] or 0,
            'total_goals': career_stats.aggregate(total=Sum('goals'))['total'] or 0,
            'total_assists': career_stats.aggregate(total=Sum('assists'))['total'] or 0,
            'average_rating': round(career_stats.aggregate(avg=Avg('rating'))['avg'] or 0, 2),
            'highest_rating': career_stats.aggregate(max=Max('rating'))['max'] or 0,
            'goals_per_match': round((career_stats.aggregate(total=Sum('goals'))['total'] or 0) / max(total_matches, 1), 2),
            'assists_per_match': round((career_stats.aggregate(total=Sum('assists'))['total'] or 0) / max(total_matches, 1), 2),
            'pass_accuracy': self._calculate_overall_pass_accuracy(career_stats),
            'distance_covered_total': career_stats.aggregate(total=Sum('distance_covered'))['total'] or 0
        }
    
    def _calculate_overall_pass_accuracy(self, career_stats):
        total_completed = career_stats.aggregate(total=Sum('passes_completed'))['total'] or 0
        total_attempted = career_stats.aggregate(total=Sum('passes_attempted'))['total'] or 0
        
        if total_attempted == 0:
            return 0
        
        return round((total_completed / total_attempted) * 100, 2)
    
    def _analyze_performance_trajectory(self, career_stats):
        recent_stats = career_stats.order_by('-match__scheduled_datetime')[:10]
        early_stats = career_stats.order_by('match__scheduled_datetime')[:10]
        
        recent_avg = recent_stats.aggregate(avg=Avg('rating'))['avg'] or 0
        early_avg = early_stats.aggregate(avg=Avg('rating'))['avg'] or 0
        
        trajectory = 'improving' if recent_avg > early_avg + 0.3 else 'declining' if recent_avg < early_avg - 0.3 else 'stable'
        
        return {
            'trajectory': trajectory,
            'recent_form_rating': round(recent_avg, 2),
            'early_form_rating': round(early_avg, 2),
            'improvement_rate': round(recent_avg - early_avg, 2),
            'form_analysis': self._analyze_form_periods(career_stats)
        }
    
    def _analyze_form_periods(self, career_stats):
        stats_by_month = {}
        for stat in career_stats.select_related('match'):
            month_key = stat.match.scheduled_datetime.strftime('%Y-%m')
            if month_key not in stats_by_month:
                stats_by_month[month_key] = []
            stats_by_month[month_key].append(stat.rating)
        
        monthly_averages = {}
        for month, ratings in stats_by_month.items():
            monthly_averages[month] = sum(ratings) / len(ratings)
        
        best_month = max(monthly_averages.items(), key=lambda x: x[1]) if monthly_averages else ('N/A', 0)
        worst_month = min(monthly_averages.items(), key=lambda x: x[1]) if monthly_averages else ('N/A', 0)
        
        return {
            'best_month': {'period': best_month[0], 'rating': round(best_month[1], 2)},
            'worst_month': {'period': worst_month[0], 'rating': round(worst_month[1], 2)},
            'monthly_consistency': round(self._calculate_variance([avg for avg in monthly_averages.values()]), 2)
        }
    
    def _identify_career_milestones(self, player, career_stats):
        milestones = []
        
        total_goals = career_stats.aggregate(total=Sum('goals'))['total'] or 0
        total_assists = career_stats.aggregate(total=Sum('assists'))['total'] or 0
        total_matches = career_stats.count()
        
        goal_milestones = [1, 5, 10, 25, 50, 100]
        for milestone in goal_milestones:
            if total_goals >= milestone:
                milestones.append({
                    'type': 'goals',
                    'achievement': f'{milestone} career goals',
                    'status': 'achieved'
                })
        
        assist_milestones = [1, 5, 10, 25, 50]
        for milestone in assist_milestones:
            if total_assists >= milestone:
                milestones.append({
                    'type': 'assists',
                    'achievement': f'{milestone} career assists',
                    'status': 'achieved'
                })
        
        appearance_milestones = [1, 10, 25, 50, 100, 200]
        for milestone in appearance_milestones:
            if total_matches >= milestone:
                milestones.append({
                    'type': 'appearances',
                    'achievement': f'{milestone} appearances',
                    'status': 'achieved'
                })
        
        highest_rating = career_stats.aggregate(max=Max('rating'))['max'] or 0
        if highest_rating >= 9.0:
            milestones.append({
                'type': 'performance',
                'achievement': f'Achieved {highest_rating}/10 match rating',
                'status': 'achieved'
            })
        
        return milestones
    
    def _calculate_consistency_metrics(self, career_stats):
        ratings = [stat.rating for stat in career_stats]
        
        if not ratings:
            return {'variance': 0, 'consistency_score': 0, 'reliability_index': 0}
        
        variance = self._calculate_variance(ratings)
        consistency_score = max(0, 100 - (variance * 10))
        
        matches_above_seven = len([r for r in ratings if r >= 7.0])
        reliability_index = (matches_above_seven / len(ratings)) * 100 if ratings else 0
        
        return {
            'variance': round(variance, 2),
            'consistency_score': round(consistency_score, 2),
            'reliability_index': round(reliability_index, 2),
            'performance_range': {
                'highest': max(ratings),
                'lowest': min(ratings),
                'spread': round(max(ratings) - min(ratings), 2)
            }
        }
    
    def _extract_career_highlights(self, player, career_stats):
        highlights = []
        
        best_performance = career_stats.order_by('-rating').first()
        if best_performance:
            highlights.append({
                'type': 'best_match',
                'description': f'Best performance: {best_performance.rating}/10 rating',
                'match': str(best_performance.match),
                'date': best_performance.match.scheduled_datetime.strftime('%d/%m/%Y')
            })
        
        highest_goal_match = career_stats.filter(goals__gt=0).order_by('-goals').first()
        if highest_goal_match and highest_goal_match.goals > 1:
            highlights.append({
                'type': 'goals',
                'description': f'{highest_goal_match.goals} goals in single match',
                'match': str(highest_goal_match.match),
                'date': highest_goal_match.match.scheduled_datetime.strftime('%d/%m/%Y')
            })
        
        highest_assist_match = career_stats.filter(assists__gt=0).order_by('-assists').first()
        if highest_assist_match and highest_assist_match.assists > 1:
            highlights.append({
                'type': 'assists',
                'description': f'{highest_assist_match.assists} assists in single match',
                'match': str(highest_assist_match.match),
                'date': highest_assist_match.match.scheduled_datetime.strftime('%d/%m/%Y')
            })
        
        return highlights
    
    def _analyze_development_trajectory(self, career_stats):
        if career_stats.count() < 10:
            return {'insufficient_data': True}
        
        stats_chronological = career_stats.order_by('match__scheduled_datetime')
        early_period = stats_chronological[:career_stats.count()//3]
        late_period = stats_chronological[2*career_stats.count()//3:]
        
        early_metrics = {
            'rating': early_period.aggregate(avg=Avg('rating'))['avg'] or 0,
            'goals': early_period.aggregate(avg=Avg('goals'))['avg'] or 0,
            'assists': early_period.aggregate(avg=Avg('assists'))['avg'] or 0
        }
        
        late_metrics = {
            'rating': late_period.aggregate(avg=Avg('rating'))['avg'] or 0,
            'goals': late_period.aggregate(avg=Avg('goals'))['avg'] or 0,
            'assists': late_period.aggregate(avg=Avg('assists'))['avg'] or 0
        }
        
        development_areas = []
        if late_metrics['rating'] > early_metrics['rating'] + 0.5:
            development_areas.append('Overall performance significantly improved')
        if late_metrics['goals'] > early_metrics['goals'] + 0.1:
            development_areas.append('Goal scoring ability enhanced')
        if late_metrics['assists'] > early_metrics['assists'] + 0.1:
            development_areas.append('Creative contribution increased')
        
        return {
            'early_period_avg': round(early_metrics['rating'], 2),
            'recent_period_avg': round(late_metrics['rating'], 2),
            'development_areas': development_areas,
            'overall_progression': 'positive' if late_metrics['rating'] > early_metrics['rating'] else 'needs_attention'
        }
    
    def _calculate_variance(self, values):
        if len(values) <= 1:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5