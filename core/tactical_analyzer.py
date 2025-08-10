from django.db.models import Q, Avg, Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging

from .models import Formation, Match, PlayerStats, TeamStats, MatchLineup, MatchEvent, Player, Opponent

logger = logging.getLogger('core.performance')

class TacticalAnalyzer:
    
    def __init__(self):
        self.logger = logging.getLogger('core.performance')
        self.analysis_period_days = 90
    
    def analyze_formation_effectiveness(self, formation, period_days=None):
        if period_days is None:
            period_days = self.analysis_period_days
        
        cutoff_date = timezone.now() - timedelta(days=period_days)
        
        formation_matches = self._get_formation_matches(formation, cutoff_date)
        
        if not formation_matches:
            return self._empty_formation_analysis(formation)
        
        effectiveness_data = {
            'formation_name': formation.name,
            'analysis_period': period_days,
            'total_matches': len(formation_matches),
            'tactical_metrics': self._calculate_tactical_metrics(formation_matches),
            'performance_analysis': self._analyze_formation_performance(formation_matches),
            'opposition_analysis': self._analyze_against_opposition_styles(formation, formation_matches),
            'player_utilisation': self._analyze_player_utilisation(formation, formation_matches),
            'tactical_flexibility': self._assess_tactical_flexibility(formation, formation_matches),
            'recommendations': []
        }
        
        effectiveness_data['recommendations'] = self._generate_tactical_recommendations(effectiveness_data)
        
        self.logger.info(f"Tactical analysis completed for formation {formation.name}")
        return effectiveness_data
    
    def _get_formation_matches(self, formation, cutoff_date):
        lineups = MatchLineup.objects.filter(
            formation=formation,
            match__status__in=['COMPLETED', 'FULL_TIME'],
            match__scheduled_datetime__gte=cutoff_date,
            is_starting_eleven=True
        ).select_related('match').prefetch_related('match__team_stats')
        
        return [lineup.match for lineup in lineups]
    
    def _calculate_tactical_metrics(self, matches):
        if not matches:
            return {}
        
        team_stats = TeamStats.objects.filter(match__in=matches)
        
        metrics = {
            'average_possession': round(team_stats.aggregate(avg=Avg('possession_percentage'))['avg'] or 50, 2),
            'passing_accuracy': round(team_stats.aggregate(avg=Avg('pass_accuracy'))['avg'] or 0, 2),
            'shots_per_match': round(team_stats.aggregate(avg=Avg('shots_total'))['avg'] or 0, 2),
            'shots_on_target_ratio': self._calculate_shot_accuracy(team_stats),
            'defensive_actions': self._calculate_defensive_actions(matches),
            'attacking_third_entries': self._estimate_attacking_entries(team_stats),
            'set_piece_effectiveness': self._analyze_set_pieces(matches)
        }
        
        return metrics
    
    def _calculate_shot_accuracy(self, team_stats):
        total_shots = team_stats.aggregate(total=Sum('shots_total'))['total'] or 0
        shots_on_target = team_stats.aggregate(total=Sum('shots_on_target'))['total'] or 0
        
        if total_shots == 0:
            return 0
        
        return round((shots_on_target / total_shots) * 100, 2)
    
    def _calculate_defensive_actions(self, matches):
        all_player_stats = PlayerStats.objects.filter(match__in=matches)
        
        return {
            'tackles_per_match': round(all_player_stats.aggregate(avg=Avg('tackles_won'))['avg'] or 0, 2),
            'interceptions_per_match': round(all_player_stats.aggregate(avg=Avg('interceptions'))['avg'] or 0, 2),
            'clearances_per_match': round(all_player_stats.aggregate(avg=Avg('clearances'))['avg'] or 0, 2)
        }
    
    def _estimate_attacking_entries(self, team_stats):
        passes_total = team_stats.aggregate(avg=Avg('total_passes'))['avg'] or 0
        possession = team_stats.aggregate(avg=Avg('possession_percentage'))['avg'] or 50
        
        estimated_entries = (passes_total * possession / 100) * 0.15
        return round(estimated_entries, 2)
    
    def _analyze_set_pieces(self, matches):
        corners_total = 0
        goals_from_corners = 0
        
        for match in matches:
            try:
                team_stats = TeamStats.objects.get(match=match)
                corners_total += team_stats.corners
                
                corner_goals = MatchEvent.objects.filter(
                    match=match,
                    event_type='GOAL',
                    description__icontains='corner'
                ).count()
                goals_from_corners += corner_goals
                
            except TeamStats.DoesNotExist:
                continue
        
        corner_conversion = 0
        if corners_total > 0:
            corner_conversion = round((goals_from_corners / corners_total) * 100, 2)
        
        return {
            'corners_per_match': round(corners_total / max(len(matches), 1), 2),
            'corner_conversion_rate': corner_conversion
        }
    
    def _analyze_formation_performance(self, matches):
        wins = sum(1 for match in matches if match.result == 'WIN')
        draws = sum(1 for match in matches if match.result == 'DRAW')
        losses = sum(1 for match in matches if match.result == 'LOSS')
        
        goals_scored = sum(match.chelsea_score for match in matches)
        goals_conceded = sum(match.opponent_score for match in matches)
        
        return {
            'win_percentage': round((wins / len(matches)) * 100, 2),
            'draw_percentage': round((draws / len(matches)) * 100, 2),
            'loss_percentage': round((losses / len(matches)) * 100, 2),
            'goals_per_match': round(goals_scored / len(matches), 2),
            'goals_conceded_per_match': round(goals_conceded / len(matches), 2),
            'goal_difference': goals_scored - goals_conceded,
            'clean_sheets': sum(1 for match in matches if match.opponent_score == 0),
            'clean_sheet_percentage': round((sum(1 for match in matches if match.opponent_score == 0) / len(matches)) * 100, 2)
        }
    
    def _analyze_against_opposition_styles(self, formation, matches):
        opposition_analysis = {}
        
        for match in matches:
            opponent_style = match.opponent.playing_style or 'Unknown'
            opponent_formation = match.opponent.typical_formation
            
            if opponent_style not in opposition_analysis:
                opposition_analysis[opponent_style] = {
                    'matches': 0,
                    'wins': 0,
                    'goals_scored': 0,
                    'goals_conceded': 0,
                    'formations_faced': {}
                }
            
            style_data = opposition_analysis[opponent_style]
            style_data['matches'] += 1
            style_data['goals_scored'] += match.chelsea_score
            style_data['goals_conceded'] += match.opponent_score
            
            if match.result == 'WIN':
                style_data['wins'] += 1
            
            if opponent_formation not in style_data['formations_faced']:
                style_data['formations_faced'][opponent_formation] = 0
            style_data['formations_faced'][opponent_formation] += 1
        
        for style, data in opposition_analysis.items():
            if data['matches'] > 0:
                data['win_rate'] = round((data['wins'] / data['matches']) * 100, 2)
                data['avg_goals_scored'] = round(data['goals_scored'] / data['matches'], 2)
                data['avg_goals_conceded'] = round(data['goals_conceded'] / data['matches'], 2)
        
        return opposition_analysis
    
    def _analyze_player_utilisation(self, formation, matches):
        position_analysis = {}
        
        all_lineup_players = []
        for match in matches:
            try:
                lineup = MatchLineup.objects.get(match=match, formation=formation, is_starting_eleven=True)
                lineup_players = lineup.lineup_players.all()
                all_lineup_players.extend(lineup_players)
            except MatchLineup.DoesNotExist:
                continue
        
        for lineup_player in all_lineup_players:
            position = lineup_player.position
            
            if position not in position_analysis:
                position_analysis[position] = {
                    'players_used': set(),
                    'total_minutes': 0,
                    'average_rating': 0,
                    'goals': 0,
                    'assists': 0
                }
            
            pos_data = position_analysis[position]
            pos_data['players_used'].add(lineup_player.player.full_name)
            pos_data['total_minutes'] += lineup_player.minutes_played
            
            try:
                player_stats = PlayerStats.objects.get(
                    player=lineup_player.player,
                    match=lineup_player.lineup.match
                )
                pos_data['goals'] += player_stats.goals
                pos_data['assists'] += player_stats.assists
                
            except PlayerStats.DoesNotExist:
                continue
        
        for position, data in position_analysis.items():
            data['players_used'] = list(data['players_used'])
            data['player_rotation'] = len(data['players_used'])
            
            if data['total_minutes'] > 0:
                position_stats = PlayerStats.objects.filter(
                    match__in=matches,
                    player__position=position
                )
                data['average_rating'] = round(position_stats.aggregate(avg=Avg('rating'))['avg'] or 0, 2)
        
        return position_analysis
    
    def _assess_tactical_flexibility(self, formation, matches):
        in_game_changes = 0
        formation_changes = 0
        
        for match in matches:
            substitutions = MatchEvent.objects.filter(
                match=match,
                event_type='SUBSTITUTION'
            ).count()
            
            in_game_changes += substitutions
            
            lineups_count = MatchLineup.objects.filter(match=match).count()
            if lineups_count > 1:
                formation_changes += 1
        
        return {
            'average_substitutions': round(in_game_changes / max(len(matches), 1), 2),
            'formation_changes_frequency': round((formation_changes / len(matches)) * 100, 2),
            'tactical_adaptability': self._calculate_adaptability_score(in_game_changes, formation_changes, len(matches))
        }
    
    def _calculate_adaptability_score(self, substitutions, formation_changes, total_matches):
        sub_score = min(100, (substitutions / total_matches) * 20)
        change_score = min(50, (formation_changes / total_matches) * 100)
        
        return round(sub_score + change_score, 2)
    
    def _generate_tactical_recommendations(self, analysis_data):
        recommendations = []
        
        performance = analysis_data['performance_analysis']
        metrics = analysis_data['tactical_metrics']
        
        if performance['win_percentage'] < 50:
            recommendations.append({
                'priority': 'High',
                'category': 'Overall Performance',
                'recommendation': 'Consider alternative formations or tactical adjustments',
                'rationale': f"Current win rate of {performance['win_percentage']}% indicates room for improvement"
            })
        
        if performance['goals_per_match'] < 1.5:
            recommendations.append({
                'priority': 'High',
                'category': 'Attack',
                'recommendation': 'Increase attacking focus and creative player positioning',
                'rationale': f"Average of {performance['goals_per_match']} goals per match is below expectations"
            })
        
        if performance['goals_conceded_per_match'] > 1.2:
            recommendations.append({
                'priority': 'High',
                'category': 'Defence',
                'recommendation': 'Strengthen defensive structure and positioning',
                'rationale': f"Conceding {performance['goals_conceded_per_match']} goals per match on average"
            })
        
        if metrics.get('average_possession', 0) < 45:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Possession',
                'recommendation': 'Improve ball retention and passing accuracy',
                'rationale': f"Low possession average of {metrics['average_possession']}%"
            })
        
        if metrics.get('shots_on_target_ratio', 0) < 35:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Finishing',
                'recommendation': 'Focus on shot selection and finishing in training',
                'rationale': f"Shot accuracy of {metrics['shots_on_target_ratio']}% needs improvement"
            })
        
        return recommendations
    
    def _empty_formation_analysis(self, formation):
        return {
            'formation_name': formation.name,
            'analysis_period': self.analysis_period_days,
            'total_matches': 0,
            'tactical_metrics': {},
            'performance_analysis': {},
            'opposition_analysis': {},
            'player_utilisation': {},
            'tactical_flexibility': {},
            'recommendations': [{
                'priority': 'High',
                'category': 'Data Collection',
                'recommendation': 'Insufficient match data for analysis',
                'rationale': 'Need more matches with this formation to provide meaningful insights'
            }]
        }
    
    def analyze_match_tactics(self, match):
        try:
            lineup = MatchLineup.objects.get(match=match, is_starting_eleven=True)
            formation = lineup.formation
        except MatchLineup.DoesNotExist:
            return {'error': 'No lineup data available for tactical analysis'}
        
        try:
            team_stats = TeamStats.objects.get(match=match)
        except TeamStats.DoesNotExist:
            return {'error': 'No team statistics available for tactical analysis'}
        
        player_stats = PlayerStats.objects.filter(match=match)
        
        tactical_analysis = {
            'match_info': {
                'opponent': match.opponent.name,
                'formation_used': formation.name,
                'result': match.result,
                'score': f"{match.chelsea_score}-{match.opponent_score}"
            },
            'possession_analysis': self._analyze_match_possession(team_stats, player_stats),
            'attacking_analysis': self._analyze_match_attacking(team_stats, player_stats),
            'defensive_analysis': self._analyze_match_defensive(team_stats, player_stats),
            'formation_effectiveness': self._analyze_formation_in_match(formation, match, team_stats),
            'key_tactical_moments': self._identify_tactical_moments(match),
            'player_tactical_performance': self._analyze_player_tactical_roles(lineup, player_stats)
        }
        
        return tactical_analysis
    
    def _analyze_match_possession(self, team_stats, player_stats):
        total_passes = player_stats.aggregate(total=Sum('passes_attempted'))['total'] or 0
        completed_passes = player_stats.aggregate(total=Sum('passes_completed'))['total'] or 0
        
        return {
            'possession_percentage': float(team_stats.possession_percentage),
            'pass_completion_rate': round((completed_passes / max(total_passes, 1)) * 100, 2),
            'total_passes': total_passes,
            'possession_effectiveness': self._rate_possession_effectiveness(team_stats.possession_percentage, completed_passes, total_passes)
        }
    
    def _analyze_match_attacking(self, team_stats, player_stats):
        total_shots = player_stats.aggregate(
            on_target=Sum('shots_on_target'),
            off_target=Sum('shots_off_target')
        )
        
        return {
            'shots_total': team_stats.shots_total,
            'shots_on_target': team_stats.shots_on_target,
            'shot_accuracy': round((team_stats.shots_on_target / max(team_stats.shots_total, 1)) * 100, 2),
            'attacking_third_passes': self._estimate_attacking_passes(player_stats),
            'crosses_attempted': player_stats.aggregate(total=Sum('crosses_attempted'))['total'] or 0,
            'crosses_completed': player_stats.aggregate(total=Sum('crosses_completed'))['total'] or 0
        }
    
    def _analyze_match_defensive(self, team_stats, player_stats):
        return {
            'tackles_won': player_stats.aggregate(total=Sum('tackles_won'))['total'] or 0,
            'interceptions': player_stats.aggregate(total=Sum('interceptions'))['total'] or 0,
            'clearances': player_stats.aggregate(total=Sum('clearances'))['total'] or 0,
            'fouls_committed': team_stats.fouls_committed,
            'defensive_solidity': self._rate_defensive_performance(player_stats)
        }
    
    def _analyze_formation_in_match(self, formation, match, team_stats):
        historical_effectiveness = self.analyze_formation_effectiveness(formation, period_days=180)
        
        return {
            'formation_name': formation.name,
            'match_performance_vs_average': self._compare_to_formation_average(match, team_stats, historical_effectiveness),
            'formation_suitability_rating': self._rate_formation_suitability(match, team_stats, historical_effectiveness)
        }
    
    def _identify_tactical_moments(self, match):
        events = MatchEvent.objects.filter(match=match).order_by('minute')
        
        tactical_moments = []
        for event in events:
            if event.event_type in ['GOAL', 'RED_CARD', 'SUBSTITUTION']:
                tactical_moments.append({
                    'minute': event.minute,
                    'event_type': event.event_type,
                    'player': event.player.full_name,
                    'description': event.description,
                    'tactical_impact': self._assess_event_tactical_impact(event)
                })
        
        return tactical_moments
    
    def _analyze_player_tactical_roles(self, lineup, player_stats):
        role_analysis = {}
        
        for lineup_player in lineup.lineup_players.all():
            try:
                stats = player_stats.get(player=lineup_player.player)
                role_analysis[lineup_player.player.full_name] = {
                    'position': lineup_player.position,
                    'minutes_played': lineup_player.minutes_played,
                    'tactical_rating': float(stats.rating),
                    'role_effectiveness': self._assess_positional_effectiveness(lineup_player.position, stats)
                }
            except PlayerStats.DoesNotExist:
                continue
        
        return role_analysis
    
    def generate_tactical_insights(self, period_days=30):
        cutoff_date = timezone.now() - timedelta(days=period_days)
        recent_matches = Match.objects.filter(
            scheduled_datetime__gte=cutoff_date,
            status__in=['COMPLETED', 'FULL_TIME']
        )
        
        insights = {
            'period_summary': f"Last {period_days} days",
            'matches_analyzed': recent_matches.count(),
            'formation_insights': self._generate_formation_insights(recent_matches),
            'performance_patterns': self._identify_performance_patterns(recent_matches),
            'tactical_trends': self._analyze_tactical_trends(recent_matches),
            'opposition_vulnerabilities': self._identify_opposition_patterns(recent_matches),
            'recommended_adjustments': []
        }
        
        insights['recommended_adjustments'] = self._generate_tactical_adjustments(insights)
        
        return insights
    
    def _generate_formation_insights(self, matches):
        formation_performance = {}
        
        for match in matches:
            try:
                lineup = MatchLineup.objects.get(match=match, is_starting_eleven=True)
                formation_name = lineup.formation.name
                
                if formation_name not in formation_performance:
                    formation_performance[formation_name] = {
                        'matches': 0,
                        'wins': 0,
                        'goals_scored': 0,
                        'goals_conceded': 0
                    }
                
                data = formation_performance[formation_name]
                data['matches'] += 1
                data['goals_scored'] += match.chelsea_score
                data['goals_conceded'] += match.opponent_score
                
                if match.result == 'WIN':
                    data['wins'] += 1
                    
            except MatchLineup.DoesNotExist:
                continue
        
        for formation, data in formation_performance.items():
            if data['matches'] > 0:
                data['win_rate'] = round((data['wins'] / data['matches']) * 100, 2)
                data['goals_per_match'] = round(data['goals_scored'] / data['matches'], 2)
                data['goals_conceded_per_match'] = round(data['goals_conceded'] / data['matches'], 2)
        
        return formation_performance
    
    def _identify_performance_patterns(self, matches):
        home_performance = {'wins': 0, 'total': 0, 'goals_scored': 0, 'goals_conceded': 0}
        away_performance = {'wins': 0, 'total': 0, 'goals_scored': 0, 'goals_conceded': 0}
        
        for match in matches:
            performance = home_performance if match.is_home else away_performance
            performance['total'] += 1
            performance['goals_scored'] += match.chelsea_score
            performance['goals_conceded'] += match.opponent_score
            
            if match.result == 'WIN':
                performance['wins'] += 1
        
        return {
            'home_vs_away': {
                'home_win_rate': round((home_performance['wins'] / max(home_performance['total'], 1)) * 100, 2),
                'away_win_rate': round((away_performance['wins'] / max(away_performance['total'], 1)) * 100, 2),
                'home_goals_per_match': round(home_performance['goals_scored'] / max(home_performance['total'], 1), 2),
                'away_goals_per_match': round(away_performance['goals_scored'] / max(away_performance['total'], 1), 2)
            }
        }
    
    def _analyze_tactical_trends(self, matches):
        return {
            'most_used_formation': self._get_most_used_formation(matches),
            'formation_changes_per_match': self._calculate_formation_changes(matches),
            'substitution_patterns': self._analyze_substitution_patterns(matches)
        }
    
    def _identify_opposition_patterns(self, matches):
        opponent_analysis = {}
        
        for match in matches:
            opponent_formation = match.opponent.typical_formation
            
            if opponent_formation not in opponent_analysis:
                opponent_analysis[opponent_formation] = {
                    'matches': 0,
                    'wins': 0,
                    'goals_scored': 0,
                    'goals_conceded': 0
                }
            
            data = opponent_analysis[opponent_formation]
            data['matches'] += 1
            data['goals_scored'] += match.chelsea_score
            data['goals_conceded'] += match.opponent_score
            
            if match.result == 'WIN':
                data['wins'] += 1
        
        return opponent_analysis
    
    def _generate_tactical_adjustments(self, insights):
        adjustments = []
        
        formation_insights = insights.get('formation_insights', {})
        best_formation = max(formation_insights.keys(), key=lambda x: formation_insights[x].get('win_rate', 0)) if formation_insights else None
        
        if best_formation:
            best_win_rate = formation_insights[best_formation]['win_rate']
            if best_win_rate > 70:
                adjustments.append(f"Continue utilising {best_formation} formation - showing excellent results with {best_win_rate}% win rate")
        
        patterns = insights.get('performance_patterns', {}).get('home_vs_away', {})
        home_rate = patterns.get('home_win_rate', 0)
        away_rate = patterns.get('away_win_rate', 0)
        
        if home_rate > away_rate + 20:
            adjustments.append("Consider tactical adjustments for away matches to improve consistency")
        elif away_rate > home_rate + 20:
            adjustments.append("Apply successful away tactical approach to home matches")
        
        return adjustments
    
    def _rate_possession_effectiveness(self, possession_pct, completed_passes, total_passes):
        pass_accuracy = (completed_passes / max(total_passes, 1)) * 100
        
        if possession_pct > 60 and pass_accuracy > 85:
            return 'Excellent'
        elif possession_pct > 50 and pass_accuracy > 80:
            return 'Good'
        elif possession_pct > 40 and pass_accuracy > 75:
            return 'Average'
        else:
            return 'Needs Improvement'
    
    def _estimate_attacking_passes(self, player_stats):
        attacking_positions = ['CAM', 'LW', 'RW', 'ST']
        attacking_passes = player_stats.filter(
            player__position__in=attacking_positions
        ).aggregate(total=Sum('passes_completed'))['total'] or 0
        
        return attacking_passes
    
    def _rate_defensive_performance(self, player_stats):
        defensive_actions = (
            (player_stats.aggregate(total=Sum('tackles_won'))['total'] or 0) +
            (player_stats.aggregate(total=Sum('interceptions'))['total'] or 0) +
            (player_stats.aggregate(total=Sum('clearances'))['total'] or 0)
        )
        
        if defensive_actions > 20:
            return 'Excellent'
        elif defensive_actions > 15:
            return 'Good'
        elif defensive_actions > 10:
            return 'Average'
        else:
            return 'Poor'
    
    def _compare_to_formation_average(self, match, team_stats, historical_data):
        if not historical_data.get('tactical_metrics'):
            return 'No comparison data available'
        
        historical = historical_data['tactical_metrics']
        current_possession = float(team_stats.possession_percentage)
        historical_possession = historical.get('average_possession', 50)
        
        possession_diff = current_possession - historical_possession
        
        if possession_diff > 10:
            return 'Above average possession control'
        elif possession_diff < -10:
            return 'Below average possession control'
        else:
            return 'Consistent with formation average'
    
    def _rate_formation_suitability(self, match, team_stats, historical_data):
        result_score = 3 if match.result == 'WIN' else 1 if match.result == 'DRAW' else 0
        possession_score = min(3, float(team_stats.possession_percentage) / 20)
        shot_score = min(3, team_stats.shots_on_target / 2)
        
        total_score = result_score + possession_score + shot_score
        
        if total_score >= 7:
            return 'Highly Suitable'
        elif total_score >= 5:
            return 'Suitable'
        elif total_score >= 3:
            return 'Moderately Suitable'
        else:
            return 'Unsuitable'
    
    def _assess_event_tactical_impact(self, event):
        impact_ratings = {
            'GOAL': 'High - Changes momentum and scoreline',
            'RED_CARD': 'Very High - Forces tactical reorganisation',
            'SUBSTITUTION': 'Medium - Tactical adjustment',
            'PENALTY': 'High - High-value scoring opportunity',
            'YELLOW_CARD': 'Low - Minor tactical consideration'
        }
        
        return impact_ratings.get(event.event_type, 'Minimal tactical impact')
    
    def _assess_positional_effectiveness(self, position, stats):
        position_metrics = {
            'GK': stats.rating,
            'CB': (stats.tackles_won + stats.interceptions + stats.clearances) / 3,
            'LB': (stats.tackles_won + stats.crosses_completed + stats.assists * 2) / 3,
            'RB': (stats.tackles_won + stats.crosses_completed + stats.assists * 2) / 3,
            'CDM': (stats.tackles_won + stats.interceptions + stats.passes_completed / 10) / 3,
            'CM': (stats.passes_completed / 10 + stats.assists * 2 + stats.goals * 3) / 3,
            'CAM': (stats.assists * 3 + stats.goals * 4 + stats.shots_on_target) / 3,
            'LM': (stats.crosses_completed + stats.assists * 2 + stats.goals * 3) / 3,
            'RM': (stats.crosses_completed + stats.assists * 2 + stats.goals * 3) / 3,
            'LW': (stats.goals * 4 + stats.assists * 2 + stats.shots_on_target) / 3,
            'RW': (stats.goals * 4 + stats.assists * 2 + stats.shots_on_target) / 3,
            'ST': (stats.goals * 5 + stats.assists + stats.shots_on_target) / 3
        }
        
        effectiveness_score = position_metrics.get(position, float(stats.rating))
        
        if effectiveness_score >= 8:
            return 'Excellent'
        elif effectiveness_score >= 6:
            return 'Good'
        elif effectiveness_score >= 4:
            return 'Average'
        else:
            return 'Below Par'
    
    def _get_most_used_formation(self, matches):
        formation_counts = {}
        
        for match in matches:
            try:
                lineup = MatchLineup.objects.get(match=match, is_starting_eleven=True)
                formation_name = lineup.formation.name
                formation_counts[formation_name] = formation_counts.get(formation_name, 0) + 1
            except MatchLineup.DoesNotExist:
                continue
        
        if formation_counts:
            return max(formation_counts, key=formation_counts.get)
        return 'No data available'
    
    def _calculate_formation_changes(self, matches):
        total_changes = 0
        
        for match in matches:
            lineups = MatchLineup.objects.filter(match=match).count()
            if lineups > 1:
                total_changes += lineups - 1
        
        return round(total_changes / max(len(matches), 1), 2)
    
    def _analyze_substitution_patterns(self, matches):
        total_subs = 0
        early_subs = 0
        late_subs = 0
        
        for match in matches:
            subs = MatchEvent.objects.filter(match=match, event_type='SUBSTITUTION')
            total_subs += subs.count()
            
            for sub in subs:
                if sub.minute <= 60:
                    early_subs += 1
                elif sub.minute >= 75:
                    late_subs += 1
        
        return {
            'average_substitutions': round(total_subs / max(len(matches), 1), 2),
            'early_substitutions_percentage': round((early_subs / max(total_subs, 1)) * 100, 2),
            'late_substitutions_percentage': round((late_subs / max(total_subs, 1)) * 100, 2)
        }