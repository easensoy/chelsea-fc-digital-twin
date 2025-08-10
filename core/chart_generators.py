from django.db.models import Q, F, Sum, Avg, Count, Max, Min
from django.utils import timezone
from datetime import timedelta, datetime
import json
import logging
from collections import defaultdict, OrderedDict

from .models import Player, Match, PlayerStats, TeamStats, Formation, MatchLineup, MatchEvent, Opponent

logger = logging.getLogger('core.performance')

class ChartGenerators:
    
    def __init__(self):
        self.logger = logging.getLogger('core.performance')
        self.default_colors = {
            'primary': '#1f4e79',
            'secondary': '#3d85c6',
            'success': '#34a853',
            'warning': '#fbbc04',
            'danger': '#ea4335',
            'info': '#4285f4',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }
        
    def generate_dashboard_charts(self):
        charts_data = {
            'performance_overview': self.generate_performance_overview_chart(),
            'formation_effectiveness': self.generate_formation_effectiveness_chart(),
            'player_ratings_trend': self.generate_player_ratings_trend_chart(),
            'match_results_timeline': self.generate_match_results_timeline_chart(),
            'position_analysis': self.generate_position_analysis_chart(),
            'goals_assists_comparison': self.generate_goals_assists_chart(),
            'possession_vs_results': self.generate_possession_results_chart(),
            'player_fitness_status': self.generate_fitness_status_chart(),
            'monthly_performance': self.generate_monthly_performance_chart(),
            'tactical_heat_map': self.generate_tactical_heat_map_chart()
        }
        
        return {
            'charts': charts_data,
            'generated_at': timezone.now().isoformat(),
            'total_charts': len(charts_data)
        }
    
    def generate_performance_overview_chart(self, days=30):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        recent_matches = Match.objects.filter(
            scheduled_datetime__date__range=[start_date, end_date],
            status__in=['COMPLETED', 'FULL_TIME']
        ).order_by('scheduled_datetime')
        
        chart_data = {
            'labels': [],
            'datasets': [
                {
                    'label': 'Goals Scored',
                    'data': [],
                    'backgroundColor': self.default_colors['success'],
                    'borderColor': self.default_colors['success'],
                    'tension': 0.4
                },
                {
                    'label': 'Goals Conceded',
                    'data': [],
                    'backgroundColor': self.default_colors['danger'],
                    'borderColor': self.default_colors['danger'],
                    'tension': 0.4
                }
            ]
        }
        
        for match in recent_matches:
            chart_data['labels'].append(f"vs {match.opponent.name}")
            chart_data['datasets'][0]['data'].append(match.chelsea_score)
            chart_data['datasets'][1]['data'].append(match.opponent_score)
        
        return {
            'type': 'line',
            'data': chart_data,
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'Goals Scored vs Conceded (Last {days} Days)'
                    },
                    'legend': {
                        'position': 'top'
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Goals'
                        }
                    }
                }
            }
        }
    
    def generate_formation_effectiveness_chart(self):
        formations = Formation.objects.filter(is_active=True)
        
        formation_data = []
        formation_labels = []
        
        for formation in formations:
            recent_matches = self._get_formation_recent_matches(formation, days=90)
            
            if recent_matches:
                wins = sum(1 for match in recent_matches if match.result == 'WIN')
                win_rate = (wins / len(recent_matches)) * 100
                
                formation_data.append(round(win_rate, 1))
                formation_labels.append(formation.name)
        
        chart_data = {
            'labels': formation_labels,
            'datasets': [{
                'label': 'Win Rate %',
                'data': formation_data,
                'backgroundColor': [
                    self.default_colors['primary'],
                    self.default_colors['secondary'],
                    self.default_colors['success'],
                    self.default_colors['info'],
                    self.default_colors['warning'],
                    self.default_colors['danger']
                ][:len(formation_data)]
            }]
        }
        
        return {
            'type': 'doughnut',
            'data': chart_data,
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Formation Effectiveness (Win Rate %)'
                    },
                    'legend': {
                        'position': 'bottom'
                    }
                }
            }
        }
    
    def generate_player_ratings_trend_chart(self, player_limit=5):
        top_players = self._get_top_performers_recent(limit=player_limit)
        
        chart_data = {
            'labels': [],
            'datasets': []
        }
        
        colors = [
            self.default_colors['primary'],
            self.default_colors['secondary'],
            self.default_colors['success'],
            self.default_colors['warning'],
            self.default_colors['info']
        ]
        
        if top_players:
            recent_matches = Match.objects.filter(
                scheduled_datetime__gte=timezone.now() - timedelta(days=60),
                status__in=['COMPLETED', 'FULL_TIME']
            ).order_by('scheduled_datetime')
            
            chart_data['labels'] = [match.scheduled_datetime.strftime('%d/%m') for match in recent_matches]
            
            for idx, player in enumerate(top_players):
                player_ratings = []
                
                for match in recent_matches:
                    try:
                        stats = PlayerStats.objects.get(player=player, match=match)
                        player_ratings.append(float(stats.rating))
                    except PlayerStats.DoesNotExist:
                        player_ratings.append(None)
                
                chart_data['datasets'].append({
                    'label': player.full_name,
                    'data': player_ratings,
                    'borderColor': colors[idx % len(colors)],
                    'backgroundColor': colors[idx % len(colors)] + '20',
                    'tension': 0.4,
                    'fill': False
                })
        
        return {
            'type': 'line',
            'data': chart_data,
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Top Players Performance Trends'
                    },
                    'legend': {
                        'position': 'top'
                    }
                },
                'scales': {
                    'y': {
                        'min': 5,
                        'max': 10,
                        'title': {
                            'display': True,
                            'text': 'Player Rating'
                        }
                    }
                },
                'elements': {
                    'point': {
                        'radius': 3
                    }
                }
            }
        }
    
    def generate_match_results_timeline_chart(self, days=90):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        matches = Match.objects.filter(
            scheduled_datetime__date__range=[start_date, end_date],
            status__in=['COMPLETED', 'FULL_TIME']
        ).order_by('scheduled_datetime')
        
        results_data = []
        background_colors = []
        
        for match in matches:
            if match.result == 'WIN':
                results_data.append(3)
                background_colors.append(self.default_colors['success'])
            elif match.result == 'DRAW':
                results_data.append(1)
                background_colors.append(self.default_colors['warning'])
            else:
                results_data.append(0)
                background_colors.append(self.default_colors['danger'])
        
        chart_data = {
            'labels': [f"vs {match.opponent.name}" for match in matches],
            'datasets': [{
                'label': 'Match Results',
                'data': results_data,
                'backgroundColor': background_colors,
                'borderWidth': 1
            }]
        }
        
        return {
            'type': 'bar',
            'data': chart_data,
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Match Results Timeline'
                    },
                    'legend': {
                        'display': False
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'max': 3,
                        'ticks': {
                            'stepSize': 1,
                            'callback': 'function(value) { return value === 3 ? "Win" : value === 1 ? "Draw" : "Loss"; }'
                        },
                        'title': {
                            'display': True,
                            'text': 'Result'
                        }
                    },
                    'x': {
                        'title': {
                            'display': True,
                            'text': 'Matches'
                        }
                    }
                }
            }
        }
    
    def generate_position_analysis_chart(self):
        position_stats = PlayerStats.objects.filter(
            match__scheduled_datetime__gte=timezone.now() - timedelta(days=60),
            match__status__in=['COMPLETED', 'FULL_TIME']
        ).select_related('player')
        
        position_data = defaultdict(lambda: {'count': 0, 'total_rating': 0, 'goals': 0, 'assists': 0})
        
        for stats in position_stats:
            position = stats.player.position
            position_data[position]['count'] += 1
            position_data[position]['total_rating'] += float(stats.rating)
            position_data[position]['goals'] += stats.goals
            position_data[position]['assists'] += stats.assists
        
        chart_data = {
            'labels': list(position_data.keys()),
            'datasets': [
                {
                    'label': 'Average Rating',
                    'data': [
                        round(data['total_rating'] / data['count'], 2) if data['count'] > 0 else 0
                        for data in position_data.values()
                    ],
                    'backgroundColor': self.default_colors['primary'],
                    'yAxisID': 'y'
                },
                {
                    'label': 'Goal Contributions',
                    'data': [data['goals'] + data['assists'] for data in position_data.values()],
                    'backgroundColor': self.default_colors['success'],
                    'yAxisID': 'y1'
                }
            ]
        }
        
        return {
            'type': 'bar',
            'data': chart_data,
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Performance Analysis by Position'
                    }
                },
                'scales': {
                    'y': {
                        'type': 'linear',
                        'display': True,
                        'position': 'left',
                        'title': {
                            'display': True,
                            'text': 'Average Rating'
                        }
                    },
                    'y1': {
                        'type': 'linear',
                        'display': True,
                        'position': 'right',
                        'title': {
                            'display': True,
                            'text': 'Goal Contributions'
                        },
                        'grid': {
                            'drawOnChartArea': False
                        }
                    }
                }
            }
        }
    
    def generate_goals_assists_chart(self, player_limit=10):
        recent_stats = PlayerStats.objects.filter(
            match__scheduled_datetime__gte=timezone.now() - timedelta(days=60),
            match__status__in=['COMPLETED', 'FULL_TIME']
        ).values('player__full_name').annotate(
            total_goals=Sum('goals'),
            total_assists=Sum('assists')
        ).order_by('-total_goals', '-total_assists')[:player_limit]
        
        player_names = [stats['player__full_name'] for stats in recent_stats]
        goals_data = [stats['total_goals'] for stats in recent_stats]
        assists_data = [stats['total_assists'] for stats in recent_stats]
        
        chart_data = {
            'labels': player_names,
            'datasets': [
                {
                    'label': 'Goals',
                    'data': goals_data,
                    'backgroundColor': self.default_colors['success']
                },
                {
                    'label': 'Assists',
                    'data': assists_data,
                    'backgroundColor': self.default_colors['info']
                }
            ]
        }
        
        return {
            'type': 'bar',
            'data': chart_data,
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Goals and Assists (Last 60 Days)'
                    }
                },
                'scales': {
                    'x': {
                        'stacked': True
                    },
                    'y': {
                        'stacked': True,
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Count'
                        }
                    }
                }
            }
        }
    
    def generate_possession_results_chart(self):
        matches_with_stats = Match.objects.filter(
            scheduled_datetime__gte=timezone.now() - timedelta(days=120),
            status__in=['COMPLETED', 'FULL_TIME'],
            team_stats__isnull=False
        ).select_related('team_stats')
        
        possession_data = []
        result_colors = []
        labels = []
        
        for match in matches_with_stats:
            possession_data.append(float(match.team_stats.possession_percentage))
            labels.append(f"vs {match.opponent.name}")
            
            if match.result == 'WIN':
                result_colors.append(self.default_colors['success'])
            elif match.result == 'DRAW':
                result_colors.append(self.default_colors['warning'])
            else:
                result_colors.append(self.default_colors['danger'])
        
        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': 'Possession %',
                'data': possession_data,
                'backgroundColor': result_colors,
                'borderColor': self.default_colors['primary'],
                'borderWidth': 1
            }]
        }
        
        return {
            'type': 'scatter',
            'data': {
                'datasets': [{
                    'label': 'Possession vs Results',
                    'data': [
                        {'x': possession, 'y': 3 if match.result == 'WIN' else 1 if match.result == 'DRAW' else 0}
                        for possession, match in zip(possession_data, matches_with_stats)
                    ],
                    'backgroundColor': result_colors,
                    'borderColor': self.default_colors['primary']
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Possession % vs Match Results'
                    }
                },
                'scales': {
                    'x': {
                        'title': {
                            'display': True,
                            'text': 'Possession %'
                        },
                        'min': 30,
                        'max': 80
                    },
                    'y': {
                        'title': {
                            'display': True,
                            'text': 'Result'
                        },
                        'min': -0.5,
                        'max': 3.5,
                        'ticks': {
                            'stepSize': 1,
                            'callback': 'function(value) { return value === 3 ? "Win" : value === 1 ? "Draw" : value === 0 ? "Loss" : ""; }'
                        }
                    }
                }
            }
        }
    
    def generate_fitness_status_chart(self):
        active_players = Player.objects.filter(is_active=True)
        
        fitness_ranges = {
            'Excellent (90-100)': 0,
            'Good (80-89)': 0,
            'Average (70-79)': 0,
            'Poor (60-69)': 0,
            'Critical (<60)': 0
        }
        
        for player in active_players:
            fitness = player.fitness_level
            
            if fitness >= 90:
                fitness_ranges['Excellent (90-100)'] += 1
            elif fitness >= 80:
                fitness_ranges['Good (80-89)'] += 1
            elif fitness >= 70:
                fitness_ranges['Average (70-79)'] += 1
            elif fitness >= 60:
                fitness_ranges['Poor (60-69)'] += 1
            else:
                fitness_ranges['Critical (<60)'] += 1
        
        chart_data = {
            'labels': list(fitness_ranges.keys()),
            'datasets': [{
                'data': list(fitness_ranges.values()),
                'backgroundColor': [
                    self.default_colors['success'],
                    self.default_colors['info'],
                    self.default_colors['warning'],
                    self.default_colors['danger'],
                    '#8B0000'
                ]
            }]
        }
        
        return {
            'type': 'pie',
            'data': chart_data,
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Squad Fitness Status Distribution'
                    },
                    'legend': {
                        'position': 'bottom'
                    }
                }
            }
        }
    
    def generate_monthly_performance_chart(self, months=6):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=months * 30)
        
        monthly_data = defaultdict(lambda: {'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0})
        
        matches = Match.objects.filter(
            scheduled_datetime__date__range=[start_date, end_date],
            status__in=['COMPLETED', 'FULL_TIME']
        )
        
        for match in matches:
            month_key = match.scheduled_datetime.strftime('%Y-%m')
            
            if match.result == 'WIN':
                monthly_data[month_key]['wins'] += 1
            elif match.result == 'DRAW':
                monthly_data[month_key]['draws'] += 1
            else:
                monthly_data[month_key]['losses'] += 1
            
            monthly_data[month_key]['goals_for'] += match.chelsea_score
            monthly_data[month_key]['goals_against'] += match.opponent_score
        
        sorted_months = sorted(monthly_data.keys())
        
        chart_data = {
            'labels': [datetime.strptime(month, '%Y-%m').strftime('%b %Y') for month in sorted_months],
            'datasets': [
                {
                    'label': 'Wins',
                    'data': [monthly_data[month]['wins'] for month in sorted_months],
                    'backgroundColor': self.default_colors['success']
                },
                {
                    'label': 'Draws',
                    'data': [monthly_data[month]['draws'] for month in sorted_months],
                    'backgroundColor': self.default_colors['warning']
                },
                {
                    'label': 'Losses',
                    'data': [monthly_data[month]['losses'] for month in sorted_months],
                    'backgroundColor': self.default_colors['danger']
                }
            ]
        }
        
        return {
            'type': 'bar',
            'data': chart_data,
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Monthly Performance Overview'
                    }
                },
                'scales': {
                    'x': {
                        'stacked': True
                    },
                    'y': {
                        'stacked': True,
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Matches'
                        }
                    }
                }
            }
        }
    
    def generate_tactical_heat_map_chart(self):
        formation_usage = MatchLineup.objects.filter(
            match__scheduled_datetime__gte=timezone.now() - timedelta(days=90),
            match__status__in=['COMPLETED', 'FULL_TIME'],
            is_starting_eleven=True
        ).values('formation__name').annotate(
            usage_count=Count('id'),
            avg_goals_scored=Avg('match__chelsea_score'),
            avg_goals_conceded=Avg('match__opponent_score')
        )
        
        heat_map_data = []
        
        for usage in formation_usage:
            formation_name = usage['formation__name']
            usage_count = usage['usage_count']
            effectiveness = (usage['avg_goals_scored'] or 0) - (usage['avg_goals_conceded'] or 0)
            
            heat_map_data.append({
                'x': formation_name,
                'y': 'Usage Frequency',
                'v': usage_count
            })
            
            heat_map_data.append({
                'x': formation_name,
                'y': 'Goal Difference',
                'v': round(effectiveness, 2)
            })
        
        return {
            'type': 'matrix',
            'data': {
                'datasets': [{
                    'label': 'Formation Analysis',
                    'data': heat_map_data,
                    'backgroundColor': 'function(context) { return context.parsed.v > 0 ? "rgba(52, 168, 83, 0.8)" : "rgba(234, 67, 53, 0.8)"; }',
                    'borderColor': 'rgba(255, 255, 255, 0.1)',
                    'borderWidth': 1,
                    'width': '{c}',
                    'height': '{c}'
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Formation Usage and Effectiveness Heat Map'
                    },
                    'legend': {
                        'display': False
                    }
                },
                'scales': {
                    'x': {
                        'type': 'category',
                        'position': 'bottom',
                        'title': {
                            'display': True,
                            'text': 'Formation'
                        }
                    },
                    'y': {
                        'type': 'category',
                        'title': {
                            'display': True,
                            'text': 'Metric'
                        }
                    }
                }
            }
        }
    
    def _get_formation_recent_matches(self, formation, days=90):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        lineups = MatchLineup.objects.filter(
            formation=formation,
            match__status__in=['COMPLETED', 'FULL_TIME'],
            match__scheduled_datetime__gte=cutoff_date,
            is_starting_eleven=True
        ).select_related('match')
        
        return [lineup.match for lineup in lineups]
    
    def _get_top_performers_recent(self, limit=5, days=60):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        top_performers = PlayerStats.objects.filter(
            match__scheduled_datetime__gte=cutoff_date,
            match__status__in=['COMPLETED', 'FULL_TIME']
        ).values('player').annotate(
            avg_rating=Avg('rating'),
            matches_played=Count('match')
        ).filter(
            matches_played__gte=3
        ).order_by('-avg_rating')[:limit]
        
        player_ids = [performer['player'] for performer in top_performers]
        return Player.objects.filter(id__in=player_ids)
    
    def generate_custom_chart(self, chart_config):
        chart_type = chart_config.get('type', 'line')
        data_source = chart_config.get('data_source', 'player_stats')
        filters = chart_config.get('filters', {})
        
        if data_source == 'player_stats':
            return self._generate_player_stats_chart(chart_type, filters)
        elif data_source == 'match_results':
            return self._generate_match_results_chart(chart_type, filters)
        elif data_source == 'formations':
            return self._generate_formation_chart(chart_type, filters)
        else:
            return {'error': 'Unsupported data source'}
    
    def _generate_player_stats_chart(self, chart_type, filters):
        stats_query = PlayerStats.objects.all()
        
        if 'player_id' in filters:
            stats_query = stats_query.filter(player_id=filters['player_id'])
        
        if 'date_range' in filters:
            start_date = datetime.fromisoformat(filters['date_range']['start'])
            end_date = datetime.fromisoformat(filters['date_range']['end'])
            stats_query = stats_query.filter(
                match__scheduled_datetime__date__range=[start_date.date(), end_date.date()]
            )
        
        stats_data = list(stats_query.values(
            'match__scheduled_datetime',
            'player__full_name',
            'rating',
            'goals',
            'assists'
        ).order_by('match__scheduled_datetime'))
        
        return {
            'type': chart_type,
            'data': stats_data,
            'generated_at': timezone.now().isoformat()
        }
    
    def _generate_match_results_chart(self, chart_type, filters):
        matches_query = Match.objects.filter(status__in=['COMPLETED', 'FULL_TIME'])
        
        if 'match_type' in filters:
            matches_query = matches_query.filter(match_type=filters['match_type'])
        
        if 'date_range' in filters:
            start_date = datetime.fromisoformat(filters['date_range']['start'])
            end_date = datetime.fromisoformat(filters['date_range']['end'])
            matches_query = matches_query.filter(
                scheduled_datetime__date__range=[start_date.date(), end_date.date()]
            )
        
        matches_data = list(matches_query.values(
            'scheduled_datetime',
            'opponent__name',
            'chelsea_score',
            'opponent_score',
            'result'
        ).order_by('scheduled_datetime'))
        
        return {
            'type': chart_type,
            'data': matches_data,
            'generated_at': timezone.now().isoformat()
        }
    
    def _generate_formation_chart(self, chart_type, filters):
        lineups_query = MatchLineup.objects.filter(is_starting_eleven=True)
        
        if 'formation_id' in filters:
            lineups_query = lineups_query.filter(formation_id=filters['formation_id'])
        
        if 'date_range' in filters:
            start_date = datetime.fromisoformat(filters['date_range']['start'])
            end_date = datetime.fromisoformat(filters['date_range']['end'])
            lineups_query = lineups_query.filter(
                match__scheduled_datetime__date__range=[start_date.date(), end_date.date()]
            )
        
        formation_data = list(lineups_query.values(
            'formation__name',
            'match__scheduled_datetime',
            'match__result',
            'match__chelsea_score',
            'match__opponent_score'
        ).order_by('match__scheduled_datetime'))
        
        return {
            'type': chart_type,
            'data': formation_data,
            'generated_at': timezone.now().isoformat()
        }