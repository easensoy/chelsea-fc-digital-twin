from django.db.models import Avg, Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
import logging
from collections import defaultdict, OrderedDict

from .models import Player, PlayerStats, Match, TeamStats, Formation, MatchLineup
from .exceptions import InsufficientDataError

logger = logging.getLogger('core.performance')

class TrendAnalyzer:
    
    def __init__(self):
        self.logger = logging.getLogger('core.performance')
        self.analysis_periods = {
            'short_term': 30,
            'medium_term': 90,
            'long_term': 365
        }
    
    def analyze_performance_trends(self, period_days=90):
        cutoff_date = timezone.now() - timedelta(days=period_days)
        
        recent_matches = Match.objects.filter(
            scheduled_datetime__gte=cutoff_date,
            status__in=['COMPLETED', 'FULL_TIME']
        ).order_by('scheduled_datetime')
        
        if recent_matches.count() < 5:
            raise InsufficientDataError(f"Insufficient matches for trend analysis: {recent_matches.count()} available")
        
        trends = {
            'analysis_period': period_days,
            'matches_analyzed': recent_matches.count(),
            'team_performance_trends': self._analyze_team_performance_trends(recent_matches),
            'individual_player_trends': self._analyze_individual_player_trends(recent_matches),
            'formation_effectiveness_trends': self._analyze_formation_trends(recent_matches),
            'scoring_trends': self._analyze_scoring_trends(recent_matches),
            'defensive_trends': self._analyze_defensive_trends(recent_matches),
            'possession_trends': self._analyze_possession_trends(recent_matches),
            'monthly_performance_breakdown': self._analyze_monthly_breakdown(recent_matches),
            'trend_predictions': self._generate_trend_predictions(recent_matches)
        }
        
        self.logger.info(f"Performance trends analyzed for {period_days} days: {recent_matches.count()} matches")
        return trends
    
    def analyze_player_development_trends(self, player, days=180):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        player_stats = PlayerStats.objects.filter(
            player=player,
            match__scheduled_datetime__gte=cutoff_date,
            match__status__in=['COMPLETED', 'FULL_TIME']
        ).select_related('match').order_by('match__scheduled_datetime')
        
        if player_stats.count() < 5:
            raise InsufficientDataError(f"Insufficient data for {player.full_name}: {player_stats.count()} matches")
        
        development_analysis = {
            'player_id': str(player.id),
            'player_name': player.full_name,
            'position': player.position,
            'analysis_period': days,
            'matches_analyzed': player_stats.count(),
            'performance_trajectory': self._calculate_performance_trajectory(player_stats),
            'skill_development_areas': self._analyze_skill_development(player_stats),
            'consistency_trends': self._analyze_consistency_trends(player_stats),
            'peak_performance_periods': self._identify_peak_periods(player_stats),
            'improvement_recommendations': self._generate_improvement_recommendations(player_stats, player),
            'development_velocity': self._calculate_development_velocity(player_stats)
        }
        
        return development_analysis
    
    def _analyze_team_performance_trends(self, matches):
        performance_data = []
        
        for match in matches:
            match_data = {
                'date': match.scheduled_datetime.date(),
                'result': match.result,
                'goals_scored': match.chelsea_score,
                'goals_conceded': match.opponent_score,
                'goal_difference': match.chelsea_score - match.opponent_score,
                'opponent': match.opponent.name,
                'is_home': match.is_home
            }
            
            try:
                team_stats = TeamStats.objects.get(match=match)
                match_data.update({
                    'possession': float(team_stats.possession_percentage or 50),
                    'shots_on_target': team_stats.shots_on_target,
                    'pass_accuracy': self._calculate_match_pass_accuracy(match)
                })
            except TeamStats.DoesNotExist:
                match_data.update({
                    'possession': None,
                    'shots_on_target': None,
                    'pass_accuracy': None
                })
            
            performance_data.append(match_data)
        
        trends = self._calculate_team_trends(performance_data)
        return trends
    
    def _analyze_individual_player_trends(self, matches):
        player_trends = {}
        
        for match in matches:
            player_stats = PlayerStats.objects.filter(match=match)
            
            for stat in player_stats:
                player_name = stat.player.full_name
                
                if player_name not in player_trends:
                    player_trends[player_name] = {
                        'player_id': str(stat.player.id),
                        'position': stat.player.position,
                        'performances': []
                    }
                
                player_trends[player_name]['performances'].append({
                    'date': match.scheduled_datetime.date(),
                    'rating': float(stat.rating),
                    'goals': stat.goals,
                    'assists': stat.assists,
                    'minutes_played': stat.minutes_played
                })
        
        analyzed_trends = {}
        for player_name, data in player_trends.items():
            if len(data['performances']) >= 3:
                analyzed_trends[player_name] = {
                    'player_id': data['player_id'],
                    'position': data['position'],
                    'trend_direction': self._calculate_player_trend_direction(data['performances']),
                    'average_rating': self._calculate_average_rating(data['performances']),
                    'performance_variance': self._calculate_performance_variance(data['performances']),
                    'recent_form': self._analyze_recent_form(data['performances'][-5:])
                }
        
        return analyzed_trends
    
    def _analyze_formation_trends(self, matches):
        formation_performance = defaultdict(list)
        
        for match in matches:
            lineups = MatchLineup.objects.filter(match=match, is_starting_eleven=True)
            
            for lineup in lineups:
                formation_name = lineup.formation.name
                formation_performance[formation_name].append({
                    'date': match.scheduled_datetime.date(),
                    'result': match.result,
                    'goals_scored': match.chelsea_score,
                    'goals_conceded': match.opponent_score
                })
        
        formation_trends = {}
        for formation, performances in formation_performance.items():
            if len(performances) >= 2:
                wins = len([p for p in performances if p['result'] == 'WIN'])
                total_games = len(performances)
                
                formation_trends[formation] = {
                    'matches_used': total_games,
                    'win_rate': round((wins / total_games) * 100, 2),
                    'average_goals_scored': round(sum(p['goals_scored'] for p in performances) / total_games, 2),
                    'average_goals_conceded': round(sum(p['goals_conceded'] for p in performances) / total_games, 2),
                    'effectiveness_trend': self._calculate_formation_effectiveness_trend(performances)
                }
        
        return formation_trends
    
    def _analyze_scoring_trends(self, matches):
        scoring_by_period = {'first_half': 0, 'second_half': 0}
        monthly_scoring = defaultdict(int)
        opponent_strength_scoring = {'strong': [], 'medium': [], 'weak': []}
        
        total_goals = 0
        
        for match in matches:
            total_goals += match.chelsea_score
            month_key = match.scheduled_datetime.strftime('%Y-%m')
            monthly_scoring[month_key] += match.chelsea_score
            
            opponent_strength = self._assess_opponent_strength(match.opponent)
            opponent_strength_scoring[opponent_strength].append(match.chelsea_score)
        
        avg_goals_per_match = round(total_goals / matches.count(), 2)
        
        trend_direction = self._calculate_scoring_trend_direction(matches)
        
        return {
            'total_goals': total_goals,
            'average_goals_per_match': avg_goals_per_match,
            'monthly_breakdown': dict(monthly_scoring),
            'scoring_trend_direction': trend_direction,
            'consistency_score': self._calculate_scoring_consistency(matches),
            'opponent_strength_analysis': {
                strength: round(sum(goals) / len(goals), 2) if goals else 0
                for strength, goals in opponent_strength_scoring.items()
            }
        }
    
    def _analyze_defensive_trends(self, matches):
        total_goals_conceded = sum(match.opponent_score for match in matches)
        clean_sheets = matches.filter(opponent_score=0).count()
        
        defensive_record = {
            'total_goals_conceded': total_goals_conceded,
            'average_goals_conceded': round(total_goals_conceded / matches.count(), 2),
            'clean_sheets': clean_sheets,
            'clean_sheet_rate': round((clean_sheets / matches.count()) * 100, 2),
            'defensive_trend': self._calculate_defensive_trend(matches)
        }
        
        return defensive_record
    
    def _analyze_possession_trends(self, matches):
        possession_data = []
        
        for match in matches:
            try:
                team_stats = TeamStats.objects.get(match=match)
                if team_stats.possession_percentage:
                    possession_data.append({
                        'date': match.scheduled_datetime.date(),
                        'possession': float(team_stats.possession_percentage),
                        'result': match.result
                    })
            except TeamStats.DoesNotExist:
                continue
        
        if not possession_data:
            return {'insufficient_data': True}
        
        avg_possession = sum(p['possession'] for p in possession_data) / len(possession_data)
        possession_trend = self._calculate_possession_trend(possession_data)
        
        return {
            'average_possession': round(avg_possession, 2),
            'possession_trend': possession_trend,
            'possession_vs_results': self._analyze_possession_vs_results(possession_data),
            'possession_consistency': self._calculate_possession_consistency(possession_data)
        }
    
    def _analyze_monthly_breakdown(self, matches):
        monthly_data = defaultdict(lambda: {
            'matches': 0, 'wins': 0, 'draws': 0, 'losses': 0,
            'goals_scored': 0, 'goals_conceded': 0
        })
        
        for match in matches:
            month_key = match.scheduled_datetime.strftime('%Y-%m')
            monthly_data[month_key]['matches'] += 1
            monthly_data[month_key]['goals_scored'] += match.chelsea_score
            monthly_data[month_key]['goals_conceded'] += match.opponent_score
            
            if match.result == 'WIN':
                monthly_data[month_key]['wins'] += 1
            elif match.result == 'DRAW':
                monthly_data[month_key]['draws'] += 1
            else:
                monthly_data[month_key]['losses'] += 1
        
        formatted_monthly = {}
        for month, data in monthly_data.items():
            if data['matches'] > 0:
                formatted_monthly[month] = {
                    'matches_played': data['matches'],
                    'win_rate': round((data['wins'] / data['matches']) * 100, 2),
                    'goals_per_match': round(data['goals_scored'] / data['matches'], 2),
                    'goals_conceded_per_match': round(data['goals_conceded'] / data['matches'], 2),
                    'points': data['wins'] * 3 + data['draws']
                }
        
        return OrderedDict(sorted(formatted_monthly.items()))
    
    def _generate_trend_predictions(self, matches):
        recent_performance = matches.order_by('-scheduled_datetime')[:5]
        recent_form = [match.result for match in recent_performance]
        
        win_momentum = recent_form.count('WIN') / len(recent_form)
        
        if win_momentum >= 0.8:
            next_match_prediction = 'Strong chance of positive result'
        elif win_momentum >= 0.6:
            next_match_prediction = 'Good chance of positive result'
        elif win_momentum >= 0.4:
            next_match_prediction = 'Mixed recent form - unpredictable'
        else:
            next_match_prediction = 'Concerning form - improvement needed'
        
        goal_trend = self._calculate_scoring_trend_direction(matches)
        defensive_trend = self._calculate_defensive_trend(matches)
        
        return {
            'next_match_outlook': next_match_prediction,
            'attacking_trajectory': goal_trend,
            'defensive_trajectory': defensive_trend,
            'overall_momentum': self._assess_overall_momentum(recent_form),
            'confidence_level': self._calculate_prediction_confidence(matches)
        }
    
    def _calculate_performance_trajectory(self, player_stats):
        ratings = [float(stat.rating) for stat in player_stats]
        dates = [stat.match.scheduled_datetime for stat in player_stats]
        
        if len(ratings) < 3:
            return {'insufficient_data': True}
        
        early_period = ratings[-len(ratings)//3:]
        recent_period = ratings[:len(ratings)//3]
        
        early_avg = sum(early_period) / len(early_period)
        recent_avg = sum(recent_period) / len(recent_period)
        
        trajectory = 'improving' if recent_avg > early_avg + 0.3 else 'declining' if recent_avg < early_avg - 0.3 else 'stable'
        
        return {
            'trajectory_direction': trajectory,
            'early_period_average': round(early_avg, 2),
            'recent_period_average': round(recent_avg, 2),
            'improvement_rate': round(recent_avg - early_avg, 2),
            'trend_strength': abs(recent_avg - early_avg)
        }
    
    def _analyze_skill_development(self, player_stats):
        skills_progression = {
            'attacking': [],
            'passing': [],
            'defensive': []
        }
        
        for stat in player_stats:
            attacking_score = (stat.goals * 2) + stat.assists + (stat.shots_on_target * 0.5)
            passing_score = (stat.passes_completed / max(stat.passes_attempted, 1)) * 100 if stat.passes_attempted > 0 else 0
            defensive_score = stat.tackles + stat.interceptions + (stat.clearances * 0.5)
            
            skills_progression['attacking'].append(attacking_score)
            skills_progression['passing'].append(passing_score)
            skills_progression['defensive'].append(defensive_score)
        
        skill_trends = {}
        for skill, scores in skills_progression.items():
            if len(scores) >= 3:
                early_avg = sum(scores[-3:]) / 3
                recent_avg = sum(scores[:3]) / 3
                
                skill_trends[skill] = {
                    'trend': 'improving' if recent_avg > early_avg else 'declining' if recent_avg < early_avg else 'stable',
                    'improvement_rate': round(recent_avg - early_avg, 2)
                }
        
        return skill_trends
    
    def _analyze_consistency_trends(self, player_stats):
        ratings = [float(stat.rating) for stat in player_stats]
        
        if len(ratings) < 5:
            return {'insufficient_data': True}
        
        variance = self._calculate_variance(ratings)
        consistency_score = max(0, 100 - (variance * 20))
        
        consistent_performances = len([r for r in ratings if 6.5 <= r <= 8.5])
        consistency_rate = (consistent_performances / len(ratings)) * 100
        
        return {
            'consistency_score': round(consistency_score, 2),
            'consistency_rate': round(consistency_rate, 2),
            'performance_variance': round(variance, 2),
            'trend_assessment': 'highly_consistent' if consistency_score > 80 else 'moderately_consistent' if consistency_score > 60 else 'inconsistent'
        }
    
    def _identify_peak_periods(self, player_stats):
        ratings = [(stat.match.scheduled_datetime, float(stat.rating)) for stat in player_stats]
        ratings.sort(key=lambda x: x[0])
        
        peak_periods = []
        current_streak = []
        
        for date, rating in ratings:
            if rating >= 7.5:
                current_streak.append((date, rating))
            else:
                if len(current_streak) >= 3:
                    peak_periods.append({
                        'start_date': current_streak[0][0].strftime('%d/%m/%Y'),
                        'end_date': current_streak[-1][0].strftime('%d/%m/%Y'),
                        'duration_matches': len(current_streak),
                        'average_rating': round(sum(r[1] for r in current_streak) / len(current_streak), 2)
                    })
                current_streak = []
        
        if len(current_streak) >= 3:
            peak_periods.append({
                'start_date': current_streak[0][0].strftime('%d/%m/%Y'),
                'end_date': current_streak[-1][0].strftime('%d/%m/%Y'),
                'duration_matches': len(current_streak),
                'average_rating': round(sum(r[1] for r in current_streak) / len(current_streak), 2)
            })
        
        return peak_periods
    
    def _generate_improvement_recommendations(self, player_stats, player):
        recommendations = []
        
        recent_ratings = [float(stat.rating) for stat in player_stats[:5]]
        recent_avg = sum(recent_ratings) / len(recent_ratings) if recent_ratings else 0
        
        if recent_avg < 6.5:
            recommendations.append({
                'area': 'Overall Performance',
                'recommendation': 'Focus on fundamental skills and match preparation',
                'priority': 'High'
            })
        
        goal_output = sum(stat.goals for stat in player_stats[:10])
        if player.position in ['ST', 'LW', 'RW', 'CAM'] and goal_output < 3:
            recommendations.append({
                'area': 'Goal Scoring',
                'recommendation': 'Increase attacking output through better positioning and finishing',
                'priority': 'High'
            })
        
        consistency_analysis = self._analyze_consistency_trends(player_stats)
        if not consistency_analysis.get('insufficient_data') and consistency_analysis['consistency_score'] < 60:
            recommendations.append({
                'area': 'Consistency',
                'recommendation': 'Work on maintaining performance levels across matches',
                'priority': 'Medium'
            })
        
        return recommendations
    
    def _calculate_development_velocity(self, player_stats):
        if player_stats.count() < 6:
            return {'insufficient_data': True}
        
        ratings = [float(stat.rating) for stat in player_stats.order_by('match__scheduled_datetime')]
        
        first_quarter = ratings[:len(ratings)//4]
        last_quarter = ratings[-len(ratings)//4:]
        
        first_avg = sum(first_quarter) / len(first_quarter)
        last_avg = sum(last_quarter) / len(last_quarter)
        
        development_rate = (last_avg - first_avg) / (len(ratings) / 4)
        
        velocity_assessment = 'rapid' if development_rate > 0.1 else 'steady' if development_rate > 0.05 else 'slow' if development_rate > 0 else 'declining'
        
        return {
            'development_rate_per_match': round(development_rate, 3),
            'velocity_assessment': velocity_assessment,
            'total_improvement': round(last_avg - first_avg, 2)
        }
    
    def _calculate_team_trends(self, performance_data):
        if len(performance_data) < 3:
            return {'insufficient_data': True}
        
        recent_third = performance_data[-len(performance_data)//3:]
        early_third = performance_data[:len(performance_data)//3]
        
        recent_goals_avg = sum(p['goals_scored'] for p in recent_third) / len(recent_third)
        early_goals_avg = sum(p['goals_scored'] for p in early_third) / len(early_third)
        
        recent_conceded_avg = sum(p['goals_conceded'] for p in recent_third) / len(recent_third)
        early_conceded_avg = sum(p['goals_conceded'] for p in early_third) / len(early_third)
        
        return {
            'attacking_trend': 'improving' if recent_goals_avg > early_goals_avg else 'declining' if recent_goals_avg < early_goals_avg else 'stable',
            'defensive_trend': 'improving' if recent_conceded_avg < early_conceded_avg else 'declining' if recent_conceded_avg > early_conceded_avg else 'stable',
            'goal_difference_trend': round((recent_goals_avg - recent_conceded_avg) - (early_goals_avg - early_conceded_avg), 2)
        }
    
    def _calculate_variance(self, values):
        if len(values) <= 1:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def _calculate_player_trend_direction(self, performances):
        ratings = [p['rating'] for p in performances]
        
        if len(ratings) < 3:
            return 'insufficient_data'
        
        recent_avg = sum(ratings[:3]) / 3
        earlier_avg = sum(ratings[-3:]) / 3
        
        difference = recent_avg - earlier_avg
        
        if difference > 0.5:
            return 'strongly_improving'
        elif difference > 0.2:
            return 'improving'
        elif difference < -0.5:
            return 'strongly_declining'
        elif difference < -0.2:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_average_rating(self, performances):
        ratings = [p['rating'] for p in performances]
        return round(sum(ratings) / len(ratings), 2)
    
    def _calculate_performance_variance(self, performances):
        ratings = [p['rating'] for p in performances]
        return round(self._calculate_variance(ratings), 2)
    
    def _analyze_recent_form(self, recent_performances):
        if len(recent_performances) < 3:
            return 'insufficient_data'
        
        avg_rating = sum(p['rating'] for p in recent_performances) / len(recent_performances)
        
        if avg_rating >= 7.5:
            return 'excellent_form'
        elif avg_rating >= 7.0:
            return 'good_form'
        elif avg_rating >= 6.0:
            return 'average_form'
        else:
            return 'poor_form'
    
    def _calculate_formation_effectiveness_trend(self, performances):
        if len(performances) < 4:
            return 'insufficient_data'
        
        recent_half = performances[-len(performances)//2:]
        early_half = performances[:len(performances)//2]
        
        recent_wins = len([p for p in recent_half if p['result'] == 'WIN'])
        early_wins = len([p for p in early_half if p['result'] == 'WIN'])
        
        recent_win_rate = recent_wins / len(recent_half)
        early_win_rate = early_wins / len(early_half)
        
        if recent_win_rate > early_win_rate + 0.2:
            return 'improving'
        elif recent_win_rate < early_win_rate - 0.2:
            return 'declining'
        else:
            return 'stable'
    
    def _assess_opponent_strength(self, opponent):
        if 'Champions League' in opponent.league or 'Premier League' in opponent.league:
            return 'strong'
        elif 'Championship' in opponent.league or 'League' in opponent.league:
            return 'medium'
        else:
            return 'weak'
    
    def _calculate_scoring_trend_direction(self, matches):
        goal_data = [(match.scheduled_datetime, match.chelsea_score) for match in matches]
        goal_data.sort(key=lambda x: x[0])
        
        if len(goal_data) < 4:
            return 'insufficient_data'
        
        recent_quarter = goal_data[-len(goal_data)//4:]
        early_quarter = goal_data[:len(goal_data)//4]
        
        recent_avg = sum(g[1] for g in recent_quarter) / len(recent_quarter)
        early_avg = sum(g[1] for g in early_quarter) / len(early_quarter)
        
        if recent_avg > early_avg + 0.5:
            return 'strongly_improving'
        elif recent_avg > early_avg:
            return 'improving'
        elif recent_avg < early_avg - 0.5:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_scoring_consistency(self, matches):
        goals = [match.chelsea_score for match in matches]
        variance = self._calculate_variance(goals)
        
        consistency_score = max(0, 100 - (variance * 30))
        return round(consistency_score, 2)
    
    def _calculate_defensive_trend(self, matches):
        defensive_data = [(match.scheduled_datetime, match.opponent_score) for match in matches]
        defensive_data.sort(key=lambda x: x[0])
        
        if len(defensive_data) < 4:
            return 'insufficient_data'
        
        recent_quarter = defensive_data[-len(defensive_data)//4:]
        early_quarter = defensive_data[:len(defensive_data)//4]
        
        recent_avg = sum(g[1] for g in recent_quarter) / len(recent_quarter)
        early_avg = sum(g[1] for g in early_quarter) / len(early_quarter)
        
        if recent_avg < early_avg - 0.3:
            return 'improving'
        elif recent_avg > early_avg + 0.3:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_match_pass_accuracy(self, match):
        player_stats = PlayerStats.objects.filter(match=match)
        
        total_completed = player_stats.aggregate(total=Sum('passes_completed'))['total'] or 0
        total_attempted = player_stats.aggregate(total=Sum('passes_attempted'))['total'] or 0
        
        if total_attempted == 0:
            return None
        
        return round((total_completed / total_attempted) * 100, 2)
    
    def _calculate_possession_trend(self, possession_data):
        if len(possession_data) < 4:
            return 'insufficient_data'
        
        recent_quarter = possession_data[-len(possession_data)//4:]
        early_quarter = possession_data[:len(possession_data)//4]
        
        recent_avg = sum(p['possession'] for p in recent_quarter) / len(recent_quarter)
        early_avg = sum(p['possession'] for p in early_quarter) / len(early_quarter)
        
        if recent_avg > early_avg + 5:
            return 'improving'
        elif recent_avg < early_avg - 5:
            return 'declining'
        else:
            return 'stable'
    
    def _analyze_possession_vs_results(self, possession_data):
        high_possession_wins = len([p for p in possession_data if p['possession'] > 60 and p['result'] == 'WIN'])
        high_possession_total = len([p for p in possession_data if p['possession'] > 60])
        
        if high_possession_total == 0:
            return {'insufficient_high_possession_games': True}
        
        win_rate_with_possession = (high_possession_wins / high_possession_total) * 100
        
        return {
            'high_possession_win_rate': round(win_rate_with_possession, 2),
            'possession_effectiveness': 'high' if win_rate_with_possession > 70 else 'medium' if win_rate_with_possession > 50 else 'low'
        }
    
    def _calculate_possession_consistency(self, possession_data):
        possessions = [p['possession'] for p in possession_data]
        variance = self._calculate_variance(possessions)
        
        consistency_score = max(0, 100 - (variance * 2))
        return round(consistency_score, 2)
    
    def _assess_overall_momentum(self, recent_form):
        wins = recent_form.count('WIN')
        losses = recent_form.count('LOSS')
        
        if wins >= 4:
            return 'very_positive'
        elif wins >= 3:
            return 'positive'
        elif losses >= 3:
            return 'concerning'
        else:
            return 'neutral'
    
    def _calculate_prediction_confidence(self, matches):
        data_quality_score = min(100, matches.count() * 10)
        
        recent_consistency = self._calculate_recent_consistency(matches)
        
        confidence = (data_quality_score * 0.6) + (recent_consistency * 0.4)
        
        return round(min(100, confidence), 2)
    
    def _calculate_recent_consistency(self, matches):
        recent_results = [match.result for match in matches.order_by('-scheduled_datetime')[:5]]
        
        win_rate = recent_results.count('WIN') / len(recent_results)
        
        if win_rate >= 0.8 or win_rate <= 0.2:
            return 90
        elif win_rate >= 0.6 or win_rate <= 0.4:
            return 70
        else:
            return 50