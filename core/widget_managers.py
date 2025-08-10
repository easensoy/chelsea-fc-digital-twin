from django.db.models import Q, F, Sum, Avg, Count, Max, Min
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta, datetime
import json
import logging

from .models import Player, Match, PlayerStats, TeamStats, Formation, MatchLineup, MatchEvent, Analytics, Opponent
from .performance_tracker import PerformanceTracker
from .live_tracker import LiveTracker

logger = logging.getLogger('core.performance')

class WidgetManagers:
    
    def __init__(self):
        self.logger = logging.getLogger('core.performance')
        self.cache_timeout = 300  # 5 minutes
        
    def get_dashboard_widgets(self):
        widgets = {
            'overview_stats': self.get_overview_stats_widget(),
            'recent_matches': self.get_recent_matches_widget(),
            'top_performers': self.get_top_performers_widget(),
            'formation_summary': self.get_formation_summary_widget(),
            'live_match_status': self.get_live_match_widget(),
            'fitness_overview': self.get_fitness_overview_widget(),
            'upcoming_fixtures': self.get_upcoming_fixtures_widget(),
            'performance_alerts': self.get_performance_alerts_widget(),
            'tactical_insights': self.get_tactical_insights_widget(),
            'squad_availability': self.get_squad_availability_widget()
        }
        
        return {
            'widgets': widgets,
            'last_updated': timezone.now().isoformat(),
            'cache_status': 'live'
        }
    
    def get_overview_stats_widget(self):
        cache_key = 'widget_overview_stats'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        current_season_matches = self._get_current_season_matches()
        recent_matches = current_season_matches.filter(
            status__in=['COMPLETED', 'FULL_TIME']
        )
        
        total_matches = recent_matches.count()
        wins = recent_matches.filter(result='WIN').count()
        draws = recent_matches.filter(result='DRAW').count()
        losses = recent_matches.filter(result='LOSS').count()
        
        goals_scored = sum(match.chelsea_score for match in recent_matches)
        goals_conceded = sum(match.opponent_score for match in recent_matches)
        
        win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
        
        widget_data = {
            'title': 'Season Overview',
            'stats': {
                'matches_played': total_matches,
                'wins': wins,
                'draws': draws,
                'losses': losses,
                'win_rate': round(win_rate, 1),
                'goals_scored': goals_scored,
                'goals_conceded': goals_conceded,
                'goal_difference': goals_scored - goals_conceded,
                'points': (wins * 3) + draws,
                'goals_per_match': round(goals_scored / max(total_matches, 1), 2),
                'clean_sheets': recent_matches.filter(opponent_score=0).count()
            },
            'trends': {
                'form_last_5': self._get_recent_form(recent_matches, 5),
                'form_last_10': self._get_recent_form(recent_matches, 10)
            },
            'widget_type': 'stats_grid',
            'priority': 'high'
        }
        
        cache.set(cache_key, widget_data, self.cache_timeout)
        return widget_data
    
    def get_recent_matches_widget(self):
        cache_key = 'widget_recent_matches'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        recent_matches = Match.objects.filter(
            status__in=['COMPLETED', 'FULL_TIME']
        ).select_related('opponent').order_by('-scheduled_datetime')[:5]
        
        matches_data = []
        for match in recent_matches:
            match_data = {
                'id': str(match.id),
                'date': match.scheduled_datetime.strftime('%d/%m/%Y'),
                'opponent': match.opponent.name,
                'is_home': match.is_home,
                'score': f"{match.chelsea_score}-{match.opponent_score}",
                'result': match.result,
                'match_type': match.match_type,
                'venue': match.venue if not match.is_home else 'Stamford Bridge'
            }
            matches_data.append(match_data)
        
        widget_data = {
            'title': 'Recent Matches',
            'matches': matches_data,
            'widget_type': 'match_list',
            'priority': 'high'
        }
        
        cache.set(cache_key, widget_data, self.cache_timeout)
        return widget_data
    
    def get_top_performers_widget(self):
        cache_key = 'widget_top_performers'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        cutoff_date = timezone.now() - timedelta(days=30)
        
        top_performers = PlayerStats.objects.filter(
            match__scheduled_datetime__gte=cutoff_date,
            match__status__in=['COMPLETED', 'FULL_TIME']
        ).values('player__full_name', 'player__position', 'player__squad_number').annotate(
            avg_rating=Avg('rating'),
            total_goals=Sum('goals'),
            total_assists=Sum('assists'),
            matches_played=Count('match')
        ).filter(matches_played__gte=3).order_by('-avg_rating')[:5]
        
        performers_data = []
        for performer in top_performers:
            performer_data = {
                'name': performer['player__full_name'],
                'position': performer['player__position'],
                'squad_number': performer['player__squad_number'],
                'average_rating': round(performer['avg_rating'], 2),
                'goals': performer['total_goals'],
                'assists': performer['total_assists'],
                'matches_played': performer['matches_played'],
                'goal_contributions': performer['total_goals'] + performer['total_assists']
            }
            performers_data.append(performer_data)
        
        widget_data = {
            'title': 'Top Performers (Last 30 Days)',
            'performers': performers_data,
            'widget_type': 'performer_list',
            'priority': 'medium'
        }
        
        cache.set(cache_key, widget_data, self.cache_timeout)
        return widget_data
    
    def get_formation_summary_widget(self):
        cache_key = 'widget_formation_summary'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        recent_lineups = MatchLineup.objects.filter(
            match__scheduled_datetime__gte=timezone.now() - timedelta(days=60),
            match__status__in=['COMPLETED', 'FULL_TIME'],
            is_starting_eleven=True
        ).select_related('formation', 'match')
        
        formation_stats = {}
        for lineup in recent_lineups:
            formation_name = lineup.formation.name
            
            if formation_name not in formation_stats:
                formation_stats[formation_name] = {
                    'usage_count': 0,
                    'wins': 0,
                    'draws': 0,
                    'losses': 0,
                    'goals_scored': 0,
                    'goals_conceded': 0
                }
            
            stats = formation_stats[formation_name]
            stats['usage_count'] += 1
            stats['goals_scored'] += lineup.match.chelsea_score
            stats['goals_conceded'] += lineup.match.opponent_score
            
            if lineup.match.result == 'WIN':
                stats['wins'] += 1
            elif lineup.match.result == 'DRAW':
                stats['draws'] += 1
            else:
                stats['losses'] += 1
        
        # Calculate effectiveness for each formation
        for formation, stats in formation_stats.items():
            stats['win_rate'] = round((stats['wins'] / stats['usage_count']) * 100, 1)
            stats['avg_goals_scored'] = round(stats['goals_scored'] / stats['usage_count'], 2)
            stats['avg_goals_conceded'] = round(stats['goals_conceded'] / stats['usage_count'], 2)
            stats['goal_difference'] = stats['avg_goals_scored'] - stats['avg_goals_conceded']
        
        # Get most used and most effective formations
        most_used = max(formation_stats.items(), key=lambda x: x[1]['usage_count']) if formation_stats else None
        most_effective = max(formation_stats.items(), key=lambda x: x[1]['win_rate']) if formation_stats else None
        
        widget_data = {
            'title': 'Formation Analysis',
            'summary': {
                'total_formations_used': len(formation_stats),
                'most_used_formation': most_used[0] if most_used else 'None',
                'most_used_count': most_used[1]['usage_count'] if most_used else 0,
                'most_effective_formation': most_effective[0] if most_effective else 'None',
                'most_effective_win_rate': most_effective[1]['win_rate'] if most_effective else 0
            },
            'formations': formation_stats,
            'widget_type': 'formation_summary',
            'priority': 'medium'
        }
        
        cache.set(cache_key, widget_data, self.cache_timeout)
        return widget_data
    
    def get_live_match_widget(self):
        live_matches = Match.objects.filter(
            status__in=['LIVE', 'HALF_TIME']
        ).select_related('opponent')
        
        if not live_matches.exists():
            next_match = Match.objects.filter(
                status='SCHEDULED',
                scheduled_datetime__gt=timezone.now()
            ).select_related('opponent').order_by('scheduled_datetime').first()
            
            if next_match:
                widget_data = {
                    'title': 'Next Match',
                    'status': 'upcoming',
                    'match': {
                        'opponent': next_match.opponent.name,
                        'datetime': next_match.scheduled_datetime.isoformat(),
                        'venue': next_match.venue if not next_match.is_home else 'Stamford Bridge',
                        'is_home': next_match.is_home,
                        'match_type': next_match.match_type,
                        'hours_until_kickoff': self._calculate_hours_until_match(next_match)
                    },
                    'widget_type': 'next_match',
                    'priority': 'high'
                }
            else:
                widget_data = {
                    'title': 'Match Status',
                    'status': 'no_matches',
                    'message': 'No upcoming matches scheduled',
                    'widget_type': 'status_message',
                    'priority': 'low'
                }
            
            return widget_data
        
        live_match = live_matches.first()
        live_tracker = LiveTracker()
        live_data = live_tracker._get_live_match_data(live_match)
        
        widget_data = {
            'title': 'Live Match',
            'status': 'live',
            'match': {
                'opponent': live_match.opponent.name,
                'score': f"{live_match.chelsea_score}-{live_match.opponent_score}",
                'match_time': live_data['match_time'],
                'status': live_match.status,
                'venue': live_match.venue if not live_match.is_home else 'Stamford Bridge',
                'formation': live_data['formation']['formation_name'],
                'recent_events': live_data['recent_events'][:3]
            },
            'widget_type': 'live_match',
            'priority': 'critical'
        }
        
        return widget_data
    
    def get_fitness_overview_widget(self):
        cache_key = 'widget_fitness_overview'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        active_players = Player.objects.filter(is_active=True)
        
        fitness_categories = {
            'excellent': 0,  # 90-100
            'good': 0,       # 80-89
            'average': 0,    # 70-79
            'poor': 0,       # 60-69
            'critical': 0    # <60
        }
        
        injured_players = []
        low_fitness_players = []
        
        for player in active_players:
            fitness = player.fitness_level
            
            if player.is_injured:
                injured_players.append({
                    'name': player.full_name,
                    'position': player.position,
                    'squad_number': player.squad_number
                })
            elif fitness < 70:
                low_fitness_players.append({
                    'name': player.full_name,
                    'position': player.position,
                    'fitness_level': fitness
                })
            
            if fitness >= 90:
                fitness_categories['excellent'] += 1
            elif fitness >= 80:
                fitness_categories['good'] += 1
            elif fitness >= 70:
                fitness_categories['average'] += 1
            elif fitness >= 60:
                fitness_categories['poor'] += 1
            else:
                fitness_categories['critical'] += 1
        
        total_players = active_players.count()
        available_players = total_players - len(injured_players)
        
        widget_data = {
            'title': 'Squad Fitness Overview',
            'summary': {
                'total_players': total_players,
                'available_players': available_players,
                'injured_players': len(injured_players),
                'availability_percentage': round((available_players / total_players) * 100, 1) if total_players > 0 else 0
            },
            'fitness_distribution': fitness_categories,
            'alerts': {
                'injured_players': injured_players,
                'low_fitness_players': low_fitness_players[:5]
            },
            'widget_type': 'fitness_overview',
            'priority': 'medium'
        }
        
        cache.set(cache_key, widget_data, self.cache_timeout)
        return widget_data
    
    def get_upcoming_fixtures_widget(self):
        cache_key = 'widget_upcoming_fixtures'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        upcoming_matches = Match.objects.filter(
            status='SCHEDULED',
            scheduled_datetime__gt=timezone.now()
        ).select_related('opponent').order_by('scheduled_datetime')[:5]
        
        fixtures_data = []
        for match in upcoming_matches:
            fixture_data = {
                'id': str(match.id),
                'opponent': match.opponent.name,
                'date': match.scheduled_datetime.strftime('%d/%m/%Y'),
                'time': match.scheduled_datetime.strftime('%H:%M'),
                'venue': match.venue if not match.is_home else 'Stamford Bridge',
                'is_home': match.is_home,
                'match_type': match.match_type,
                'days_until': (match.scheduled_datetime.date() - timezone.now().date()).days,
                'opponent_info': {
                    'league': match.opponent.league,
                    'typical_formation': match.opponent.typical_formation
                }
            }
            fixtures_data.append(fixture_data)
        
        widget_data = {
            'title': 'Upcoming Fixtures',
            'fixtures': fixtures_data,
            'widget_type': 'fixture_list',
            'priority': 'medium'
        }
        
        cache.set(cache_key, widget_data, self.cache_timeout)
        return widget_data
    
    def get_performance_alerts_widget(self):
        alerts = []
        
        # Check for players with declining performance
        recent_poor_performers = PlayerStats.objects.filter(
            match__scheduled_datetime__gte=timezone.now() - timedelta(days=14),
            match__status__in=['COMPLETED', 'FULL_TIME'],
            rating__lt=6.0
        ).values('player__full_name', 'player__position').annotate(
            avg_rating=Avg('rating'),
            match_count=Count('match')
        ).filter(match_count__gte=2)
        
        for performer in recent_poor_performers:
            alerts.append({
                'type': 'performance_concern',
                'priority': 'medium',
                'message': f"{performer['player__full_name']} has averaged {performer['avg_rating']:.1f} rating in recent matches",
                'player': performer['player__full_name'],
                'position': performer['player__position']
            })
        
        # Check for injury concerns
        injured_players = Player.objects.filter(is_active=True, is_injured=True)
        for player in injured_players:
            alerts.append({
                'type': 'injury',
                'priority': 'high',
                'message': f"{player.full_name} is currently injured",
                'player': player.full_name,
                'position': player.position
            })
        
        # Check for fitness concerns
        low_fitness_players = Player.objects.filter(
            is_active=True, 
            is_injured=False, 
            fitness_level__lt=70
        )
        for player in low_fitness_players:
            alerts.append({
                'type': 'fitness_concern',
                'priority': 'medium',
                'message': f"{player.full_name} has low fitness level ({player.fitness_level}%)",
                'player': player.full_name,
                'position': player.position
            })
        
        # Check for formation effectiveness concerns
        recent_formation_performance = self._check_formation_performance()
        if recent_formation_performance:
            alerts.extend(recent_formation_performance)
        
        widget_data = {
            'title': 'Performance Alerts',
            'alerts': alerts[:10],  # Limit to 10 most important alerts
            'total_alerts': len(alerts),
            'widget_type': 'alert_list',
            'priority': 'high' if alerts else 'low'
        }
        
        return widget_data
    
    def get_tactical_insights_widget(self):
        cache_key = 'widget_tactical_insights'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        insights = []
        
        # Analyze recent match patterns
        recent_matches = Match.objects.filter(
            scheduled_datetime__gte=timezone.now() - timedelta(days=30),
            status__in=['COMPLETED', 'FULL_TIME']
        )
        
        if recent_matches.count() >= 3:
            home_performance = recent_matches.filter(is_home=True)
            away_performance = recent_matches.filter(is_home=False)
            
            if home_performance.exists() and away_performance.exists():
                home_win_rate = (home_performance.filter(result='WIN').count() / home_performance.count()) * 100
                away_win_rate = (away_performance.filter(result='WIN').count() / away_performance.count()) * 100
                
                if abs(home_win_rate - away_win_rate) > 25:
                    insights.append({
                        'category': 'Home/Away Performance',
                        'insight': f"Significant difference in home ({home_win_rate:.0f}%) vs away ({away_win_rate:.0f}%) performance",
                        'type': 'pattern_analysis'
                    })
            
            # Analyze goal patterns
            total_goals = sum(match.chelsea_score for match in recent_matches)
            avg_goals_per_match = total_goals / recent_matches.count()
            
            if avg_goals_per_match < 1.2:
                insights.append({
                    'category': 'Attacking Performance',
                    'insight': f"Low scoring rate: averaging {avg_goals_per_match:.1f} goals per match",
                    'type': 'performance_concern'
                })
            elif avg_goals_per_match > 2.5:
                insights.append({
                    'category': 'Attacking Performance',
                    'insight': f"Excellent scoring form: averaging {avg_goals_per_match:.1f} goals per match",
                    'type': 'positive_trend'
                })
        
        # Formation insights
        formation_insights = self._generate_formation_insights()
        insights.extend(formation_insights)
        
        widget_data = {
            'title': 'Tactical Insights',
            'insights': insights[:5],  # Show top 5 insights
            'widget_type': 'insight_list',
            'priority': 'medium'
        }
        
        cache.set(cache_key, widget_data, self.cache_timeout)
        return widget_data
    
    def get_squad_availability_widget(self):
        cache_key = 'widget_squad_availability'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        all_players = Player.objects.filter(is_active=True)
        
        position_availability = {}
        for position in ['GK', 'CB', 'LB', 'RB', 'CDM', 'CM', 'CAM', 'LM', 'RM', 'LW', 'RW', 'ST']:
            position_players = all_players.filter(position=position)
            available_players = position_players.filter(is_injured=False, fitness_level__gte=70)
            
            position_availability[position] = {
                'total': position_players.count(),
                'available': available_players.count(),
                'injured': position_players.filter(is_injured=True).count(),
                'low_fitness': position_players.filter(is_injured=False, fitness_level__lt=70).count(),
                'availability_percentage': round((available_players.count() / max(position_players.count(), 1)) * 100, 1)
            }
        
        # Identify positions with concerns
        position_concerns = []
        for position, data in position_availability.items():
            if data['available'] <= 1:
                position_concerns.append({
                    'position': position,
                    'concern_level': 'high',
                    'message': f"Only {data['available']} available player(s) in {position}"
                })
            elif data['availability_percentage'] < 70:
                position_concerns.append({
                    'position': position,
                    'concern_level': 'medium',
                    'message': f"Low availability in {position}: {data['availability_percentage']}%"
                })
        
        widget_data = {
            'title': 'Squad Availability by Position',
            'position_availability': position_availability,
            'concerns': position_concerns,
            'overall_availability': round(
                sum(data['available'] for data in position_availability.values()) / 
                max(sum(data['total'] for data in position_availability.values()), 1) * 100, 1
            ),
            'widget_type': 'availability_grid',
            'priority': 'medium'
        }
        
        cache.set(cache_key, widget_data, self.cache_timeout)
        return widget_data
    
    def get_all_widgets(self):
        return self.get_dashboard_widgets()
    
    def _get_current_season_matches(self):
        current_date = timezone.now().date()
        
        if current_date.month >= 7:
            season_start = current_date.replace(month=7, day=1)
            season_end = current_date.replace(year=current_date.year + 1, month=6, day=30)
        else:
            season_start = current_date.replace(year=current_date.year - 1, month=7, day=1)
            season_end = current_date.replace(month=6, day=30)
        
        return Match.objects.filter(
            scheduled_datetime__date__range=[season_start, season_end]
        )
    
    def _get_recent_form(self, matches, num_matches):
        recent_matches = matches.order_by('-scheduled_datetime')[:num_matches]
        
        form_string = ''
        for match in reversed(recent_matches):
            if match.result == 'WIN':
                form_string += 'W'
            elif match.result == 'DRAW':
                form_string += 'D'
            else:
                form_string += 'L'
        
        return form_string
    
    def _calculate_hours_until_match(self, match):
        time_diff = match.scheduled_datetime - timezone.now()
        return round(time_diff.total_seconds() / 3600, 1)
    
    def _check_formation_performance(self):
        alerts = []
        
        recent_lineups = MatchLineup.objects.filter(
            match__scheduled_datetime__gte=timezone.now() - timedelta(days=21),
            match__status__in=['COMPLETED', 'FULL_TIME'],
            is_starting_eleven=True
        ).select_related('formation', 'match')
        
        formation_performance = {}
        for lineup in recent_lineups:
            formation_name = lineup.formation.name
            
            if formation_name not in formation_performance:
                formation_performance[formation_name] = {'matches': 0, 'wins': 0}
            
            formation_performance[formation_name]['matches'] += 1
            if lineup.match.result == 'WIN':
                formation_performance[formation_name]['wins'] += 1
        
        for formation, performance in formation_performance.items():
            if performance['matches'] >= 3:
                win_rate = (performance['wins'] / performance['matches']) * 100
                if win_rate < 30:
                    alerts.append({
                        'type': 'formation_concern',
                        'priority': 'medium',
                        'message': f"Formation {formation} has poor recent performance ({win_rate:.0f}% win rate)",
                        'formation': formation
                    })
        
        return alerts
    
    def _generate_formation_insights(self):
        insights = []
        
        recent_lineups = MatchLineup.objects.filter(
            match__scheduled_datetime__gte=timezone.now() - timedelta(days=45),
            match__status__in=['COMPLETED', 'FULL_TIME'],
            is_starting_eleven=True
        ).select_related('formation', 'match')
        
        if recent_lineups.count() >= 5:
            formation_usage = {}
            for lineup in recent_lineups:
                formation_name = lineup.formation.name
                formation_usage[formation_name] = formation_usage.get(formation_name, 0) + 1
            
            most_used_formation = max(formation_usage, key=formation_usage.get)
            usage_percentage = (formation_usage[most_used_formation] / recent_lineups.count()) * 100
            
            if usage_percentage > 70:
                insights.append({
                    'category': 'Formation Usage',
                    'insight': f"Heavy reliance on {most_used_formation} formation ({usage_percentage:.0f}% of recent matches)",
                    'type': 'tactical_pattern'
                })
            elif len(formation_usage) >= 4:
                insights.append({
                    'category': 'Formation Usage',
                    'insight': f"Good tactical variety with {len(formation_usage)} different formations used recently",
                    'type': 'positive_trend'
                })
        
        return insights
    
    def refresh_widget_cache(self, widget_name=None):
        if widget_name:
            cache_key = f'widget_{widget_name}'
            cache.delete(cache_key)
            self.logger.info(f"Cache cleared for widget: {widget_name}")
        else:
            # Clear all widget caches
            widget_cache_keys = [
                'widget_overview_stats',
                'widget_recent_matches',
                'widget_top_performers',
                'widget_formation_summary',
                'widget_fitness_overview',
                'widget_upcoming_fixtures',
                'widget_tactical_insights',
                'widget_squad_availability'
            ]
            
            for key in widget_cache_keys:
                cache.delete(key)
            
            self.logger.info("All widget caches cleared")
        
        return {'success': True, 'message': 'Widget cache refreshed'}