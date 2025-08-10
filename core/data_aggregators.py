from django.db.models import Avg, Sum, Count, Q, F, Max, Min
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from collections import defaultdict, OrderedDict
import logging

from .models import Player, PlayerStats, Match, TeamStats, Formation, MatchLineup, Opponent, Analytics
from .exceptions import InsufficientDataError

logger = logging.getLogger('core.performance')

class DataAggregators:
    
    def __init__(self):
        self.logger = logging.getLogger('core.performance')
    
    def aggregate_player_season_stats(self, season_start=None, position_filter=None):
        if not season_start:
            season_start = timezone.now().date() - timedelta(days=180)
        
        players_query = Player.objects.filter(is_active=True)
        if position_filter:
            players_query = players_query.filter(position=position_filter)
        
        aggregated_data = []
        
        for player in players_query:
            player_stats = PlayerStats.objects.filter(
                player=player,
                match__scheduled_datetime__date__gte=season_start,
                match__status__in=['COMPLETED', 'FULL_TIME']
            )
            
            if player_stats.exists():
                stats_summary = player_stats.aggregate(
                    matches_played=Count('id'),
                    total_minutes=Sum('minutes_played'),
                    total_goals=Sum('goals'),
                    total_assists=Sum('assists'),
                    avg_rating=Avg('rating'),
                    total_passes_completed=Sum('passes_completed'),
                    total_passes_attempted=Sum('passes_attempted'),
                    total_distance=Sum('distance_covered'),
                    total_tackles=Sum('tackles'),
                    total_interceptions=Sum('interceptions')
                )
                
                aggregated_data.append({
                    'player_id': str(player.id),
                    'player_name': player.full_name,
                    'position': player.position,
                    'squad_number': player.squad_number,
                    'matches_played': stats_summary['matches_played'],
                    'total_minutes': stats_summary['total_minutes'] or 0,
                    'goals': stats_summary['total_goals'] or 0,
                    'assists': stats_summary['total_assists'] or 0,
                    'goals_per_match': round((stats_summary['total_goals'] or 0) / max(stats_summary['matches_played'], 1), 2),
                    'assists_per_match': round((stats_summary['total_assists'] or 0) / max(stats_summary['matches_played'], 1), 2),
                    'average_rating': round(stats_summary['avg_rating'] or 0, 2),
                    'pass_accuracy': self._calculate_pass_accuracy(stats_summary),
                    'total_distance': stats_summary['total_distance'] or 0,
                    'defensive_actions': (stats_summary['total_tackles'] or 0) + (stats_summary['total_interceptions'] or 0),
                    'minutes_per_match': round((stats_summary['total_minutes'] or 0) / max(stats_summary['matches_played'], 1), 1)
                })
        
        return sorted(aggregated_data, key=lambda x: x['average_rating'], reverse=True)
    
    def aggregate_team_monthly_performance(self, months=12):
        cutoff_date = timezone.now() - timedelta(days=months * 30)
        
        matches = Match.objects.filter(
            scheduled_datetime__gte=cutoff_date,
            status__in=['COMPLETED', 'FULL_TIME']
        ).order_by('scheduled_datetime')
        
        monthly_data = defaultdict(lambda: {
            'matches': 0, 'wins': 0, 'draws': 0, 'losses': 0,
            'goals_scored': 0, 'goals_conceded': 0, 'points': 0
        })
        
        for match in matches:
            month_key = match.scheduled_datetime.strftime('%Y-%m')
            monthly_data[month_key]['matches'] += 1
            monthly_data[month_key]['goals_scored'] += match.chelsea_score
            monthly_data[month_key]['goals_conceded'] += match.opponent_score
            
            if match.result == 'WIN':
                monthly_data[month_key]['wins'] += 1
                monthly_data[month_key]['points'] += 3
            elif match.result == 'DRAW':
                monthly_data[month_key]['draws'] += 1
                monthly_data[month_key]['points'] += 1
            else:
                monthly_data[month_key]['losses'] += 1
        
        formatted_data = []
        for month, data in sorted(monthly_data.items()):
            formatted_data.append({
                'month': month,
                'matches_played': data['matches'],
                'wins': data['wins'],
                'draws': data['draws'],
                'losses': data['losses'],
                'goals_scored': data['goals_scored'],
                'goals_conceded': data['goals_conceded'],
                'goal_difference': data['goals_scored'] - data['goals_conceded'],
                'points': data['points'],
                'win_rate': round((data['wins'] / data['matches']) * 100, 1) if data['matches'] > 0 else 0,
                'goals_per_match': round(data['goals_scored'] / data['matches'], 2) if data['matches'] > 0 else 0,
                'goals_conceded_per_match': round(data['goals_conceded'] / data['matches'], 2) if data['matches'] > 0 else 0
            })
        
        return formatted_data
    
    def aggregate_formation_effectiveness(self, days=90):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        formations = Formation.objects.filter(is_active=True)
        formation_data = []
        
        for formation in formations:
            formation_matches = Match.objects.filter(
                lineups__formation=formation,
                lineups__is_starting_eleven=True,
                scheduled_datetime__gte=cutoff_date,
                status__in=['COMPLETED', 'FULL_TIME']
            ).distinct()
            
            if formation_matches.exists():
                wins = formation_matches.filter(result='WIN').count()
                draws = formation_matches.filter(result='DRAW').count()
                losses = formation_matches.filter(result='LOSS').count()
                total_matches = formation_matches.count()
                
                goals_scored = sum(match.chelsea_score for match in formation_matches)
                goals_conceded = sum(match.opponent_score for match in formation_matches)
                
                formation_data.append({
                    'formation_id': str(formation.id),
                    'formation_name': formation.name,
                    'matches_used': total_matches,
                    'wins': wins,
                    'draws': draws,
                    'losses': losses,
                    'win_rate': round((wins / total_matches) * 100, 1),
                    'goals_scored': goals_scored,
                    'goals_conceded': goals_conceded,
                    'goals_per_match': round(goals_scored / total_matches, 2),
                    'goals_conceded_per_match': round(goals_conceded / total_matches, 2),
                    'goal_difference': goals_scored - goals_conceded,
                    'points': (wins * 3) + draws,
                    'points_per_match': round(((wins * 3) + draws) / total_matches, 2),
                    'clean_sheets': formation_matches.filter(opponent_score=0).count(),
                    'high_scoring': formation_matches.filter(chelsea_score__gte=3).count()
                })
        
        return sorted(formation_data, key=lambda x: x['points_per_match'], reverse=True)
    
    def aggregate_opponent_analysis(self, days=365):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        opponents = Opponent.objects.filter(
            matches_against__scheduled_datetime__gte=cutoff_date,
            matches_against__status__in=['COMPLETED', 'FULL_TIME']
        ).distinct()
        
        opponent_data = []
        
        for opponent in opponents:
            opponent_matches = Match.objects.filter(
                opponent=opponent,
                scheduled_datetime__gte=cutoff_date,
                status__in=['COMPLETED', 'FULL_TIME']
            )
            
            if opponent_matches.exists():
                wins = opponent_matches.filter(result='WIN').count()
                draws = opponent_matches.filter(result='DRAW').count()
                losses = opponent_matches.filter(result='LOSS').count()
                total_matches = opponent_matches.count()
                
                goals_scored = sum(match.chelsea_score for match in opponent_matches)
                goals_conceded = sum(match.opponent_score for match in opponent_matches)
                
                recent_matches = opponent_matches.order_by('-scheduled_datetime')[:3]
                recent_form = [match.result for match in recent_matches]
                
                opponent_data.append({
                    'opponent_id': str(opponent.id),
                    'opponent_name': opponent.name,
                    'league': opponent.league,
                    'total_meetings': total_matches,
                    'chelsea_wins': wins,
                    'draws': draws,
                    'chelsea_losses': losses,
                    'chelsea_win_rate': round((wins / total_matches) * 100, 1),
                    'goals_scored_against': goals_scored,
                    'goals_conceded_to': goals_conceded,
                    'avg_goals_scored': round(goals_scored / total_matches, 2),
                    'avg_goals_conceded': round(goals_conceded / total_matches, 2),
                    'goal_difference': goals_scored - goals_conceded,
                    'recent_form': recent_form,
                    'difficulty_rating': self._calculate_difficulty_rating(wins, total_matches, goals_conceded, goals_scored),
                    'last_meeting': recent_matches.first().scheduled_datetime.strftime('%d/%m/%Y') if recent_matches else 'N/A'
                })
        
        return sorted(opponent_data, key=lambda x: x['difficulty_rating'], reverse=True)
    
    def aggregate_positional_performance(self, days=90):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        positions = Player.objects.filter(is_active=True).values_list('position', flat=True).distinct()
        positional_data = []
        
        for position in positions:
            position_players = Player.objects.filter(position=position, is_active=True)
            
            all_stats = PlayerStats.objects.filter(
                player__in=position_players,
                match__scheduled_datetime__gte=cutoff_date,
                match__status__in=['COMPLETED', 'FULL_TIME']
            )
            
            if all_stats.exists():
                position_summary = all_stats.aggregate(
                    total_matches=Count('id'),
                    total_goals=Sum('goals'),
                    total_assists=Sum('assists'),
                    avg_rating=Avg('rating'),
                    total_passes_completed=Sum('passes_completed'),
                    total_passes_attempted=Sum('passes_attempted'),
                    total_tackles=Sum('tackles'),
                    total_interceptions=Sum('interceptions'),
                    total_distance=Sum('distance_covered')
                )
                
                player_count = position_players.count()
                
                positional_data.append({
                    'position': position,
                    'player_count': player_count,
                    'total_matches': position_summary['total_matches'],
                    'avg_matches_per_player': round(position_summary['total_matches'] / player_count, 1),
                    'total_goals': position_summary['total_goals'] or 0,
                    'total_assists': position_summary['total_assists'] or 0,
                    'goals_per_match': round((position_summary['total_goals'] or 0) / position_summary['total_matches'], 3),
                    'assists_per_match': round((position_summary['total_assists'] or 0) / position_summary['total_matches'], 3),
                    'average_rating': round(position_summary['avg_rating'] or 0, 2),
                    'pass_accuracy': self._calculate_pass_accuracy(position_summary),
                    'defensive_actions_per_match': round(((position_summary['total_tackles'] or 0) + (position_summary['total_interceptions'] or 0)) / position_summary['total_matches'], 2),
                    'avg_distance_per_match': round((position_summary['total_distance'] or 0) / position_summary['total_matches'], 0),
                    'contribution_score': self._calculate_position_contribution_score(position_summary)
                })
        
        return sorted(positional_data, key=lambda x: x['average_rating'], reverse=True)
    
    def aggregate_match_type_performance(self, days=180):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        match_types = Match.objects.filter(
            scheduled_datetime__gte=cutoff_date,
            status__in=['COMPLETED', 'FULL_TIME']
        ).values_list('match_type', flat=True).distinct()
        
        match_type_data = []
        
        for match_type in match_types:
            type_matches = Match.objects.filter(
                match_type=match_type,
                scheduled_datetime__gte=cutoff_date,
                status__in=['COMPLETED', 'FULL_TIME']
            )
            
            if type_matches.exists():
                wins = type_matches.filter(result='WIN').count()
                draws = type_matches.filter(result='DRAW').count()
                losses = type_matches.filter(result='LOSS').count()
                total_matches = type_matches.count()
                
                goals_scored = sum(match.chelsea_score for match in type_matches)
                goals_conceded = sum(match.opponent_score for match in type_matches)
                
                avg_team_rating = self._calculate_avg_team_rating_for_matches(type_matches)
                
                match_type_data.append({
                    'match_type': match_type,
                    'competition_name': dict(Match.MATCH_TYPE_CHOICES).get(match_type, match_type),
                    'matches_played': total_matches,
                    'wins': wins,
                    'draws': draws,
                    'losses': losses,
                    'win_rate': round((wins / total_matches) * 100, 1),
                    'goals_scored': goals_scored,
                    'goals_conceded': goals_conceded,
                    'goals_per_match': round(goals_scored / total_matches, 2),
                    'goals_conceded_per_match': round(goals_conceded / total_matches, 2),
                    'goal_difference': goals_scored - goals_conceded,
                    'points': (wins * 3) + draws,
                    'average_team_rating': round(avg_team_rating, 2),
                    'clean_sheets': type_matches.filter(opponent_score=0).count(),
                    'failed_to_score': type_matches.filter(chelsea_score=0).count()
                })
        
        return sorted(match_type_data, key=lambda x: x['win_rate'], reverse=True)
    
    def aggregate_home_away_performance(self, days=180):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        home_away_data = []
        
        for is_home in [True, False]:
            venue_matches = Match.objects.filter(
                is_home=is_home,
                scheduled_datetime__gte=cutoff_date,
                status__in=['COMPLETED', 'FULL_TIME']
            )
            
            if venue_matches.exists():
                wins = venue_matches.filter(result='WIN').count()
                draws = venue_matches.filter(result='DRAW').count()
                losses = venue_matches.filter(result='LOSS').count()
                total_matches = venue_matches.count()
                
                goals_scored = sum(match.chelsea_score for match in venue_matches)
                goals_conceded = sum(match.opponent_score for match in venue_matches)
                
                home_away_data.append({
                    'venue': 'Home' if is_home else 'Away',
                    'matches_played': total_matches,
                    'wins': wins,
                    'draws': draws,
                    'losses': losses,
                    'win_rate': round((wins / total_matches) * 100, 1),
                    'goals_scored': goals_scored,
                    'goals_conceded': goals_conceded,
                    'goals_per_match': round(goals_scored / total_matches, 2),
                    'goals_conceded_per_match': round(goals_conceded / total_matches, 2),
                    'goal_difference': goals_scored - goals_conceded,
                    'points': (wins * 3) + draws,
                    'points_per_match': round(((wins * 3) + draws) / total_matches, 2),
                    'clean_sheets': venue_matches.filter(opponent_score=0).count(),
                    'clean_sheet_rate': round((venue_matches.filter(opponent_score=0).count() / total_matches) * 100, 1)
                })
        
        return home_away_data
    
    def aggregate_player_comparison_data(self, player_ids, days=90):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        players = Player.objects.filter(id__in=player_ids, is_active=True)
        comparison_data = []
        
        for player in players:
            player_stats = PlayerStats.objects.filter(
                player=player,
                match__scheduled_datetime__gte=cutoff_date,
                match__status__in=['COMPLETED', 'FULL_TIME']
            )
            
            if player_stats.exists():
                stats_summary = player_stats.aggregate(
                    matches_played=Count('id'),
                    total_minutes=Sum('minutes_played'),
                    total_goals=Sum('goals'),
                    total_assists=Sum('assists'),
                    avg_rating=Avg('rating'),
                    total_passes_completed=Sum('passes_completed'),
                    total_passes_attempted=Sum('passes_attempted'),
                    total_tackles=Sum('tackles'),
                    total_interceptions=Sum('interceptions'),
                    total_distance=Sum('distance_covered')
                )
                
                comparison_data.append({
                    'player_id': str(player.id),
                    'player_name': player.full_name,
                    'position': player.position,
                    'matches_played': stats_summary['matches_played'],
                    'minutes_per_match': round((stats_summary['total_minutes'] or 0) / stats_summary['matches_played'], 1),
                    'goals_per_match': round((stats_summary['total_goals'] or 0) / stats_summary['matches_played'], 2),
                    'assists_per_match': round((stats_summary['total_assists'] or 0) / stats_summary['matches_played'], 2),
                    'average_rating': round(stats_summary['avg_rating'] or 0, 2),
                    'pass_accuracy': self._calculate_pass_accuracy(stats_summary),
                    'defensive_actions_per_match': round(((stats_summary['total_tackles'] or 0) + (stats_summary['total_interceptions'] or 0)) / stats_summary['matches_played'], 2),
                    'distance_per_match': round((stats_summary['total_distance'] or 0) / stats_summary['matches_played'], 0),
                    'consistency_score': self._calculate_player_consistency(player_stats),
                    'form_trend': self._calculate_recent_form_trend(player_stats)
                })
        
        return comparison_data
    
    def aggregate_analytics_insights(self, days=30):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        analytics = Analytics.objects.filter(created_at__gte=cutoff_date)
        
        insights_by_type = defaultdict(list)
        confidence_levels = defaultdict(int)
        
        for analytic in analytics:
            insights_by_type[analytic.analysis_type].extend(analytic.insights)
            
            if analytic.confidence_score >= 90:
                confidence_levels['high'] += 1
            elif analytic.confidence_score >= 70:
                confidence_levels['medium'] += 1
            else:
                confidence_levels['low'] += 1
        
        return {
            'total_analytics': analytics.count(),
            'analytics_by_type': {
                analysis_type: {
                    'count': Analytics.objects.filter(
                        analysis_type=analysis_type,
                        created_at__gte=cutoff_date
                    ).count(),
                    'insights_count': len(insights)
                }
                for analysis_type, insights in insights_by_type.items()
            },
            'confidence_distribution': dict(confidence_levels),
            'avg_confidence': round(analytics.aggregate(avg=Avg('confidence_score'))['avg'] or 0, 1),
            'recent_insights': self._get_recent_key_insights(analytics)
        }
    
    def aggregate_performance_trends(self, days=90):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        matches = Match.objects.filter(
            scheduled_datetime__gte=cutoff_date,
            status__in=['COMPLETED', 'FULL_TIME']
        ).order_by('scheduled_datetime')
        
        if matches.count() < 5:
            raise InsufficientDataError("Insufficient matches for trend analysis")
        
        total_matches = matches.count()
        mid_point = total_matches // 2
        
        early_matches = matches[:mid_point]
        recent_matches = matches[mid_point:]
        
        early_performance = self._calculate_period_performance(early_matches)
        recent_performance = self._calculate_period_performance(recent_matches)
        
        return {
            'analysis_period': days,
            'total_matches': total_matches,
            'early_period': early_performance,
            'recent_period': recent_performance,
            'trends': {
                'win_rate_trend': recent_performance['win_rate'] - early_performance['win_rate'],
                'goals_trend': recent_performance['goals_per_match'] - early_performance['goals_per_match'],
                'defensive_trend': early_performance['goals_conceded_per_match'] - recent_performance['goals_conceded_per_match'],
                'overall_momentum': self._assess_momentum(recent_matches)
            }
        }
    
    def _calculate_pass_accuracy(self, stats_summary):
        completed = stats_summary.get('total_passes_completed', 0) or 0
        attempted = stats_summary.get('total_passes_attempted', 0) or 0
        
        if attempted == 0:
            return 0
        
        return round((completed / attempted) * 100, 1)
    
    def _calculate_difficulty_rating(self, chelsea_wins, total_matches, goals_conceded_to_opponent, goals_scored_against_opponent):
        win_rate = (chelsea_wins / total_matches) * 100
        goal_threat = (goals_conceded_to_opponent / total_matches) * 20
        defensive_solidity = 100 - ((goals_scored_against_opponent / total_matches) * 15)
        
        difficulty = 100 - win_rate + goal_threat - (defensive_solidity * 0.3)
        
        return round(max(0, min(100, difficulty)), 1)
    
    def _calculate_position_contribution_score(self, position_summary):
        goals_factor = (position_summary['total_goals'] or 0) * 3
        assists_factor = (position_summary['total_assists'] or 0) * 2
        rating_factor = (position_summary['avg_rating'] or 0) * 2
        
        contribution = goals_factor + assists_factor + rating_factor
        
        return round(contribution, 1)
    
    def _calculate_avg_team_rating_for_matches(self, matches):
        total_rating = 0
        match_count = 0
        
        for match in matches:
            match_avg = PlayerStats.objects.filter(match=match).aggregate(avg=Avg('rating'))['avg']
            if match_avg:
                total_rating += match_avg
                match_count += 1
        
        return total_rating / match_count if match_count > 0 else 0
    
    def _calculate_player_consistency(self, player_stats):
        ratings = [float(stat.rating) for stat in player_stats]
        
        if len(ratings) < 3:
            return 0
        
        mean_rating = sum(ratings) / len(ratings)
        variance = sum((r - mean_rating) ** 2 for r in ratings) / len(ratings)
        std_dev = variance ** 0.5
        
        consistency_score = max(0, 100 - (std_dev * 20))
        
        return round(consistency_score, 1)
    
    def _calculate_recent_form_trend(self, player_stats):
        recent_ratings = [float(stat.rating) for stat in player_stats.order_by('-match__scheduled_datetime')[:5]]
        
        if len(recent_ratings) < 3:
            return 'insufficient_data'
        
        recent_avg = sum(recent_ratings[:3]) / 3
        earlier_avg = sum(recent_ratings[-3:]) / len(recent_ratings[-3:])
        
        difference = recent_avg - earlier_avg
        
        if difference > 0.5:
            return 'improving'
        elif difference < -0.5:
            return 'declining'
        else:
            return 'stable'
    
    def _get_recent_key_insights(self, analytics):
        key_insights = []
        
        high_confidence_analytics = analytics.filter(confidence_score__gte=85).order_by('-created_at')[:5]
        
        for analytic in high_confidence_analytics:
            if analytic.insights:
                key_insights.extend(analytic.insights[:2])
        
        return key_insights[:10]
    
    def _calculate_period_performance(self, matches):
        total_matches = matches.count()
        
        if total_matches == 0:
            return {
                'matches': 0, 'wins': 0, 'win_rate': 0,
                'goals_scored': 0, 'goals_conceded': 0,
                'goals_per_match': 0, 'goals_conceded_per_match': 0
            }
        
        wins = matches.filter(result='WIN').count()
        goals_scored = sum(match.chelsea_score for match in matches)
        goals_conceded = sum(match.opponent_score for match in matches)
        
        return {
            'matches': total_matches,
            'wins': wins,
            'win_rate': round((wins / total_matches) * 100, 1),
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'goals_per_match': round(goals_scored / total_matches, 2),
            'goals_conceded_per_match': round(goals_conceded / total_matches, 2)
        }
    
    def _assess_momentum(self, recent_matches):
        results = [match.result for match in recent_matches.order_by('-scheduled_datetime')[:5]]
        
        wins = results.count('WIN')
        losses = results.count('LOSS')
        
        if wins >= 4:
            return 'very_positive'
        elif wins >= 3:
            return 'positive'
        elif losses >= 3:
            return 'concerning'
        elif losses >= 4:
            return 'very_concerning'
        else:
            return 'neutral'