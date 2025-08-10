from django.db.models import Avg, Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
import logging
import json

from .models import Player, PlayerStats, Match, Formation, MatchLineup, TeamStats, Opponent, Analytics
from .performance_tracker import PerformanceTracker
from .career_analyzer import CareerAnalyzer
from .tactical_analyzer import TacticalAnalyzer
from .trend_analyzer import TrendAnalyzer
from .comparison_engine import ComparisonEngine
from .prediction_models import PredictionModels
from .exceptions import InsufficientDataError, ValidationError

logger = logging.getLogger('core.performance')

class ReportGenerators:
    
    def __init__(self):
        self.logger = logging.getLogger('core.performance')
        self.performance_tracker = PerformanceTracker()
        self.career_analyzer = CareerAnalyzer()
        self.tactical_analyzer = TacticalAnalyzer()
        self.trend_analyzer = TrendAnalyzer()
        self.comparison_engine = ComparisonEngine()
        self.prediction_models = PredictionModels()
    
    def generate_comprehensive_season_report(self, season_start_date=None):
        if not season_start_date:
            season_start_date = timezone.now().date() - timedelta(days=180)
        
        season_matches = Match.objects.filter(
            scheduled_datetime__date__gte=season_start_date,
            status__in=['COMPLETED', 'FULL_TIME']
        )
        
        if season_matches.count() < 5:
            raise InsufficientDataError("Insufficient matches for comprehensive season report")
        
        report = {
            'report_metadata': {
                'title': 'Chelsea FC Comprehensive Season Report',
                'generated_at': timezone.now().isoformat(),
                'season_start': season_start_date.isoformat(),
                'matches_analyzed': season_matches.count(),
                'report_type': 'comprehensive_season'
            },
            'executive_summary': self._generate_executive_summary(season_matches),
            'team_performance_overview': self._generate_team_performance_overview(season_matches),
            'individual_player_analysis': self._generate_individual_player_analysis(season_matches),
            'tactical_analysis': self._generate_tactical_analysis_section(season_matches),
            'formation_effectiveness': self._analyze_formation_effectiveness(season_matches),
            'opponent_analysis': self._generate_opponent_analysis(season_matches),
            'performance_trends': self._generate_performance_trends_section(season_matches),
            'key_statistics': self._compile_key_statistics(season_matches),
            'areas_for_improvement': self._identify_improvement_areas(season_matches),
            'future_projections': self._generate_future_projections(),
            'recommendations': self._generate_season_recommendations(season_matches)
        }
        
        self.logger.info(f"Comprehensive season report generated covering {season_matches.count()} matches")
        return report
    
    def generate_match_analysis_report(self, match):
        if not isinstance(match, Match):
            raise ValidationError("Invalid match object provided")
        
        if match.status not in ['COMPLETED', 'FULL_TIME']:
            raise ValidationError("Match analysis report only available for completed matches")
        
        report = {
            'report_metadata': {
                'title': f'Match Analysis: Chelsea vs {match.opponent.name}',
                'match_date': match.scheduled_datetime.strftime('%d/%m/%Y'),
                'generated_at': timezone.now().isoformat(),
                'report_type': 'match_analysis'
            },
            'match_overview': self._generate_match_overview(match),
            'performance_analysis': self._analyze_match_performance(match),
            'tactical_breakdown': self._generate_tactical_breakdown(match),
            'individual_ratings': self._generate_individual_ratings(match),
            'key_moments_analysis': self._analyze_key_moments(match),
            'statistical_breakdown': self._generate_statistical_breakdown(match),
            'comparison_with_previous_meetings': self._compare_with_previous_meetings(match),
            'lessons_learned': self._extract_lessons_learned(match),
            'areas_for_improvement': self._identify_match_improvement_areas(match)
        }
        
        self.logger.info(f"Match analysis report generated for {match}")
        return report
    
    def generate_player_development_report(self, player, months=6):
        if not isinstance(player, Player):
            raise ValidationError("Invalid player object provided")
        
        cutoff_date = timezone.now() - timedelta(days=months * 30)
        
        player_stats = PlayerStats.objects.filter(
            player=player,
            match__scheduled_datetime__gte=cutoff_date,
            match__status__in=['COMPLETED', 'FULL_TIME']
        )
        
        if not player_stats.exists():
            raise InsufficientDataError(f"Insufficient data for {player.full_name} development report")
        
        report = {
            'report_metadata': {
                'title': f'Player Development Report: {player.full_name}',
                'analysis_period': f'{months} months',
                'generated_at': timezone.now().isoformat(),
                'report_type': 'player_development'
            },
            'player_profile': self._generate_player_profile(player),
            'performance_summary': self._generate_performance_summary(player, player_stats),
            'career_progression': self._analyze_career_progression(player),
            'development_trends': self._analyze_development_trends(player, player_stats),
            'strengths_and_weaknesses': self._identify_player_strengths_weaknesses(player_stats),
            'consistency_analysis': self._analyze_player_consistency(player_stats),
            'comparative_analysis': self._generate_comparative_analysis(player),
            'future_potential': self._assess_future_potential(player, player_stats),
            'development_recommendations': self._generate_development_recommendations(player, player_stats)
        }
        
        self.logger.info(f"Player development report generated for {player.full_name}")
        return report
    
    def generate_tactical_insights_report(self, days=90):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        recent_matches = Match.objects.filter(
            scheduled_datetime__gte=cutoff_date,
            status__in=['COMPLETED', 'FULL_TIME']
        )
        
        if recent_matches.count() < 5:
            raise InsufficientDataError("Insufficient matches for tactical insights report")
        
        report = {
            'report_metadata': {
                'title': 'Tactical Insights and Analysis Report',
                'analysis_period': f'{days} days',
                'generated_at': timezone.now().isoformat(),
                'matches_analyzed': recent_matches.count(),
                'report_type': 'tactical_insights'
            },
            'formation_analysis': self._analyze_formation_usage(recent_matches),
            'tactical_patterns': self._identify_tactical_patterns(recent_matches),
            'opponent_adaptation': self._analyze_opponent_adaptation(recent_matches),
            'positional_analysis': self._analyze_positional_effectiveness(recent_matches),
            'set_piece_analysis': self._analyze_set_piece_effectiveness(recent_matches),
            'pressing_and_defensive_shape': self._analyze_defensive_tactics(recent_matches),
            'attacking_patterns': self._analyze_attacking_patterns(recent_matches),
            'tactical_flexibility': self._assess_tactical_flexibility(recent_matches),
            'recommendations': self._generate_tactical_recommendations(recent_matches)
        }
        
        self.logger.info(f"Tactical insights report generated covering {recent_matches.count()} matches")
        return report
    
    def generate_pre_match_briefing(self, opponent, proposed_formation=None):
        if not isinstance(opponent, Opponent):
            raise ValidationError("Invalid opponent object provided")
        
        historical_matches = Match.objects.filter(
            opponent=opponent,
            scheduled_datetime__gte=timezone.now() - timedelta(days=730),
            status__in=['COMPLETED', 'FULL_TIME']
        )
        
        briefing = {
            'briefing_metadata': {
                'title': f'Pre-Match Briefing: Chelsea vs {opponent.name}',
                'generated_at': timezone.now().isoformat(),
                'report_type': 'pre_match_briefing'
            },
            'opponent_overview': self._generate_opponent_overview(opponent),
            'historical_record': self._analyze_historical_record(opponent, historical_matches),
            'recent_form_analysis': self._analyze_recent_form(opponent),
            'tactical_expectations': self._generate_tactical_expectations(opponent, historical_matches),
            'key_player_threats': self._identify_key_threats(opponent, historical_matches),
            'predicted_lineup': self._predict_opponent_lineup(opponent),
            'match_prediction': self._generate_match_prediction(opponent, proposed_formation),
            'tactical_preparation': self._generate_tactical_preparation_guide(opponent, proposed_formation),
            'set_piece_preparation': self._generate_set_piece_preparation(opponent, historical_matches),
            'key_focus_areas': self._identify_key_focus_areas(opponent, historical_matches)
        }
        
        self.logger.info(f"Pre-match briefing generated for {opponent.name}")
        return briefing
    
    def generate_monthly_performance_report(self, year=None, month=None):
        if not year:
            year = timezone.now().year
        if not month:
            month = timezone.now().month
        
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month + 1, 1).date()
        
        monthly_matches = Match.objects.filter(
            scheduled_datetime__date__gte=start_date,
            scheduled_datetime__date__lt=end_date,
            status__in=['COMPLETED', 'FULL_TIME']
        )
        
        report = {
            'report_metadata': {
                'title': f'Monthly Performance Report - {start_date.strftime("%B %Y")}',
                'reporting_period': f'{start_date.strftime("%B %Y")}',
                'generated_at': timezone.now().isoformat(),
                'matches_analyzed': monthly_matches.count(),
                'report_type': 'monthly_performance'
            },
            'monthly_summary': self._generate_monthly_summary(monthly_matches),
            'performance_highlights': self._identify_monthly_highlights(monthly_matches),
            'statistical_overview': self._generate_monthly_statistics(monthly_matches),
            'player_of_the_month': self._identify_player_of_month(monthly_matches),
            'tactical_review': self._review_monthly_tactics(monthly_matches),
            'improvement_areas': self._identify_monthly_improvements(monthly_matches),
            'goals_and_objectives': self._assess_monthly_objectives(monthly_matches),
            'looking_ahead': self._generate_forward_outlook()
        }
        
        self.logger.info(f"Monthly performance report generated for {start_date.strftime('%B %Y')}")
        return report
    
    def _generate_executive_summary(self, season_matches):
        total_matches = season_matches.count()
        wins = season_matches.filter(result='WIN').count()
        draws = season_matches.filter(result='DRAW').count()
        losses = season_matches.filter(result='LOSS').count()
        
        win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
        
        goals_scored = sum(match.chelsea_score for match in season_matches)
        goals_conceded = sum(match.opponent_score for match in season_matches)
        
        recent_form = season_matches.order_by('-scheduled_datetime')[:5]
        recent_wins = recent_form.filter(result='WIN').count()
        
        return {
            'overall_record': f'{wins}W-{draws}D-{losses}L from {total_matches} matches',
            'win_rate': round(win_rate, 1),
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'goal_difference': goals_scored - goals_conceded,
            'goals_per_match': round(goals_scored / total_matches, 2) if total_matches > 0 else 0,
            'goals_conceded_per_match': round(goals_conceded / total_matches, 2) if total_matches > 0 else 0,
            'recent_form': f'{recent_wins} wins from last 5 matches',
            'season_assessment': self._assess_season_performance(win_rate, goals_scored, goals_conceded, total_matches)
        }
    
    def _generate_team_performance_overview(self, season_matches):
        performance_metrics = {}
        
        for match in season_matches:
            try:
                team_stats = TeamStats.objects.get(match=match)
                player_stats = PlayerStats.objects.filter(match=match)
                
                if team_stats.possession_percentage:
                    if 'possession' not in performance_metrics:
                        performance_metrics['possession'] = []
                    performance_metrics['possession'].append(float(team_stats.possession_percentage))
                
                if player_stats.exists():
                    avg_rating = player_stats.aggregate(avg=Avg('rating'))['avg']
                    if avg_rating:
                        if 'team_ratings' not in performance_metrics:
                            performance_metrics['team_ratings'] = []
                        performance_metrics['team_ratings'].append(avg_rating)
                        
            except TeamStats.DoesNotExist:
                continue
        
        overview = {
            'matches_analyzed': season_matches.count(),
            'home_record': self._calculate_home_away_record(season_matches, True),
            'away_record': self._calculate_home_away_record(season_matches, False)
        }
        
        if 'possession' in performance_metrics:
            overview['average_possession'] = round(sum(performance_metrics['possession']) / len(performance_metrics['possession']), 1)
        
        if 'team_ratings' in performance_metrics:
            overview['average_team_rating'] = round(sum(performance_metrics['team_ratings']) / len(performance_metrics['team_ratings']), 2)
        
        return overview
    
    def _generate_individual_player_analysis(self, season_matches):
        active_players = Player.objects.filter(is_active=True)
        player_analysis = []
        
        for player in active_players:
            player_stats = PlayerStats.objects.filter(
                player=player,
                match__in=season_matches
            )
            
            if player_stats.exists():
                analysis = {
                    'player_name': player.full_name,
                    'position': player.position,
                    'matches_played': player_stats.count(),
                    'total_minutes': player_stats.aggregate(total=Sum('minutes_played'))['total'] or 0,
                    'goals': player_stats.aggregate(total=Sum('goals'))['total'] or 0,
                    'assists': player_stats.aggregate(total=Sum('assists'))['total'] or 0,
                    'average_rating': round(player_stats.aggregate(avg=Avg('rating'))['avg'] or 0, 2),
                    'contribution_rating': self._calculate_player_contribution_rating(player_stats)
                }
                player_analysis.append(analysis)
        
        return sorted(player_analysis, key=lambda x: x['contribution_rating'], reverse=True)[:15]
    
    def _generate_tactical_analysis_section(self, season_matches):
        formation_usage = {}
        tactical_outcomes = {}
        
        for match in season_matches:
            lineups = MatchLineup.objects.filter(match=match, is_starting_eleven=True)
            
            for lineup in lineups:
                formation_name = lineup.formation.name
                
                if formation_name not in formation_usage:
                    formation_usage[formation_name] = {'matches': 0, 'wins': 0, 'goals_scored': 0, 'goals_conceded': 0}
                
                formation_usage[formation_name]['matches'] += 1
                if match.result == 'WIN':
                    formation_usage[formation_name]['wins'] += 1
                formation_usage[formation_name]['goals_scored'] += match.chelsea_score
                formation_usage[formation_name]['goals_conceded'] += match.opponent_score
        
        for formation, data in formation_usage.items():
            tactical_outcomes[formation] = {
                'usage_rate': round((data['matches'] / season_matches.count()) * 100, 1),
                'win_rate': round((data['wins'] / data['matches']) * 100, 1) if data['matches'] > 0 else 0,
                'goals_per_match': round(data['goals_scored'] / data['matches'], 2) if data['matches'] > 0 else 0,
                'goals_conceded_per_match': round(data['goals_conceded'] / data['matches'], 2) if data['matches'] > 0 else 0
            }
        
        return {
            'formation_usage': formation_usage,
            'tactical_effectiveness': tactical_outcomes,
            'preferred_formation': max(formation_usage.items(), key=lambda x: x[1]['matches'])[0] if formation_usage else 'N/A',
            'most_effective_formation': max(tactical_outcomes.items(), key=lambda x: x[1]['win_rate'])[0] if tactical_outcomes else 'N/A'
        }
    
    def _analyze_formation_effectiveness(self, season_matches):
        formations = Formation.objects.filter(is_active=True)
        effectiveness_analysis = {}
        
        for formation in formations:
            formation_matches = season_matches.filter(
                lineups__formation=formation,
                lineups__is_starting_eleven=True
            ).distinct()
            
            if formation_matches.exists():
                wins = formation_matches.filter(result='WIN').count()
                total = formation_matches.count()
                
                effectiveness_analysis[formation.name] = {
                    'matches_used': total,
                    'win_rate': round((wins / total) * 100, 1),
                    'effectiveness_score': self._calculate_formation_effectiveness_score(formation_matches),
                    'best_results': self._get_formation_best_results(formation_matches),
                    'suitability_assessment': self._assess_formation_suitability(formation, formation_matches)
                }
        
        return effectiveness_analysis
    
    def _generate_opponent_analysis(self, season_matches):
        opponent_records = {}
        
        for match in season_matches:
            opponent_name = match.opponent.name
            
            if opponent_name not in opponent_records:
                opponent_records[opponent_name] = {
                    'matches': 0, 'wins': 0, 'draws': 0, 'losses': 0,
                    'goals_scored': 0, 'goals_conceded': 0
                }
            
            opponent_records[opponent_name]['matches'] += 1
            opponent_records[opponent_name]['goals_scored'] += match.chelsea_score
            opponent_records[opponent_name]['goals_conceded'] += match.opponent_score
            
            if match.result == 'WIN':
                opponent_records[opponent_name]['wins'] += 1
            elif match.result == 'DRAW':
                opponent_records[opponent_name]['draws'] += 1
            else:
                opponent_records[opponent_name]['losses'] += 1
        
        return {
            'opponents_faced': len(opponent_records),
            'detailed_records': opponent_records,
            'most_challenging_opponents': self._identify_challenging_opponents(opponent_records),
            'best_results': self._identify_best_results(opponent_records)
        }
    
    def _generate_performance_trends_section(self, season_matches):
        try:
            trends = self.trend_analyzer.analyze_performance_trends(period_days=180)
            return {
                'team_performance_trends': trends.get('team_performance_trends', {}),
                'scoring_trends': trends.get('scoring_trends', {}),
                'defensive_trends': trends.get('defensive_trends', {}),
                'monthly_breakdown': trends.get('monthly_performance_breakdown', {})
            }
        except InsufficientDataError:
            return {'insufficient_data': True}
    
    def _compile_key_statistics(self, season_matches):
        total_matches = season_matches.count()
        
        stats = {
            'total_matches': total_matches,
            'total_goals_scored': sum(match.chelsea_score for match in season_matches),
            'total_goals_conceded': sum(match.opponent_score for match in season_matches),
            'clean_sheets': season_matches.filter(opponent_score=0).count(),
            'failed_to_score': season_matches.filter(chelsea_score=0).count(),
            'biggest_win': self._find_biggest_win(season_matches),
            'biggest_loss': self._find_biggest_loss(season_matches),
            'highest_scoring_match': self._find_highest_scoring_match(season_matches)
        }
        
        if total_matches > 0:
            stats.update({
                'clean_sheet_rate': round((stats['clean_sheets'] / total_matches) * 100, 1),
                'scoring_rate': round(((total_matches - stats['failed_to_score']) / total_matches) * 100, 1)
            })
        
        return stats
    
    def _identify_improvement_areas(self, season_matches):
        improvement_areas = []
        
        total_matches = season_matches.count()
        goals_scored = sum(match.chelsea_score for match in season_matches)
        goals_conceded = sum(match.opponent_score for match in season_matches)
        
        avg_goals_scored = goals_scored / total_matches if total_matches > 0 else 0
        avg_goals_conceded = goals_conceded / total_matches if total_matches > 0 else 0
        
        if avg_goals_scored < 2.0:
            improvement_areas.append({
                'area': 'Goal Scoring',
                'concern': f'Average of {avg_goals_scored:.2f} goals per match is below expectations',
                'priority': 'High'
            })
        
        if avg_goals_conceded > 1.5:
            improvement_areas.append({
                'area': 'Defensive Solidity',
                'concern': f'Conceding {avg_goals_conceded:.2f} goals per match on average',
                'priority': 'High'
            })
        
        away_matches = season_matches.filter(is_home=False)
        if away_matches.exists():
            away_win_rate = (away_matches.filter(result='WIN').count() / away_matches.count()) * 100
            if away_win_rate < 40:
                improvement_areas.append({
                    'area': 'Away Form',
                    'concern': f'Away win rate of {away_win_rate:.1f}% needs improvement',
                    'priority': 'Medium'
                })
        
        return improvement_areas
    
    def _generate_future_projections(self):
        try:
            projections = self.prediction_models.predict_season_trajectory(months_ahead=3)
            return {
                'three_month_outlook': projections.get('projected_performance_trends', {}),
                'potential_scenarios': projections.get('potential_scenarios', {}),
                'key_factors': projections.get('key_improvement_areas', [])
            }
        except InsufficientDataError:
            return {'projection_limited': 'Insufficient data for detailed projections'}
    
    def _generate_season_recommendations(self, season_matches):
        recommendations = []
        
        tactical_analysis = self._generate_tactical_analysis_section(season_matches)
        
        if tactical_analysis.get('most_effective_formation') != tactical_analysis.get('preferred_formation'):
            recommendations.append({
                'category': 'Tactical',
                'recommendation': f"Consider using {tactical_analysis['most_effective_formation']} more frequently",
                'rationale': 'Higher win rate than most used formation',
                'priority': 'Medium'
            })
        
        improvement_areas = self._identify_improvement_areas(season_matches)
        for area in improvement_areas[:2]:
            recommendations.append({
                'category': 'Performance',
                'recommendation': f"Focus training on {area['area'].lower()}",
                'rationale': area['concern'],
                'priority': area['priority']
            })
        
        return recommendations
    
    def _generate_match_overview(self, match):
        return {
            'opponent': match.opponent.name,
            'date': match.scheduled_datetime.strftime('%d/%m/%Y'),
            'venue': 'Stamford Bridge' if match.is_home else f'{match.opponent.name} (Away)',
            'competition': match.get_match_type_display(),
            'final_score': f"Chelsea {match.chelsea_score}-{match.opponent_score} {match.opponent.name}",
            'result': match.result,
            'attendance': match.attendance
        }
    
    def _analyze_match_performance(self, match):
        try:
            team_stats = TeamStats.objects.get(match=match)
            player_stats = PlayerStats.objects.filter(match=match)
            
            return {
                'possession': f"{team_stats.possession_percentage}%" if team_stats.possession_percentage else 'N/A',
                'shots_on_target': team_stats.shots_on_target,
                'shots_off_target': team_stats.shots_off_target,
                'corners': team_stats.corners,
                'team_average_rating': round(player_stats.aggregate(avg=Avg('rating'))['avg'] or 0, 2),
                'total_distance_covered': player_stats.aggregate(total=Sum('distance_covered'))['total'] or 0,
                'pass_accuracy': self._calculate_match_pass_accuracy(player_stats)
            }
        except TeamStats.DoesNotExist:
            return {'data_unavailable': True}
    
    def _generate_tactical_breakdown(self, match):
        lineups = MatchLineup.objects.filter(match=match, is_starting_eleven=True)
        
        tactical_info = {
            'formation_used': 'N/A',
            'tactical_approach': 'Standard'
        }
        
        if lineups.exists():
            formation = lineups.first().formation
            tactical_info['formation_used'] = formation.name
            tactical_info['formation_effectiveness'] = self._assess_match_formation_effectiveness(match, formation)
        
        return tactical_info
    
    def _generate_individual_ratings(self, match):
        player_stats = PlayerStats.objects.filter(match=match).select_related('player')
        
        ratings = []
        for stats in player_stats:
            ratings.append({
                'player': stats.player.full_name,
                'position': stats.player.position,
                'minutes_played': stats.minutes_played,
                'rating': float(stats.rating),
                'goals': stats.goals,
                'assists': stats.assists,
                'key_contributions': self._identify_key_contributions(stats)
            })
        
        return sorted(ratings, key=lambda x: x['rating'], reverse=True)
    
    def _analyze_key_moments(self, match):
        events = MatchEvent.objects.filter(match=match).order_by('minute')
        
        key_moments = []
        for event in events:
            if event.event_type in ['GOAL', 'RED_CARD', 'PENALTY']:
                key_moments.append({
                    'minute': event.minute,
                    'event': event.get_event_type_display(),
                    'player': event.player.full_name if event.player else 'Unknown',
                    'description': event.description,
                    'impact': self._assess_moment_impact(event)
                })
        
        return key_moments
    
    def _generate_statistical_breakdown(self, match):
        try:
            team_stats = TeamStats.objects.get(match=match)
            return {
                'shots_total': team_stats.shots_on_target + team_stats.shots_off_target + team_stats.shots_blocked,
                'shots_on_target': team_stats.shots_on_target,
                'shot_accuracy': round((team_stats.shots_on_target / max(1, team_stats.shots_on_target + team_stats.shots_off_target)) * 100, 1),
                'corners': team_stats.corners,
                'offsides': team_stats.offsides,
                'yellow_cards': team_stats.yellow_cards,
                'red_cards': team_stats.red_cards
            }
        except TeamStats.DoesNotExist:
            return {'statistical_data_unavailable': True}
    
    def _compare_with_previous_meetings(self, match):
        previous_meetings = Match.objects.filter(
            opponent=match.opponent,
            scheduled_datetime__lt=match.scheduled_datetime,
            status__in=['COMPLETED', 'FULL_TIME']
        ).order_by('-scheduled_datetime')[:3]
        
        comparisons = []
        for prev_match in previous_meetings:
            comparisons.append({
                'date': prev_match.scheduled_datetime.strftime('%d/%m/%Y'),
                'score': f"{prev_match.chelsea_score}-{prev_match.opponent_score}",
                'result': prev_match.result,
                'venue': 'Home' if prev_match.is_home else 'Away'
            })
        
        return {
            'recent_meetings': comparisons,
            'head_to_head_trend': self._analyze_head_to_head_trend(previous_meetings + [match])
        }
    
    def _extract_lessons_learned(self, match):
        lessons = []
        
        if match.result == 'WIN' and match.chelsea_score >= 3:
            lessons.append("Clinical finishing and multiple goal threats effective")
        
        if match.result == 'LOSS' and match.opponent_score >= 2:
            lessons.append("Defensive vulnerabilities exposed - review required")
        
        try:
            team_stats = TeamStats.objects.get(match=match)
            if team_stats.possession_percentage and team_stats.possession_percentage > 65:
                if match.result != 'WIN':
                    lessons.append("High possession didn't translate to result - improve final third efficiency")
        except TeamStats.DoesNotExist:
            pass
        
        return lessons
    
    def _identify_match_improvement_areas(self, match):
        areas = []
        
        if match.chelsea_score < match.opponent_score:
            areas.append("Attacking efficiency needs improvement")
        
        if match.opponent_score > 2:
            areas.append("Defensive organization requires attention")
        
        return areas
    
    def _generate_player_profile(self, player):
        return {
            'name': player.full_name,
            'position': player.position,
            'age': player.age,
            'squad_number': player.squad_number,
            'height': f"{player.height}cm",
            'preferred_foot': player.get_preferred_foot_display(),
            'market_value': f"£{player.market_value}M",
            'contract_expiry': player.contract_expiry.strftime('%d/%m/%Y'),
            'current_fitness': player.fitness_level,
            'injury_status': 'Injured' if player.is_injured else 'Fit'
        }
    
    def _generate_performance_summary(self, player, player_stats):
        matches_played = player_stats.count()
        
        return {
            'matches_played': matches_played,
            'total_minutes': player_stats.aggregate(total=Sum('minutes_played'))['total'] or 0,
            'average_minutes_per_match': round((player_stats.aggregate(total=Sum('minutes_played'))['total'] or 0) / max(matches_played, 1), 1),
            'goals': player_stats.aggregate(total=Sum('goals'))['total'] or 0,
            'assists': player_stats.aggregate(total=Sum('assists'))['total'] or 0,
            'average_rating': round(player_stats.aggregate(avg=Avg('rating'))['avg'] or 0, 2),
            'best_performance': self._find_best_performance(player_stats),
            'consistency_score': self._calculate_consistency_score(player_stats)
        }
    
    def _analyze_career_progression(self, player):
        try:
            career_analysis = self.career_analyzer.get_career_overview(player)
            return {
                'career_matches': career_analysis['career_statistics']['total_matches'],
                'career_goals': career_analysis['career_statistics']['total_goals'],
                'career_rating': career_analysis['career_statistics']['average_rating'],
                'development_trajectory': career_analysis['development_trajectory']['overall_progression'],
                'career_highlights': career_analysis['career_highlights']
            }
        except (InsufficientDataError, KeyError):
            return {'insufficient_career_data': True}
    
    def _analyze_development_trends(self, player, player_stats):
        try:
            trends = self.trend_analyzer.analyze_player_development_trends(player)
            return {
                'performance_trajectory': trends.get('performance_trajectory', {}),
                'skill_development': trends.get('skill_development_areas', {}),
                'consistency_trends': trends.get('consistency_trends', {}),
                'development_velocity': trends.get('development_velocity', {})
            }
        except InsufficientDataError:
            return {'insufficient_trend_data': True}
    
    def _identify_player_strengths_weaknesses(self, player_stats):
        stats_summary = player_stats.aggregate(
            avg_goals=Avg('goals'),
            avg_assists=Avg('assists'),
            avg_tackles=Avg('tackles'),
            avg_passes_completed=Avg('passes_completed'),
            avg_passes_attempted=Avg('passes_attempted'),
            avg_rating=Avg('rating')
        )
        
        strengths = []
        weaknesses = []
        
        if (stats_summary['avg_goals'] or 0) > 0.5:
            strengths.append("Consistent goal scoring threat")
        elif (stats_summary['avg_goals'] or 0) < 0.1:
            weaknesses.append("Limited goal scoring output")
        
        if (stats_summary['avg_assists'] or 0) > 0.3:
            strengths.append("Good creative contribution")
        
        pass_accuracy = 0
        if stats_summary['avg_passes_attempted'] and stats_summary['avg_passes_attempted'] > 0:
            pass_accuracy = (stats_summary['avg_passes_completed'] / stats_summary['avg_passes_attempted']) * 100
        
        if pass_accuracy > 85:
            strengths.append("Excellent passing accuracy")
        elif pass_accuracy < 75:
            weaknesses.append("Passing accuracy needs improvement")
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'overall_assessment': 'Positive' if len(strengths) > len(weaknesses) else 'Areas for improvement'
        }
    
    def _analyze_player_consistency(self, player_stats):
        ratings = [float(stat.rating) for stat in player_stats]
        
        if len(ratings) < 3:
            return {'insufficient_data': True}
        
        mean_rating = sum(ratings) / len(ratings)
        variance = sum((r - mean_rating) ** 2 for r in ratings) / len(ratings)
        std_deviation = variance ** 0.5
        
        consistency_score = max(0, 100 - (std_deviation * 20))
        
        performances_above_7 = len([r for r in ratings if r >= 7.0])
        reliability_rate = (performances_above_7 / len(ratings)) * 100
        
        return {
            'consistency_score': round(consistency_score, 1),
            'reliability_rate': round(reliability_rate, 1),
            'performance_variance': round(std_deviation, 2),
            'assessment': 'Highly consistent' if consistency_score > 80 else 'Moderately consistent' if consistency_score > 60 else 'Inconsistent'
        }
    
    def _generate_comparative_analysis(self, player):
        position_peers = Player.objects.filter(position=player.position, is_active=True).exclude(id=player.id)
        
        if position_peers.exists():
            comparison_player = position_peers.first()
            try:
                comparison = self.comparison_engine.compare_players(player, comparison_player)
                return {
                    'compared_with': comparison_player.full_name,
                    'comparison_summary': comparison.get('head_to_head_metrics', {}),
                    'position_ranking': 'Data available'
                }
            except (InsufficientDataError, ValidationError):
                return {'comparison_unavailable': True}
        
        return {'no_position_peers': True}
    
    def _assess_future_potential(self, player, player_stats):
        age = player.age
        recent_trend = self._calculate_recent_performance_trend(player_stats)
        
        if age < 21:
            potential = 'Very High' if recent_trend > 0.2 else 'High'
        elif age < 25:
            potential = 'High' if recent_trend > 0.1 else 'Medium' if recent_trend > -0.1 else 'Moderate'
        elif age < 29:
            potential = 'Medium' if recent_trend >= 0 else 'Limited'
        else:
            potential = 'Maintenance phase'
        
        return {
            'potential_rating': potential,
            'age_factor': age,
            'development_trend': 'Positive' if recent_trend > 0 else 'Stable' if recent_trend > -0.1 else 'Concerning'
        }
    
    def _generate_development_recommendations(self, player, player_stats):
        recommendations = []
        
        strengths_weaknesses = self._identify_player_strengths_weaknesses(player_stats)
        
        for weakness in strengths_weaknesses['weaknesses']:
            if 'goal scoring' in weakness.lower():
                recommendations.append({
                    'area': 'Attacking Training',
                    'recommendation': 'Focus on finishing drills and positioning in penalty area'
                })
            elif 'passing' in weakness.lower():
                recommendations.append({
                    'area': 'Technical Skills',
                    'recommendation': 'Improve passing accuracy through dedicated training sessions'
                })
        
        consistency_analysis = self._analyze_player_consistency(player_stats)
        if not consistency_analysis.get('insufficient_data') and consistency_analysis['consistency_score'] < 70:
            recommendations.append({
                'area': 'Mental Preparation',
                'recommendation': 'Work on maintaining consistent performance levels through mental conditioning'
            })
        
        return recommendations
    
    def _assess_season_performance(self, win_rate, goals_scored, goals_conceded, total_matches):
        if win_rate > 70:
            return 'Excellent season performance'
        elif win_rate > 60:
            return 'Good season performance with room for improvement'
        elif win_rate > 50:
            return 'Average season performance'
        else:
            return 'Below expectations - significant improvement needed'
    
    def _calculate_home_away_record(self, matches, is_home):
        filtered_matches = matches.filter(is_home=is_home)
        total = filtered_matches.count()
        
        if total == 0:
            return {'matches': 0, 'record': 'N/A'}
        
        wins = filtered_matches.filter(result='WIN').count()
        draws = filtered_matches.filter(result='DRAW').count()
        losses = filtered_matches.filter(result='LOSS').count()
        
        return {
            'matches': total,
            'record': f'{wins}W-{draws}D-{losses}L',
            'win_rate': round((wins / total) * 100, 1)
        }
    
    def _calculate_player_contribution_rating(self, player_stats):
        matches = player_stats.count()
        if matches == 0:
            return 0
        
        goals = player_stats.aggregate(total=Sum('goals'))['total'] or 0
        assists = player_stats.aggregate(total=Sum('assists'))['total'] or 0
        avg_rating = player_stats.aggregate(avg=Avg('rating'))['avg'] or 0
        
        contribution_score = (goals * 3) + (assists * 2) + (avg_rating * matches * 0.5)
        return round(contribution_score, 2)
    
    def _calculate_formation_effectiveness_score(self, formation_matches):
        total_matches = formation_matches.count()
        if total_matches == 0:
            return 0
        
        wins = formation_matches.filter(result='WIN').count()
        draws = formation_matches.filter(result='DRAW').count()
        
        points = (wins * 3) + draws
        points_per_match = points / total_matches
        
        return round((points_per_match / 3) * 100, 1)
    
    def _get_formation_best_results(self, formation_matches):
        best_results = []
        
        for match in formation_matches.filter(result='WIN').order_by('-chelsea_score')[:3]:
            best_results.append({
                'opponent': match.opponent.name,
                'score': f"{match.chelsea_score}-{match.opponent_score}",
                'date': match.scheduled_datetime.strftime('%d/%m/%Y')
            })
        
        return best_results
    
    def _assess_formation_suitability(self, formation, formation_matches):
        effectiveness_score = self._calculate_formation_effectiveness_score(formation_matches)
        
        if effectiveness_score > 75:
            return 'Highly suitable'
        elif effectiveness_score > 60:
            return 'Suitable'
        elif effectiveness_score > 45:
            return 'Moderately suitable'
        else:
            return 'Needs review'
    
    def _identify_challenging_opponents(self, opponent_records):
        challenging = []
        
        for opponent, record in opponent_records.items():
            win_rate = (record['wins'] / record['matches']) * 100 if record['matches'] > 0 else 0
            
            if win_rate < 50 and record['matches'] >= 2:
                challenging.append({
                    'opponent': opponent,
                    'record': f"{record['wins']}W-{record['draws']}D-{record['losses']}L",
                    'win_rate': round(win_rate, 1)
                })
        
        return sorted(challenging, key=lambda x: x['win_rate'])[:5]
    
    def _identify_best_results(self, opponent_records):
        best = []
        
        for opponent, record in opponent_records.items():
            if record['wins'] > 0:
                goal_difference = record['goals_scored'] - record['goals_conceded']
                best.append({
                    'opponent': opponent,
                    'wins': record['wins'],
                    'goal_difference': goal_difference
                })
        
        return sorted(best, key=lambda x: (x['wins'], x['goal_difference']), reverse=True)[:5]
    
    def _find_biggest_win(self, matches):
        biggest_win = None
        max_margin = 0
        
        for match in matches.filter(result='WIN'):
            margin = match.chelsea_score - match.opponent_score
            if margin > max_margin:
                max_margin = margin
                biggest_win = f"{match.chelsea_score}-{match.opponent_score} vs {match.opponent.name}"
        
        return biggest_win or 'N/A'
    
    def _find_biggest_loss(self, matches):
        biggest_loss = None
        max_margin = 0
        
        for match in matches.filter(result='LOSS'):
            margin = match.opponent_score - match.chelsea_score
            if margin > max_margin:
                max_margin = margin
                biggest_loss = f"{match.chelsea_score}-{match.opponent_score} vs {match.opponent.name}"
        
        return biggest_loss or 'N/A'
    
    def _find_highest_scoring_match(self, matches):
        highest_scoring = None
        max_goals = 0
        
        for match in matches:
            total_goals = match.chelsea_score + match.opponent_score
            if total_goals > max_goals:
                max_goals = total_goals
                highest_scoring = f"{match.chelsea_score}-{match.opponent_score} vs {match.opponent.name}"
        
        return highest_scoring or 'N/A'
    
    def _calculate_match_pass_accuracy(self, player_stats):
        total_completed = player_stats.aggregate(total=Sum('passes_completed'))['total'] or 0
        total_attempted = player_stats.aggregate(total=Sum('passes_attempted'))['total'] or 0
        
        if total_attempted == 0:
            return 0
        
        return round((total_completed / total_attempted) * 100, 1)
    
    def _assess_match_formation_effectiveness(self, match, formation):
        if match.result == 'WIN':
            return 'Highly effective'
        elif match.result == 'DRAW':
            return 'Moderately effective'
        else:
            return 'Ineffective'
    
    def _identify_key_contributions(self, stats):
        contributions = []
        
        if stats.goals > 0:
            contributions.append(f"{stats.goals} goal{'s' if stats.goals > 1 else ''}")
        if stats.assists > 0:
            contributions.append(f"{stats.assists} assist{'s' if stats.assists > 1 else ''}")
        if stats.tackles > 3:
            contributions.append(f"{stats.tackles} tackles")
        
        return contributions
    
    def _assess_moment_impact(self, event):
        if event.event_type == 'GOAL':
            return 'High - Changed scoreline'
        elif event.event_type == 'RED_CARD':
            return 'Very High - Numerical disadvantage'
        elif event.event_type == 'PENALTY':
            return 'High - Penalty situation'
        else:
            return 'Medium'
    
    def _analyze_head_to_head_trend(self, matches):
        if len(matches) < 3:
            return 'Insufficient data'
        
        recent_results = [match.result for match in matches[-3:]]
        wins = recent_results.count('WIN')
        
        if wins >= 2:
            return 'Positive trend'
        elif wins == 0:
            return 'Concerning trend'
        else:
            return 'Mixed results'
    
    def _find_best_performance(self, player_stats):
        best = player_stats.order_by('-rating').first()
        
        if best:
            return {
                'rating': float(best.rating),
                'opponent': best.match.opponent.name,
                'date': best.match.scheduled_datetime.strftime('%d/%m/%Y'),
                'goals': best.goals,
                'assists': best.assists
            }
        
        return None
    
    def _calculate_consistency_score(self, player_stats):
        ratings = [float(stat.rating) for stat in player_stats]
        
        if len(ratings) < 3:
            return 0
        
        mean_rating = sum(ratings) / len(ratings)
        variance = sum((r - mean_rating) ** 2 for r in ratings) / len(ratings)
        std_deviation = variance ** 0.5
        
        consistency_score = max(0, 100 - (std_deviation * 20))
        return round(consistency_score, 1)
    
    def _calculate_recent_performance_trend(self, player_stats):
        recent_ratings = [float(stat.rating) for stat in player_stats.order_by('-match__scheduled_datetime')[:5]]
        
        if len(recent_ratings) < 3:
            return 0
        
        recent_avg = sum(recent_ratings[:3]) / 3
        earlier_avg = sum(recent_ratings[-3:]) / len(recent_ratings[-3:])
        
        return recent_avg - earlier_avg
    
    def _generate_opponent_overview(self, opponent):
        return {
            'name': opponent.name,
            'league': opponent.league,
            'country': opponent.country,
            'typical_formation': opponent.typical_formation,
            'playing_style': opponent.playing_style
        }
    
    def _analyze_historical_record(self, opponent, matches):
        if not matches.exists():
            return {'insufficient_historical_data': True}
        
        total = matches.count()
        wins = matches.filter(result='WIN').count()
        draws = matches.filter(result='DRAW').count()
        losses = matches.filter(result='LOSS').count()
        
        return {
            'total_meetings': total,
            'chelsea_wins': wins,
            'draws': draws,
            'chelsea_losses': losses,
            'chelsea_win_rate': round((wins / total) * 100, 1),
            'last_meeting': self._get_last_meeting_info(matches)
        }
    
    def _analyze_recent_form(self, opponent):
        return {
            'note': 'Recent form analysis would require external data sources',
            'recommendation': 'Monitor opponent recent matches through scouting reports'
        }
    
    def _generate_tactical_expectations(self, opponent, matches):
        expectations = {
            'expected_formation': opponent.typical_formation,
            'playing_style': opponent.playing_style
        }
        
        if matches.exists():
            avg_goals_against = sum(match.opponent_score for match in matches) / matches.count()
            expectations['attacking_threat'] = 'High' if avg_goals_against > 1.5 else 'Medium' if avg_goals_against > 0.8 else 'Low'
        
        return expectations
    
    def _identify_key_threats(self, opponent, matches):
        return {
            'note': 'Key player threat analysis requires detailed opponent squad data',
            'recommendation': 'Focus scouting on opponent key players and recent performances'
        }
    
    def _predict_opponent_lineup(self, opponent):
        return {
            'predicted_formation': opponent.typical_formation,
            'note': 'Detailed lineup prediction requires current squad and injury information'
        }
    
    def _generate_match_prediction(self, opponent, formation):
        try:
            prediction = self.prediction_models.predict_match_outcome(opponent, formation)
            return {
                'predicted_result': prediction.get('predicted_outcome', {}),
                'predicted_score': prediction.get('predicted_scoreline', {}),
                'confidence': prediction.get('prediction_confidence', 0)
            }
        except (InsufficientDataError, ValidationError):
            return {'prediction_unavailable': 'Insufficient data for prediction'}
    
    def _generate_tactical_preparation_guide(self, opponent, formation):
        guide = []
        
        if opponent.typical_formation:
            guide.append(f"Prepare for {opponent.typical_formation} formation")
        
        if 'attacking' in opponent.playing_style.lower():
            guide.append("Focus on defensive organization and transition speed")
        elif 'defensive' in opponent.playing_style.lower():
            guide.append("Emphasize patient build-up and creating space")
        
        return guide
    
    def _generate_set_piece_preparation(self, opponent, matches):
        return {
            'defensive_set_pieces': 'Review opponent corner and free-kick routines',
            'attacking_set_pieces': 'Identify potential weaknesses in opponent set-piece defending'
        }
    
    def _identify_key_focus_areas(self, opponent, matches):
        focus_areas = ['Maintain tactical discipline', 'Execute game plan effectively']
        
        if matches.exists():
            recent_losses = matches.filter(result='LOSS').count()
            if recent_losses > matches.count() * 0.4:
                focus_areas.append('Address historical weaknesses against this opponent')
        
        return focus_areas
    
    def _get_last_meeting_info(self, matches):
        last_match = matches.order_by('-scheduled_datetime').first()
        
        if last_match:
            return {
                'date': last_match.scheduled_datetime.strftime('%d/%m/%Y'),
                'score': f"{last_match.chelsea_score}-{last_match.opponent_score}",
                'result': last_match.result,
                'venue': 'Home' if last_match.is_home else 'Away'
            }
        
        return None
    
    def _generate_monthly_summary(self, matches):
        if not matches.exists():
            return {'no_matches': 'No matches played in this period'}
        
        total = matches.count()
        wins = matches.filter(result='WIN').count()
        draws = matches.filter(result='DRAW').count()
        losses = matches.filter(result='LOSS').count()
        
        return {
            'matches_played': total,
            'record': f'{wins}W-{draws}D-{losses}L',
            'win_rate': round((wins / total) * 100, 1),
            'points_earned': (wins * 3) + draws,
            'goals_scored': sum(match.chelsea_score for match in matches),
            'goals_conceded': sum(match.opponent_score for match in matches)
        }
    
    def _identify_monthly_highlights(self, matches):
        highlights = []
        
        best_win = None
        max_margin = 0
        
        for match in matches.filter(result='WIN'):
            margin = match.chelsea_score - match.opponent_score
            if margin > max_margin:
                max_margin = margin
                best_win = match
        
        if best_win:
            highlights.append(f"Best result: {best_win.chelsea_score}-{best_win.opponent_score} vs {best_win.opponent.name}")
        
        return highlights
    
    def _generate_monthly_statistics(self, matches):
        if not matches.exists():
            return {}
        
        return {
            'total_goals': sum(match.chelsea_score for match in matches),
            'total_conceded': sum(match.opponent_score for match in matches),
            'clean_sheets': matches.filter(opponent_score=0).count(),
            'failed_to_score': matches.filter(chelsea_score=0).count(),
            'average_goals_per_match': round(sum(match.chelsea_score for match in matches) / matches.count(), 2),
            'average_conceded_per_match': round(sum(match.opponent_score for match in matches) / matches.count(), 2)
        }
    
    def _identify_player_of_month(self, matches):
        player_performances = {}
        
        for match in matches:
            player_stats = PlayerStats.objects.filter(match=match)
            
            for stats in player_stats:
                player_name = stats.player.full_name
                
                if player_name not in player_performances:
                    player_performances[player_name] = {
                        'matches': 0,
                        'total_rating': 0,
                        'goals': 0,
                        'assists': 0
                    }
                
                player_performances[player_name]['matches'] += 1
                player_performances[player_name]['total_rating'] += float(stats.rating)
                player_performances[player_name]['goals'] += stats.goals
                player_performances[player_name]['assists'] += stats.assists
        
        best_player = None
        best_score = 0
        
        for player, performance in player_performances.items():
            if performance['matches'] >= 2:
                avg_rating = performance['total_rating'] / performance['matches']
                contribution_score = avg_rating + (performance['goals'] * 0.5) + (performance['assists'] * 0.3)
                
                if contribution_score > best_score:
                    best_score = contribution_score
                    best_player = {
                        'player': player,
                        'average_rating': round(avg_rating, 2),
                        'goals': performance['goals'],
                        'assists': performance['assists'],
                        'matches': performance['matches']
                    }
        
        return best_player
    
    def _review_monthly_tactics(self, matches):
        formation_usage = {}
        
        for match in matches:
            lineups = MatchLineup.objects.filter(match=match, is_starting_eleven=True)
            
            for lineup in lineups:
                formation = lineup.formation.name
                
                if formation not in formation_usage:
                    formation_usage[formation] = {'matches': 0, 'wins': 0}
                
                formation_usage[formation]['matches'] += 1
                if match.result == 'WIN':
                    formation_usage[formation]['wins'] += 1
        
        return {
            'formations_used': formation_usage,
            'most_successful_formation': max(formation_usage.items(), 
                                           key=lambda x: x[1]['wins'] / x[1]['matches'] if x[1]['matches'] > 0 else 0)[0] 
                                           if formation_usage else 'N/A'
        }
    
    def _identify_monthly_improvements(self, matches):
        improvements = []
        
        if matches.exists():
            total_goals = sum(match.chelsea_score for match in matches)
            avg_goals = total_goals / matches.count()
            
            if avg_goals < 2.0:
                improvements.append("Increase attacking output and chance conversion")
            
            total_conceded = sum(match.opponent_score for match in matches)
            avg_conceded = total_conceded / matches.count()
            
            if avg_conceded > 1.5:
                improvements.append("Strengthen defensive solidity")
        
        return improvements
    
    def _assess_monthly_objectives(self, matches):
        return {
            'note': 'Monthly objectives assessment requires predefined targets',
            'recommendation': 'Set specific monthly targets for wins, goals, and defensive record'
        }
    
    def _generate_forward_outlook(self):
        return {
            'next_month_focus': ['Maintain current form', 'Address identified weaknesses', 'Build on strengths'],
            'preparation_priorities': ['Squad fitness', 'Tactical cohesion', 'Mental preparation']
        }