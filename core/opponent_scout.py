from django.db.models import Q, Avg, Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging

from .models import Opponent, Match, TeamStats, PlayerStats, Formation, MatchLineup
from .exceptions import ValidationError, InsufficientDataError

logger = logging.getLogger('core.performance')

class OpponentScout:
    
    def __init__(self):
        self.logger = logging.getLogger('core.performance')
        self.analysis_period_days = 365
    
    def generate_report(self, opponent):
        if not isinstance(opponent, Opponent):
            raise ValidationError("Invalid opponent object provided")
        
        recent_matches = self._get_historical_matches(opponent)
        
        if not recent_matches.exists():
            return self._generate_limited_report(opponent)
        
        report = {
            'opponent_info': self._extract_opponent_info(opponent),
            'historical_record': self._analyze_historical_record(opponent, recent_matches),
            'tactical_analysis': self._analyze_opponent_tactics(recent_matches),
            'key_players_analysis': self._analyze_key_threats(recent_matches),
            'playing_style_assessment': self._assess_playing_style(recent_matches),
            'strengths_and_weaknesses': self._identify_strengths_weaknesses(recent_matches),
            'tactical_recommendations': self._generate_tactical_recommendations(opponent, recent_matches),
            'recent_form_analysis': self._analyze_recent_form(recent_matches),
            'head_to_head_insights': self._analyze_head_to_head(opponent),
            'preparation_suggestions': self._generate_preparation_suggestions(opponent, recent_matches)
        }
        
        self.logger.info(f"Scout report generated for {opponent.name}: {recent_matches.count()} matches analyzed")
        return report
    
    def _get_historical_matches(self, opponent):
        cutoff_date = timezone.now() - timedelta(days=self.analysis_period_days)
        
        return Match.objects.filter(
            opponent=opponent,
            scheduled_datetime__gte=cutoff_date,
            status__in=['COMPLETED', 'FULL_TIME']
        ).order_by('-scheduled_datetime')
    
    def _extract_opponent_info(self, opponent):
        return {
            'name': opponent.name,
            'league': opponent.league,
            'country': opponent.country,
            'typical_formation': opponent.typical_formation,
            'known_playing_style': opponent.playing_style,
            'analysis_period': self.analysis_period_days
        }
    
    def _analyze_historical_record(self, opponent, matches):
        total_matches = matches.count()
        wins = matches.filter(result='LOSS').count()
        draws = matches.filter(result='DRAW').count()
        losses = matches.filter(result='WIN').count()
        
        goals_scored = sum(match.opponent_score for match in matches)
        goals_conceded = sum(match.chelsea_score for match in matches)
        
        return {
            'total_matches': total_matches,
            'opponent_wins': wins,
            'draws': draws,
            'opponent_losses': losses,
            'opponent_win_rate': round((wins / total_matches * 100), 2) if total_matches > 0 else 0,
            'goals_scored_avg': round(goals_scored / total_matches, 2) if total_matches > 0 else 0,
            'goals_conceded_avg': round(goals_conceded / total_matches, 2) if total_matches > 0 else 0,
            'goal_difference_avg': round((goals_scored - goals_conceded) / total_matches, 2) if total_matches > 0 else 0,
            'clean_sheets': matches.filter(opponent_score=0).count(),
            'high_scoring_games': matches.filter(opponent_score__gte=3).count()
        }
    
    def _analyze_opponent_tactics(self, matches):
        formations_used = {}
        tactical_patterns = {
            'high_possession_games': 0,
            'defensive_setups': 0,
            'attacking_displays': 0,
            'counter_attack_preference': 0
        }
        
        for match in matches:
            try:
                team_stats = TeamStats.objects.get(match=match)
                
                opponent_possession = 100 - float(team_stats.possession_percentage or 50)
                
                if opponent_possession > 60:
                    tactical_patterns['high_possession_games'] += 1
                elif opponent_possession < 40:
                    tactical_patterns['defensive_setups'] += 1
                
                if match.opponent_score >= 3:
                    tactical_patterns['attacking_displays'] += 1
                
                if opponent_possession < 45 and match.opponent_score >= 2:
                    tactical_patterns['counter_attack_preference'] += 1
                    
            except TeamStats.DoesNotExist:
                continue
        
        total_analyzed = max(1, sum(tactical_patterns.values()))
        
        return {
            'formations_preference': formations_used,
            'tactical_tendencies': {
                pattern: round((count / matches.count() * 100), 2)
                for pattern, count in tactical_patterns.items()
            },
            'primary_approach': self._determine_primary_tactical_approach(tactical_patterns)
        }
    
    def _analyze_key_threats(self, matches):
        goal_threats = {}
        creative_threats = {}
        
        for match in matches:
            player_stats = PlayerStats.objects.filter(match=match)
            
            for stat in player_stats:
                player_name = stat.player.full_name
                
                if stat.goals > 0:
                    goal_threats[player_name] = goal_threats.get(player_name, 0) + stat.goals
                
                if stat.assists > 0:
                    creative_threats[player_name] = creative_threats.get(player_name, 0) + stat.assists
        
        top_goal_threats = sorted(goal_threats.items(), key=lambda x: x[1], reverse=True)[:5]
        top_creative_threats = sorted(creative_threats.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'primary_goal_threats': [
                {'player': name, 'goals': goals} for name, goals in top_goal_threats
            ],
            'primary_creative_threats': [
                {'player': name, 'assists': assists} for name, assists in top_creative_threats
            ],
            'threat_assessment': self._assess_threat_level(top_goal_threats, top_creative_threats)
        }
    
    def _assess_playing_style(self, matches):
        style_indicators = {
            'possession_based': 0,
            'direct_play': 0,
            'counter_attacking': 0,
            'defensive_solidity': 0,
            'high_tempo': 0
        }
        
        analyzed_matches = 0
        
        for match in matches:
            try:
                team_stats = TeamStats.objects.get(match=match)
                opponent_possession = 100 - float(team_stats.possession_percentage or 50)
                
                if opponent_possession > 55:
                    style_indicators['possession_based'] += 1
                elif opponent_possession < 40:
                    style_indicators['counter_attacking'] += 1
                else:
                    style_indicators['direct_play'] += 1
                
                if match.opponent_score == 0:
                    style_indicators['defensive_solidity'] += 1
                
                if match.opponent_score >= 2 and opponent_possession < 50:
                    style_indicators['high_tempo'] += 1
                
                analyzed_matches += 1
                
            except TeamStats.DoesNotExist:
                continue
        
        if analyzed_matches == 0:
            return {'insufficient_data': True}
        
        dominant_style = max(style_indicators.items(), key=lambda x: x[1])
        
        return {
            'style_breakdown': {
                style: round((count / analyzed_matches * 100), 2)
                for style, count in style_indicators.items()
            },
            'dominant_style': dominant_style[0],
            'style_consistency': round((dominant_style[1] / analyzed_matches * 100), 2)
        }
    
    def _identify_strengths_weaknesses(self, matches):
        strengths = []
        weaknesses = []
        
        total_matches = matches.count()
        high_scoring = matches.filter(opponent_score__gte=3).count()
        clean_sheets_against = matches.filter(chelsea_score=0).count()
        conceded_multiple = matches.filter(chelsea_score__gte=2).count()
        
        if (high_scoring / total_matches) > 0.4:
            strengths.append("Strong attacking threat - regularly scores multiple goals")
        
        if (clean_sheets_against / total_matches) > 0.3:
            strengths.append("Solid defensive organization - capable of shutting out attacks")
        
        if (conceded_multiple / total_matches) > 0.5:
            weaknesses.append("Defensive vulnerabilities - tends to concede multiple goals")
        
        possession_analysis = self._analyze_possession_patterns(matches)
        if possession_analysis['avg_possession'] > 60:
            strengths.append("Excellent ball retention and possession control")
        elif possession_analysis['avg_possession'] < 40:
            weaknesses.append("Struggles to maintain possession against quality opposition")
        
        return {
            'identified_strengths': strengths,
            'identified_weaknesses': weaknesses,
            'key_statistics': {
                'high_scoring_rate': round((high_scoring / total_matches * 100), 2),
                'clean_sheet_rate': round((clean_sheets_against / total_matches * 100), 2),
                'defensive_fragility_rate': round((conceded_multiple / total_matches * 100), 2)
            }
        }
    
    def _generate_tactical_recommendations(self, opponent, matches):
        recommendations = []
        
        playing_style = self._assess_playing_style(matches)
        if not playing_style.get('insufficient_data'):
            dominant_style = playing_style.get('dominant_style', '')
            
            if dominant_style == 'possession_based':
                recommendations.append({
                    'area': 'Pressing Strategy',
                    'recommendation': 'Implement high-intensity pressing to disrupt their build-up play',
                    'priority': 'High'
                })
                recommendations.append({
                    'area': 'Formation',
                    'recommendation': 'Consider compact midfield to limit space between lines',
                    'priority': 'Medium'
                })
            
            elif dominant_style == 'counter_attacking':
                recommendations.append({
                    'area': 'Defensive Shape',
                    'recommendation': 'Maintain high defensive line to prevent counter-attack space',
                    'priority': 'High'
                })
                recommendations.append({
                    'area': 'Ball Retention',
                    'recommendation': 'Focus on maintaining possession to limit counter opportunities',
                    'priority': 'High'
                })
        
        historical_record = self._analyze_historical_record(opponent, matches)
        if historical_record['goals_scored_avg'] > 2:
            recommendations.append({
                'area': 'Defensive Preparation',
                'recommendation': 'Extra attention to defensive set pieces and transition moments',
                'priority': 'High'
            })
        
        if opponent.typical_formation in ['4-3-3', '3-4-3']:
            recommendations.append({
                'area': 'Wide Areas',
                'recommendation': 'Strengthen wide defensive coverage to limit crossing opportunities',
                'priority': 'Medium'
            })
        
        return recommendations
    
    def _analyze_recent_form(self, matches):
        recent_five = matches[:5]
        
        if recent_five.count() < 3:
            return {'insufficient_recent_data': True}
        
        recent_wins = recent_five.filter(result='LOSS').count()
        recent_goals = sum(match.opponent_score for match in recent_five)
        recent_conceded = sum(match.chelsea_score for match in recent_five)
        
        form_trend = 'improving' if recent_wins >= 3 else 'declining' if recent_wins == 0 else 'mixed'
        
        return {
            'recent_matches_analyzed': recent_five.count(),
            'recent_wins': recent_wins,
            'recent_goals_per_game': round(recent_goals / recent_five.count(), 2),
            'recent_goals_conceded_per_game': round(recent_conceded / recent_five.count(), 2),
            'form_trend': form_trend,
            'momentum_assessment': self._assess_momentum(recent_five)
        }
    
    def _analyze_head_to_head(self, opponent):
        all_time_matches = Match.objects.filter(opponent=opponent, status__in=['COMPLETED', 'FULL_TIME'])
        
        if all_time_matches.count() < 5:
            return {'insufficient_historical_data': True}
        
        total = all_time_matches.count()
        chelsea_wins = all_time_matches.filter(result='WIN').count()
        draws = all_time_matches.filter(result='DRAW').count()
        chelsea_losses = all_time_matches.filter(result='LOSS').count()
        
        recent_trend = all_time_matches.order_by('-scheduled_datetime')[:5]
        recent_chelsea_wins = recent_trend.filter(result='WIN').count()
        
        return {
            'all_time_record': {
                'total_matches': total,
                'chelsea_wins': chelsea_wins,
                'draws': draws,
                'chelsea_losses': chelsea_losses,
                'chelsea_win_percentage': round((chelsea_wins / total * 100), 2)
            },
            'recent_head_to_head': {
                'last_five_chelsea_wins': recent_chelsea_wins,
                'recent_trend': 'favorable' if recent_chelsea_wins >= 3 else 'concerning' if recent_chelsea_wins <= 1 else 'balanced'
            },
            'psychological_advantage': 'Chelsea' if chelsea_wins > chelsea_losses else 'Opponent' if chelsea_losses > chelsea_wins else 'Neutral'
        }
    
    def _generate_preparation_suggestions(self, opponent, matches):
        suggestions = []
        
        suggestions.append({
            'category': 'Video Analysis',
            'suggestion': f'Focus on {opponent.name} recent matches, particularly their {opponent.typical_formation} setup',
            'priority': 'High'
        })
        
        key_threats = self._analyze_key_threats(matches)
        if key_threats['primary_goal_threats']:
            top_threat = key_threats['primary_goal_threats'][0]
            suggestions.append({
                'category': 'Individual Marking',
                'suggestion': f'Special attention to {top_threat["player"]} - primary goal threat',
                'priority': 'High'
            })
        
        playing_style = self._assess_playing_style(matches)
        if not playing_style.get('insufficient_data'):
            if playing_style['dominant_style'] == 'possession_based':
                suggestions.append({
                    'category': 'Training Focus',
                    'suggestion': 'Practice pressing triggers and coordinated team pressing',
                    'priority': 'Medium'
                })
        
        suggestions.append({
            'category': 'Set Pieces',
            'suggestion': 'Review defensive and attacking set piece routines against this opposition',
            'priority': 'Medium'
        })
        
        return suggestions
    
    def _generate_limited_report(self, opponent):
        return {
            'opponent_info': self._extract_opponent_info(opponent),
            'data_limitation': 'Limited historical data available for comprehensive analysis',
            'basic_information': {
                'known_formation': opponent.typical_formation,
                'playing_style': opponent.playing_style,
                'league': opponent.league
            },
            'preparation_focus': [
                'Research recent matches from external sources',
                'Focus on tactical preparation based on known formation',
                'Prepare for multiple tactical scenarios'
            ]
        }
    
    def _determine_primary_tactical_approach(self, patterns):
        max_pattern = max(patterns.items(), key=lambda x: x[1])
        
        approach_map = {
            'high_possession_games': 'Possession-based control',
            'defensive_setups': 'Defensive solidity',
            'attacking_displays': 'Attacking intent',
            'counter_attack_preference': 'Counter-attacking'
        }
        
        return approach_map.get(max_pattern[0], 'Balanced approach')
    
    def _assess_threat_level(self, goal_threats, creative_threats):
        total_goals = sum(goals for _, goals in goal_threats)
        total_assists = sum(assists for _, assists in creative_threats)
        
        if total_goals > 15 or total_assists > 10:
            return 'High - Multiple consistent threats'
        elif total_goals > 8 or total_assists > 5:
            return 'Medium - Some dangerous players'
        else:
            return 'Low - Limited individual threats'
    
    def _analyze_possession_patterns(self, matches):
        possession_values = []
        
        for match in matches:
            try:
                team_stats = TeamStats.objects.get(match=match)
                opponent_possession = 100 - float(team_stats.possession_percentage or 50)
                possession_values.append(opponent_possession)
            except TeamStats.DoesNotExist:
                continue
        
        if not possession_values:
            return {'avg_possession': 50, 'consistency': 'Unknown'}
        
        avg_possession = sum(possession_values) / len(possession_values)
        variance = sum((x - avg_possession) ** 2 for x in possession_values) / len(possession_values)
        consistency = 'High' if variance < 100 else 'Medium' if variance < 225 else 'Low'
        
        return {
            'avg_possession': round(avg_possession, 2),
            'consistency': consistency
        }
    
    def _assess_momentum(self, recent_matches):
        if recent_matches.count() < 3:
            return 'Insufficient data'
        
        results = [match.result for match in recent_matches]
        opponent_results = ['WIN' if r == 'LOSS' else 'LOSS' if r == 'WIN' else 'DRAW' for r in results]
        
        recent_wins = opponent_results.count('WIN')
        
        if recent_wins >= 4:
            return 'Very positive - on strong winning run'
        elif recent_wins >= 2:
            return 'Positive - good recent form'
        elif recent_wins == 1:
            return 'Mixed - inconsistent results'
        else:
            return 'Negative - struggling for wins'