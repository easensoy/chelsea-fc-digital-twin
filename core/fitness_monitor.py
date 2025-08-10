from django.db.models import Avg, Sum, Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
import logging

from .models import Player, PlayerStats, Match, MatchEvent

logger = logging.getLogger('core.performance')

class FitnessMonitor:
    
    def __init__(self):
        self.logger = logging.getLogger('core.performance')
        self.fitness_thresholds = {
            'critical': 60,
            'poor': 70,
            'average': 80,
            'good': 90,
            'excellent': 95
        }
        
    def get_fitness_status(self, player):
        current_fitness = player.fitness_level
        
        fitness_data = {
            'player_id': str(player.id),
            'player_name': player.full_name,
            'current_fitness': current_fitness,
            'fitness_category': self._categorise_fitness(current_fitness),
            'is_injured': player.is_injured,
            'fitness_trend': self._calculate_fitness_trend(player),
            'workload_analysis': self._analyse_workload(player),
            'recovery_status': self._assess_recovery_status(player),
            'injury_risk': self._calculate_injury_risk(player),
            'recommendations': self._generate_fitness_recommendations(player)
        }
        
        return fitness_data
    
    def _categorise_fitness(self, fitness_level):
        if fitness_level >= self.fitness_thresholds['excellent']:
            return 'excellent'
        elif fitness_level >= self.fitness_thresholds['good']:
            return 'good'
        elif fitness_level >= self.fitness_thresholds['average']:
            return 'average'
        elif fitness_level >= self.fitness_thresholds['poor']:
            return 'poor'
        else:
            return 'critical'
    
    def _calculate_fitness_trend(self, player, days=14):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        recent_matches = Match.objects.filter(
            scheduled_datetime__gte=cutoff_date,
            status__in=['COMPLETED', 'FULL_TIME']
        ).order_by('scheduled_datetime')
        
        fitness_points = []
        
        for match in recent_matches:
            try:
                stats = PlayerStats.objects.get(player=player, match=match)
                
                distance_factor = min(1.0, stats.distance_covered / 12000)
                sprint_factor = min(1.0, stats.sprints / 25)
                time_factor = stats.minutes_played / 90
                
                match_load = (distance_factor + sprint_factor + time_factor) / 3
                
                fitness_points.append({
                    'date': match.scheduled_datetime.date(),
                    'load': match_load,
                    'minutes': stats.minutes_played,
                    'distance': float(stats.distance_covered),
                    'sprints': stats.sprints
                })
                
            except PlayerStats.DoesNotExist:
                continue
        
        if len(fitness_points) < 2:
            return {
                'trend': 'stable',
                'change_rate': 0,
                'data_points': fitness_points
            }
        
        recent_avg = sum(point['load'] for point in fitness_points[-3:]) / min(3, len(fitness_points))
        early_avg = sum(point['load'] for point in fitness_points[:3]) / min(3, len(fitness_points))
        
        change_rate = (recent_avg - early_avg) * 100
        
        if change_rate > 10:
            trend = 'declining'
        elif change_rate < -10:
            trend = 'improving'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'change_rate': round(change_rate, 2),
            'data_points': fitness_points
        }
    
    def _analyse_workload(self, player, days=21):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        recent_stats = PlayerStats.objects.filter(
            player=player,
            match__scheduled_datetime__gte=cutoff_date,
            match__status__in=['COMPLETED', 'FULL_TIME']
        )
        
        if not recent_stats.exists():
            return {
                'total_minutes': 0,
                'matches_played': 0,
                'average_distance': 0,
                'total_sprints': 0,
                'workload_rating': 'low',
                'recovery_time_needed': 1
            }
        
        total_minutes = recent_stats.aggregate(total=Sum('minutes_played'))['total'] or 0
        matches_played = recent_stats.count()
        avg_distance = recent_stats.aggregate(avg=Avg('distance_covered'))['avg'] or 0
        total_sprints = recent_stats.aggregate(total=Sum('sprints'))['total'] or 0
        
        workload_score = (
            (total_minutes / 90) +
            (avg_distance / 10000) +
            (total_sprints / 20)
        ) / 3
        
        if workload_score > 0.8:
            workload_rating = 'very_high'
            recovery_time = 3
        elif workload_score > 0.6:
            workload_rating = 'high'
            recovery_time = 2
        elif workload_score > 0.4:
            workload_rating = 'moderate'
            recovery_time = 1
        elif workload_score > 0.2:
            workload_rating = 'low'
            recovery_time = 1
        else:
            workload_rating = 'very_low'
            recovery_time = 0
        
        return {
            'total_minutes': total_minutes,
            'matches_played': matches_played,
            'average_distance': round(float(avg_distance), 2),
            'total_sprints': total_sprints,
            'workload_rating': workload_rating,
            'recovery_time_needed': recovery_time
        }
    
    def _assess_recovery_status(self, player):
        last_match = Match.objects.filter(
            status__in=['COMPLETED', 'FULL_TIME'],
            player_stats__player=player
        ).order_by('-scheduled_datetime').first()
        
        if not last_match:
            return {
                'days_since_last_match': None,
                'recovery_status': 'unknown',
                'ready_for_match': True
            }
        
        days_since = (timezone.now().date() - last_match.scheduled_datetime.date()).days
        
        try:
            last_stats = PlayerStats.objects.get(player=player, match=last_match)
            intensity = (
                (last_stats.minutes_played / 90) +
                (float(last_stats.distance_covered) / 12000) +
                (last_stats.sprints / 25)
            ) / 3
        except PlayerStats.DoesNotExist:
            intensity = 0.5
        
        required_recovery = max(1, int(intensity * 3))
        
        if days_since >= required_recovery:
            recovery_status = 'fully_recovered'
            ready_for_match = True
        elif days_since >= required_recovery - 1:
            recovery_status = 'mostly_recovered'
            ready_for_match = True
        elif days_since >= 1:
            recovery_status = 'partial_recovery'
            ready_for_match = player.fitness_level >= 80
        else:
            recovery_status = 'needs_recovery'
            ready_for_match = False
        
        return {
            'days_since_last_match': days_since,
            'recovery_status': recovery_status,
            'ready_for_match': ready_for_match,
            'recommended_recovery_days': required_recovery
        }
    
    def _calculate_injury_risk(self, player):
        risk_factors = []
        risk_score = 0
        
        if player.age > 32:
            risk_factors.append('Advanced age')
            risk_score += 2
        elif player.age < 20:
            risk_factors.append('Young player development')
            risk_score += 1
        
        if player.fitness_level < 70:
            risk_factors.append('Low fitness level')
            risk_score += 3
        elif player.fitness_level < 85:
            risk_factors.append('Below optimal fitness')
            risk_score += 1
        
        workload = self._analyse_workload(player)
        if workload['workload_rating'] in ['very_high', 'high']:
            risk_factors.append('High recent workload')
            risk_score += 2
        
        recent_injuries = MatchEvent.objects.filter(
            player=player,
            event_type='INJURY',
            match__scheduled_datetime__gte=timezone.now() - timedelta(days=90)
        ).count()
        
        if recent_injuries > 0:
            risk_factors.append('Recent injury history')
            risk_score += recent_injuries
        
        recovery = self._assess_recovery_status(player)
        if not recovery['ready_for_match']:
            risk_factors.append('Insufficient recovery time')
            risk_score += 2
        
        if risk_score >= 6:
            risk_level = 'very_high'
        elif risk_score >= 4:
            risk_level = 'high'
        elif risk_score >= 2:
            risk_level = 'moderate'
        else:
            risk_level = 'low'
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'prevention_recommendations': self._get_injury_prevention_advice(risk_level, risk_factors)
        }
    
    def _get_injury_prevention_advice(self, risk_level, risk_factors):
        advice = []
        
        if risk_level in ['very_high', 'high']:
            advice.append('Consider rotation or rest')
            advice.append('Increase recovery time between matches')
            advice.append('Enhanced warm-up and cool-down routines')
        
        if 'Low fitness level' in risk_factors:
            advice.append('Gradual fitness improvement programme')
            advice.append('Extended training sessions')
        
        if 'High recent workload' in risk_factors:
            advice.append('Reduce training intensity')
            advice.append('Focus on recovery sessions')
        
        if 'Recent injury history' in risk_factors:
            advice.append('Targeted strengthening exercises')
            advice.append('Regular physiotherapy sessions')
        
        if 'Advanced age' in risk_factors:
            advice.append('Modified training regime')
            advice.append('Additional recovery time')
        
        return advice
    
    def _generate_fitness_recommendations(self, player):
        fitness_data = self.get_fitness_status(player)
        recommendations = []
        
        if player.fitness_level < 70:
            recommendations.append({
                'priority': 'high',
                'category': 'fitness',
                'action': 'Intensive fitness programme required',
                'timeline': '2-3 weeks'
            })
        elif player.fitness_level < 85:
            recommendations.append({
                'priority': 'medium',
                'category': 'fitness',
                'action': 'Gradual fitness improvement',
                'timeline': '1-2 weeks'
            })
        
        workload = self._analyse_workload(player)
        if workload['workload_rating'] == 'very_high':
            recommendations.append({
                'priority': 'high',
                'category': 'workload',
                'action': 'Immediate rest and recovery',
                'timeline': f"{workload['recovery_time_needed']} days"
            })
        elif workload['workload_rating'] == 'high':
            recommendations.append({
                'priority': 'medium',
                'category': 'workload',
                'action': 'Reduce training intensity',
                'timeline': '3-5 days'
            })
        
        injury_risk = self._calculate_injury_risk(player)
        if injury_risk['risk_level'] in ['very_high', 'high']:
            recommendations.append({
                'priority': 'high',
                'category': 'injury_prevention',
                'action': 'Enhanced injury prevention measures',
                'timeline': 'Immediate'
            })
        
        recovery = self._assess_recovery_status(player)
        if not recovery['ready_for_match']:
            recommendations.append({
                'priority': 'high',
                'category': 'recovery',
                'action': 'Complete recovery before next match',
                'timeline': f"{recovery['recommended_recovery_days']} days"
            })
        
        return recommendations
    
    def get_squad_fitness_overview(self):
        active_players = Player.objects.filter(is_active=True)
        
        fitness_distribution = {
            'excellent': 0,
            'good': 0,
            'average': 0,
            'poor': 0,
            'critical': 0
        }
        
        injury_count = 0
        high_risk_players = []
        low_fitness_players = []
        
        for player in active_players:
            if player.is_injured:
                injury_count += 1
            
            fitness_category = self._categorise_fitness(player.fitness_level)
            fitness_distribution[fitness_category] += 1
            
            if player.fitness_level < 70:
                low_fitness_players.append({
                    'name': player.full_name,
                    'fitness': player.fitness_level,
                    'position': player.position
                })
            
            injury_risk = self._calculate_injury_risk(player)
            if injury_risk['risk_level'] in ['very_high', 'high']:
                high_risk_players.append({
                    'name': player.full_name,
                    'risk_level': injury_risk['risk_level'],
                    'position': player.position
                })
        
        total_players = active_players.count()
        available_players = total_players - injury_count
        
        return {
            'total_players': total_players,
            'available_players': available_players,
            'injured_players': injury_count,
            'availability_percentage': round((available_players / total_players) * 100, 1) if total_players > 0 else 0,
            'fitness_distribution': fitness_distribution,
            'fitness_distribution_percentage': {
                category: round((count / total_players) * 100, 1) if total_players > 0 else 0
                for category, count in fitness_distribution.items()
            },
            'high_risk_players': high_risk_players,
            'low_fitness_players': low_fitness_players,
            'squad_fitness_average': round(
                active_players.aggregate(avg=Avg('fitness_level'))['avg'] or 0, 1
            )
        }
    
    def update_fitness_after_match(self, match):
        player_stats = PlayerStats.objects.filter(match=match)
        
        for stats in player_stats:
            player = stats.player
            
            intensity_factor = (
                (stats.minutes_played / 90) * 0.4 +
                (float(stats.distance_covered) / 12000) * 0.3 +
                (stats.sprints / 25) * 0.3
            )
            
            fitness_reduction = min(15, intensity_factor * 20)
            
            if stats.yellow_cards > 0:
                fitness_reduction += 2
            if stats.red_cards > 0:
                fitness_reduction += 5
            
            if player.age > 30:
                fitness_reduction *= 1.2
            elif player.age < 22:
                fitness_reduction *= 0.8
            
            new_fitness = max(0, player.fitness_level - int(fitness_reduction))
            
            player.fitness_level = new_fitness
            player.save(update_fields=['fitness_level'])
            
            self.logger.info(f"Updated fitness for {player.full_name}: {player.fitness_level}")
    
    def schedule_fitness_updates(self):
        active_players = Player.objects.filter(is_active=True, is_injured=False)
        
        for player in active_players:
            last_match = Match.objects.filter(
                status__in=['COMPLETED', 'FULL_TIME'],
                player_stats__player=player
            ).order_by('-scheduled_datetime').first()
            
            if last_match:
                days_since = (timezone.now().date() - last_match.scheduled_datetime.date()).days
                
                if days_since > 0:
                    recovery_rate = min(5, days_since * 2)
                    
                    if player.age > 30:
                        recovery_rate *= 0.8
                    elif player.age < 22:
                        recovery_rate *= 1.2
                    
                    new_fitness = min(100, player.fitness_level + int(recovery_rate))
                    
                    if new_fitness != player.fitness_level:
                        player.fitness_level = new_fitness
                        player.save(update_fields=['fitness_level'])
                        
                        self.logger.info(f"Daily fitness update for {player.full_name}: {player.fitness_level}")
    
    def generate_fitness_report(self, days=30):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        report = {
            'report_period': days,
            'generated_at': timezone.now().isoformat(),
            'squad_overview': self.get_squad_fitness_overview(),
            'fitness_trends': [],
            'injury_analysis': self._analyse_recent_injuries(cutoff_date),
            'workload_analysis': self._analyse_squad_workload(cutoff_date),
            'recommendations': []
        }
        
        active_players = Player.objects.filter(is_active=True)
        
        for player in active_players:
            fitness_trend = self._calculate_fitness_trend(player, days)
            if fitness_trend['data_points']:
                report['fitness_trends'].append({
                    'player': player.full_name,
                    'position': player.position,
                    'trend': fitness_trend['trend'],
                    'change_rate': fitness_trend['change_rate']
                })
        
        report['recommendations'] = self._generate_squad_recommendations(report)
        
        return report
    
    def _analyse_recent_injuries(self, cutoff_date):
        injuries = MatchEvent.objects.filter(
            event_type='INJURY',
            match__scheduled_datetime__gte=cutoff_date
        ).select_related('player', 'match')
        
        injury_by_position = {}
        injury_by_player = {}
        
        for injury in injuries:
            position = injury.player.position
            player_name = injury.player.full_name
            
            injury_by_position[position] = injury_by_position.get(position, 0) + 1
            injury_by_player[player_name] = injury_by_player.get(player_name, 0) + 1
        
        return {
            'total_injuries': injuries.count(),
            'injuries_by_position': injury_by_position,
            'players_with_multiple_injuries': {
                player: count for player, count in injury_by_player.items() if count > 1
            }
        }
    
    def _analyse_squad_workload(self, cutoff_date):
        recent_matches = Match.objects.filter(
            scheduled_datetime__gte=cutoff_date,
            status__in=['COMPLETED', 'FULL_TIME']
        )
        
        total_minutes = PlayerStats.objects.filter(
            match__in=recent_matches
        ).aggregate(total=Sum('minutes_played'))['total'] or 0
        
        avg_minutes_per_match = total_minutes / max(recent_matches.count(), 1)
        
        return {
            'total_matches': recent_matches.count(),
            'total_minutes_played': total_minutes,
            'average_minutes_per_match': round(avg_minutes_per_match, 1),
            'squad_rotation_rate': self._calculate_rotation_rate(recent_matches)
        }
    
    def _calculate_rotation_rate(self, matches):
        if matches.count() < 2:
            return 0
        
        total_changes = 0
        previous_lineup = None
        
        for match in matches.order_by('scheduled_datetime'):
            current_lineup = set(
                PlayerStats.objects.filter(match=match).values_list('player_id', flat=True)
            )
            
            if previous_lineup:
                changes = len(current_lineup.symmetric_difference(previous_lineup))
                total_changes += changes
            
            previous_lineup = current_lineup
        
        return round(total_changes / max(matches.count() - 1, 1), 1)
    
    def _generate_squad_recommendations(self, report):
        recommendations = []
        
        squad_overview = report['squad_overview']
        
        if squad_overview['availability_percentage'] < 80:
            recommendations.append({
                'priority': 'high',
                'category': 'availability',
                'recommendation': 'Squad availability below 80% - consider injury prevention measures'
            })
        
        if squad_overview['fitness_distribution']['poor'] + squad_overview['fitness_distribution']['critical'] > 3:
            recommendations.append({
                'priority': 'high',
                'category': 'fitness',
                'recommendation': 'Multiple players with poor fitness - implement squad-wide fitness programme'
            })
        
        if len(squad_overview['high_risk_players']) > 2:
            recommendations.append({
                'priority': 'medium',
                'category': 'injury_prevention',
                'recommendation': 'High number of at-risk players - enhance injury prevention protocols'
            })
        
        return recommendations