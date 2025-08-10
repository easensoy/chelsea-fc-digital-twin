from django.db.models import Q, F, Sum, Avg, Count
from django.utils import timezone
from django.core.cache import cache
from decimal import Decimal
import json
import logging
from datetime import timedelta

from .models import Match, Player, PlayerStats, TeamStats, MatchEvent, MatchLineup, MatchLineupPlayer, Formation

logger = logging.getLogger('core.performance')

class LiveTracker:
    
    def __init__(self):
        self.logger = logging.getLogger('core.performance')
        self.cache_timeout = 30
        
    def get_live_data(self, live_matches):
        live_data = {
            'matches': [],
            'last_updated': timezone.now().isoformat(),
            'total_live_matches': len(live_matches)
        }
        
        for match in live_matches:
            match_data = self._get_live_match_data(match)
            live_data['matches'].append(match_data)
        
        return live_data
    
    def _get_live_match_data(self, match):
        cache_key = f"live_match_{match.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        match_data = {
            'match_id': str(match.id),
            'opponent': match.opponent.name,
            'status': match.status,
            'score': {
                'chelsea': match.chelsea_score,
                'opponent': match.opponent_score
            },
            'match_time': self._calculate_match_time(match),
            'formation': self._get_current_formation(match),
            'live_stats': self._get_live_team_stats(match),
            'player_performance': self._get_live_player_performance(match),
            'recent_events': self._get_recent_events(match),
            'tactical_insights': self._generate_live_tactical_insights(match),
            'substitution_recommendations': self._get_substitution_recommendations(match)
        }
        
        cache.set(cache_key, match_data, self.cache_timeout)
        return match_data
    
    def _calculate_match_time(self, match):
        if match.status == 'SCHEDULED':
            return 0
        elif match.status == 'LIVE':
            if match.actual_kickoff:
                elapsed = timezone.now() - match.actual_kickoff
                return min(90, int(elapsed.total_seconds() / 60))
            return 0
        elif match.status == 'HALF_TIME':
            return 45
        elif match.status in ['FULL_TIME', 'COMPLETED']:
            return 90
        
        return 0
    
    def _get_current_formation(self, match):
        try:
            current_lineup = MatchLineup.objects.filter(
                match=match
            ).order_by('-created_at').first()
            
            if current_lineup:
                return {
                    'formation_name': current_lineup.formation.name,
                    'formation_id': str(current_lineup.formation.id),
                    'players_on_pitch': self._get_players_on_pitch(current_lineup)
                }
        except MatchLineup.DoesNotExist:
            pass
        
        return {'formation_name': 'Unknown', 'formation_id': None, 'players_on_pitch': []}
    
    def _get_players_on_pitch(self, lineup):
        substitutions = MatchEvent.objects.filter(
            match=lineup.match,
            event_type='SUBSTITUTION'
        ).order_by('minute')
        
        players_on_pitch = []
        substituted_players = set()
        
        for lineup_player in lineup.lineup_players.all():
            player_subbed = False
            
            for sub in substitutions:
                if sub.description and lineup_player.player.full_name in sub.description:
                    if 'off' in sub.description.lower() or 'substituted' in sub.description.lower():
                        player_subbed = True
                        substituted_players.add(lineup_player.player.id)
                        break
            
            if not player_subbed:
                current_stats = self._get_current_player_stats(lineup_player.player, lineup.match)
                players_on_pitch.append({
                    'player_name': lineup_player.player.full_name,
                    'position': lineup_player.position,
                    'squad_number': lineup_player.player.squad_number,
                    'is_captain': lineup_player.is_captain,
                    'current_rating': current_stats.get('current_rating', 0),
                    'minutes_played': self._calculate_player_minutes(lineup_player, lineup.match)
                })
        
        for sub in substitutions:
            if 'on' in sub.description.lower() or 'substitute' in sub.description.lower():
                if sub.player.id not in substituted_players:
                    current_stats = self._get_current_player_stats(sub.player, lineup.match)
                    players_on_pitch.append({
                        'player_name': sub.player.full_name,
                        'position': sub.player.position,
                        'squad_number': sub.player.squad_number,
                        'is_captain': False,
                        'current_rating': current_stats.get('current_rating', 0),
                        'minutes_played': self._calculate_substitution_minutes(sub, lineup.match)
                    })
        
        return players_on_pitch
    
    def _get_live_team_stats(self, match):
        try:
            team_stats = TeamStats.objects.get(match=match)
            
            live_stats = {
                'possession_percentage': float(team_stats.possession_percentage),
                'total_passes': team_stats.total_passes,
                'pass_accuracy': float(team_stats.pass_accuracy),
                'shots_total': team_stats.shots_total,
                'shots_on_target': team_stats.shots_on_target,
                'corners': team_stats.corners,
                'offsides': team_stats.offsides,
                'fouls_committed': team_stats.fouls_committed,
                'yellow_cards': team_stats.yellow_cards,
                'red_cards': team_stats.red_cards
            }
            
            live_stats.update(self._calculate_dynamic_stats(match))
            return live_stats
            
        except TeamStats.DoesNotExist:
            return self._create_default_live_stats(match)
    
    def _calculate_dynamic_stats(self, match):
        player_stats = PlayerStats.objects.filter(match=match)
        
        return {
            'total_distance_covered': round(float(player_stats.aggregate(total=Sum('distance_covered'))['total'] or 0), 2),
            'total_sprints': player_stats.aggregate(total=Sum('sprints'))['total'] or 0,
            'average_player_rating': round(float(player_stats.aggregate(avg=Avg('rating'))['avg'] or 0), 2),
            'tackles_won': player_stats.aggregate(total=Sum('tackles_won'))['total'] or 0,
            'interceptions': player_stats.aggregate(total=Sum('interceptions'))['total'] or 0,
            'crosses_completed': player_stats.aggregate(total=Sum('crosses_completed'))['total'] or 0
        }
    
    def _get_live_player_performance(self, match):
        current_stats = PlayerStats.objects.filter(match=match).select_related('player')
        
        performance_data = []
        for stats in current_stats:
            player_data = {
                'player_name': stats.player.full_name,
                'position': stats.player.position,
                'squad_number': stats.player.squad_number,
                'current_rating': float(stats.rating),
                'minutes_played': stats.minutes_played,
                'goals': stats.goals,
                'assists': stats.assists,
                'passes_completed': stats.passes_completed,
                'passes_attempted': stats.passes_attempted,
                'pass_accuracy': round(self._calculate_pass_accuracy(stats), 2),
                'distance_covered': float(stats.distance_covered),
                'sprints': stats.sprints,
                'tackles_won': stats.tackles_won,
                'shots_total': stats.shots_on_target + stats.shots_off_target,
                'performance_indicator': self._calculate_performance_indicator(stats),
                'fitness_status': self._assess_live_fitness(stats)
            }
            performance_data.append(player_data)
        
        return sorted(performance_data, key=lambda x: x['current_rating'], reverse=True)
    
    def _get_recent_events(self, match, limit=10):
        recent_events = MatchEvent.objects.filter(
            match=match
        ).order_by('-minute', '-created_at')[:limit]
        
        events_data = []
        for event in recent_events:
            events_data.append({
                'minute': event.minute,
                'event_type': event.event_type,
                'player_name': event.player.full_name,
                'description': event.description,
                'tactical_impact': self._assess_event_tactical_impact(event),
                'timestamp': event.created_at.isoformat()
            })
        
        return events_data
    
    def _generate_live_tactical_insights(self, match):
        insights = []
        
        match_time = self._calculate_match_time(match)
        team_stats = self._get_live_team_stats(match)
        
        if team_stats['possession_percentage'] < 40:
            insights.append({
                'priority': 'High',
                'category': 'Possession',
                'insight': 'Low possession percentage - consider tactical adjustment',
                'recommendation': 'Increase midfield presence or adjust pressing intensity'
            })
        
        if team_stats['shots_total'] < 2 and match_time > 30:
            insights.append({
                'priority': 'Medium',
                'category': 'Attack',
                'insight': 'Limited attacking threat created',
                'recommendation': 'Consider more attacking formation or player changes'
            })
        
        if team_stats['yellow_cards'] >= 3:
            insights.append({
                'priority': 'High',
                'category': 'Discipline',
                'insight': 'High number of yellow cards accumulated',
                'recommendation': 'Caution players about tackling and consider substitutions'
            })
        
        recent_goals = MatchEvent.objects.filter(
            match=match,
            event_type='GOAL',
            minute__gte=match_time - 10
        ).count()
        
        if recent_goals > 0:
            insights.append({
                'priority': 'Medium',
                'category': 'Momentum',
                'insight': 'Recent goal scored - momentum opportunity',
                'recommendation': 'Consider maintaining attacking intensity or consolidating lead'
            })
        
        if match_time > 75:
            insights.extend(self._generate_late_match_insights(match, team_stats))
        
        return insights
    
    def _generate_late_match_insights(self, match, team_stats):
        late_insights = []
        
        score_difference = match.chelsea_score - match.opponent_score
        
        if score_difference == 0:
            late_insights.append({
                'priority': 'High',
                'category': 'Late Match',
                'insight': 'Match tied in final stages',
                'recommendation': 'Consider attacking substitutions for winner'
            })
        elif score_difference == 1:
            late_insights.append({
                'priority': 'Medium',
                'category': 'Late Match',
                'insight': 'One-goal lead in final stages',
                'recommendation': 'Balance between defending lead and seeking insurance goal'
            })
        elif score_difference == -1:
            late_insights.append({
                'priority': 'High',
                'category': 'Late Match',
                'insight': 'One goal behind in final stages',
                'recommendation': 'Urgent need for attacking changes and tactical urgency'
            })
        
        if team_stats['average_player_rating'] < 6.5:
            late_insights.append({
                'priority': 'Medium',
                'category': 'Performance',
                'insight': 'Team performance below standard in late stages',
                'recommendation': 'Consider fresh legs through substitutions'
            })
        
        return late_insights
    
    def _get_substitution_recommendations(self, match):
        current_lineup = self._get_current_formation(match)
        players_on_pitch = current_lineup.get('players_on_pitch', [])
        
        recommendations = []
        
        for player_data in players_on_pitch:
            if player_data['minutes_played'] > 75 and player_data['current_rating'] < 6.0:
                recommendations.append({
                    'type': 'Performance Substitution',
                    'player_off': player_data['player_name'],
                    'position': player_data['position'],
                    'reason': f"Poor performance (rating: {player_data['current_rating']})",
                    'urgency': 'Medium',
                    'suggested_replacement': self._suggest_replacement_player(player_data['position'], match)
                })
            
            elif player_data['minutes_played'] > 80:
                recommendations.append({
                    'type': 'Fitness Substitution',
                    'player_off': player_data['player_name'],
                    'position': player_data['position'],
                    'reason': 'High playing time - fitness consideration',
                    'urgency': 'Low',
                    'suggested_replacement': self._suggest_replacement_player(player_data['position'], match)
                })
        
        match_time = self._calculate_match_time(match)
        score_difference = match.chelsea_score - match.opponent_score
        
        if match_time > 70 and score_difference < 0:
            recommendations.extend(self._suggest_attacking_substitutions(match, players_on_pitch))
        elif match_time > 80 and score_difference > 0:
            recommendations.extend(self._suggest_defensive_substitutions(match, players_on_pitch))
        
        return recommendations
    
    def _suggest_replacement_player(self, position, match):
        used_players = set()
        
        lineup_players = MatchLineupPlayer.objects.filter(
            lineup__match=match
        ).select_related('player')
        
        for lineup_player in lineup_players:
            used_players.add(lineup_player.player.id)
        
        substitution_events = MatchEvent.objects.filter(
            match=match,
            event_type='SUBSTITUTION'
        )
        
        for sub_event in substitution_events:
            used_players.add(sub_event.player.id)
        
        available_players = Player.objects.filter(
            position=position,
            is_active=True,
            is_injured=False
        ).exclude(id__in=used_players).order_by('-fitness_level', '-market_value')
        
        if available_players.exists():
            best_replacement = available_players.first()
            return {
                'player_name': best_replacement.full_name,
                'fitness_level': best_replacement.fitness_level,
                'squad_number': best_replacement.squad_number
            }
        
        return None
    
    def _suggest_attacking_substitutions(self, match, players_on_pitch):
        attacking_subs = []
        
        defensive_players = [p for p in players_on_pitch if p['position'] in ['CB', 'CDM']]
        
        if len(defensive_players) > 3:
            defensive_player = min(defensive_players, key=lambda x: x['current_rating'])
            
            attacking_subs.append({
                'type': 'Tactical Substitution',
                'player_off': defensive_player['player_name'],
                'position': defensive_player['position'],
                'reason': 'Need more attacking threat - behind in score',
                'urgency': 'High',
                'suggested_replacement': self._suggest_attacking_player(match),
                'tactical_note': 'Sacrifice defensive stability for attacking options'
            })
        
        return attacking_subs
    
    def _suggest_defensive_substitutions(self, match, players_on_pitch):
        defensive_subs = []
        
        attacking_players = [p for p in players_on_pitch if p['position'] in ['CAM', 'LW', 'RW', 'ST']]
        
        if len(attacking_players) > 2:
            attacking_player = min(attacking_players, key=lambda x: x['current_rating'])
            
            defensive_subs.append({
                'type': 'Tactical Substitution',
                'player_off': attacking_player['player_name'],
                'position': attacking_player['position'],
                'reason': 'Protect lead with defensive reinforcement',
                'urgency': 'Medium',
                'suggested_replacement': self._suggest_defensive_player(match),
                'tactical_note': 'Strengthen defensive structure to preserve lead'
            })
        
        return defensive_subs
    
    def _suggest_attacking_player(self, match):
        used_players = self._get_used_players(match)
        
        attacking_players = Player.objects.filter(
            position__in=['CAM', 'LW', 'RW', 'ST'],
            is_active=True,
            is_injured=False
        ).exclude(id__in=used_players).order_by('-fitness_level')
        
        if attacking_players.exists():
            player = attacking_players.first()
            return {
                'player_name': player.full_name,
                'position': player.position,
                'squad_number': player.squad_number
            }
        
        return None
    
    def _suggest_defensive_player(self, match):
        used_players = self._get_used_players(match)
        
        defensive_players = Player.objects.filter(
            position__in=['CB', 'CDM', 'CM'],
            is_active=True,
            is_injured=False
        ).exclude(id__in=used_players).order_by('-fitness_level')
        
        if defensive_players.exists():
            player = defensive_players.first()
            return {
                'player_name': player.full_name,
                'position': player.position,
                'squad_number': player.squad_number
            }
        
        return None
    
    def _get_used_players(self, match):
        used_players = set()
        
        lineup_players = MatchLineupPlayer.objects.filter(
            lineup__match=match
        ).values_list('player_id', flat=True)
        
        used_players.update(lineup_players)
        
        substitution_players = MatchEvent.objects.filter(
            match=match,
            event_type='SUBSTITUTION'
        ).values_list('player_id', flat=True)
        
        used_players.update(substitution_players)
        
        return used_players
    
    def record_event(self, match, event_data):
        try:
            player = Player.objects.get(id=event_data['player_id'])
            
            event = MatchEvent.objects.create(
                match=match,
                player=player,
                event_type=event_data['event_type'],
                minute=event_data['minute'],
                description=event_data.get('description', ''),
                x_coordinate=event_data.get('x_coordinate'),
                y_coordinate=event_data.get('y_coordinate')
            )
            
            self._update_match_stats_for_event(match, event)
            self._clear_match_cache(match)
            
            self.logger.info(f"Live event recorded: {event.event_type} by {player.full_name} at {event.minute}'")
            
            return {
                'success': True,
                'event_id': str(event.id),
                'message': f"{event.event_type} recorded successfully"
            }
            
        except Player.DoesNotExist:
            return {'success': False, 'error': 'Player not found'}
        except Exception as e:
            self.logger.error(f"Failed to record event: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_match_live(self, match, update_data):
        try:
            if 'score' in update_data:
                match.chelsea_score = update_data['score']['chelsea']
                match.opponent_score = update_data['score']['opponent']
            
            if 'status' in update_data:
                match.status = update_data['status']
            
            if 'actual_kickoff' in update_data and not match.actual_kickoff:
                match.actual_kickoff = timezone.now()
            
            match.save()
            
            if 'team_stats' in update_data:
                self._update_team_stats(match, update_data['team_stats'])
            
            if 'player_stats' in update_data:
                self._update_player_stats(match, update_data['player_stats'])
            
            self._clear_match_cache(match)
            
            return {
                'success': True,
                'message': 'Match updated successfully',
                'updated_data': {
                    'score': f"{match.chelsea_score}-{match.opponent_score}",
                    'status': match.status,
                    'match_time': self._calculate_match_time(match)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update live match: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _update_match_stats_for_event(self, match, event):
        if event.event_type == 'GOAL':
            match.chelsea_score = F('chelsea_score') + 1
            match.save(update_fields=['chelsea_score'])
        
        try:
            player_stats, created = PlayerStats.objects.get_or_create(
                player=event.player,
                match=match,
                defaults={'minutes_played': self._calculate_match_time(match)}
            )
            
            if event.event_type == 'GOAL':
                player_stats.goals = F('goals') + 1
            elif event.event_type == 'ASSIST':
                player_stats.assists = F('assists') + 1
            elif event.event_type == 'YELLOW_CARD':
                player_stats.yellow_cards = F('yellow_cards') + 1
            elif event.event_type == 'RED_CARD':
                player_stats.red_cards = F('red_cards') + 1
            elif event.event_type == 'OFFSIDE':
                player_stats.offsides = F('offsides') + 1
            elif event.event_type == 'FOUL':
                player_stats.fouls_committed = F('fouls_committed') + 1
            
            player_stats.save()
            
        except Exception as e:
            self.logger.error(f"Failed to update player stats for event: {str(e)}")
    
    def _update_team_stats(self, match, team_stats_data):
        team_stats, created = TeamStats.objects.get_or_create(
            match=match,
            defaults=team_stats_data
        )
        
        if not created:
            for field, value in team_stats_data.items():
                if hasattr(team_stats, field):
                    setattr(team_stats, field, value)
            
            team_stats.save()
    
    def _update_player_stats(self, match, player_stats_data):
        for player_data in player_stats_data:
            try:
                player = Player.objects.get(id=player_data['player_id'])
                
                player_stats, created = PlayerStats.objects.get_or_create(
                    player=player,
                    match=match,
                    defaults=player_data
                )
                
                if not created:
                    for field, value in player_data.items():
                        if hasattr(player_stats, field) and field != 'player_id':
                            setattr(player_stats, field, value)
                    
                    player_stats.save()
                    
            except Player.DoesNotExist:
                continue
    
    def _clear_match_cache(self, match):
        cache_key = f"live_match_{match.id}"
        cache.delete(cache_key)
    
    def _calculate_pass_accuracy(self, stats):
        if stats.passes_attempted == 0:
            return 0
        return (stats.passes_completed / stats.passes_attempted) * 100
    
    def _calculate_performance_indicator(self, stats):
        base_rating = float(stats.rating)
        
        goal_bonus = stats.goals * 0.5
        assist_bonus = stats.assists * 0.3
        pass_accuracy_bonus = (self._calculate_pass_accuracy(stats) - 80) / 20 * 0.2
        
        performance_score = base_rating + goal_bonus + assist_bonus + pass_accuracy_bonus
        
        return min(10, max(0, round(performance_score, 2)))
    
    def _assess_live_fitness(self, stats):
        distance_factor = min(1, float(stats.distance_covered) / 12000)
        sprint_factor = min(1, stats.sprints / 20)
        time_factor = stats.minutes_played / 90
        
        fitness_score = 100 - (distance_factor * 20 + sprint_factor * 15 + time_factor * 25)
        
        if fitness_score >= 80:
            return 'Excellent'
        elif fitness_score >= 65:
            return 'Good'
        elif fitness_score >= 50:
            return 'Moderate'
        else:
            return 'Tired'
    
    def _assess_event_tactical_impact(self, event):
        impact_levels = {
            'GOAL': 'High - Momentum shift and scoreline change',
            'RED_CARD': 'Very High - Numerical disadvantage requires tactical adjustment',
            'YELLOW_CARD': 'Low - Player must be cautious in challenges',
            'SUBSTITUTION': 'Medium - Fresh legs or tactical change',
            'ASSIST': 'Medium - Creative contribution',
            'PENALTY': 'High - High-value scoring opportunity',
            'CORNER': 'Low - Set piece opportunity',
            'OFFSIDE': 'Minimal - Tactical awareness needed',
            'FOUL': 'Low - Possible disciplinary concern',
            'SAVE': 'Medium - Goalkeeper contribution',
            'INJURY': 'Medium to High - Potential substitution required'
        }
        
        return impact_levels.get(event.event_type, 'Minimal impact')
    
    def _get_current_player_stats(self, player, match):
        try:
            stats = PlayerStats.objects.get(player=player, match=match)
            return {
                'current_rating': float(stats.rating),
                'goals': stats.goals,
                'assists': stats.assists,
                'minutes_played': stats.minutes_played
            }
        except PlayerStats.DoesNotExist:
            return {
                'current_rating': 6.0,
                'goals': 0,
                'assists': 0,
                'minutes_played': 0
            }
    
    def _calculate_player_minutes(self, lineup_player, match):
        match_time = self._calculate_match_time(match)
        
        substitution_events = MatchEvent.objects.filter(
            match=match,
            event_type='SUBSTITUTION'
        )
        
        for sub in substitution_events:
            if sub.description and lineup_player.player.full_name in sub.description:
                if 'off' in sub.description.lower():
                    return min(match_time, sub.minute)
        
        return match_time
    
    def _calculate_substitution_minutes(self, substitution_event, match):
        match_time = self._calculate_match_time(match)
        return max(0, match_time - substitution_event.minute)
    
    def _create_default_live_stats(self, match):
        return {
            'possession_percentage': 50.0,
            'total_passes': 0,
            'pass_accuracy': 0.0,
            'shots_total': 0,
            'shots_on_target': 0,
            'corners': 0,
            'offsides': 0,
            'fouls_committed': 0,
            'yellow_cards': 0,
            'red_cards': 0,
            'total_distance_covered': 0.0,
            'total_sprints': 0,
            'average_player_rating': 6.0,
            'tackles_won': 0,
            'interceptions': 0,
            'crosses_completed': 0
        }