from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Player, Match, PlayerStats, TeamStats, MatchEvent, Analytics, Formation, MatchLineup
from .exceptions import ValidationError

logger = logging.getLogger('core.performance')

@receiver(post_save, sender=Player)
def player_post_save(sender, instance, created, **kwargs):
    if created:
        logger.info(f"New player created: {instance.full_name} (#{instance.squad_number})")
        
        Analytics.objects.create(
            analysis_type='PLAYER_PERFORMANCE',
            title=f'New Player Registration: {instance.full_name}',
            description=f'Player {instance.full_name} has been registered with squad number {instance.squad_number}',
            related_player=instance,
            confidence_score=100,
            insights=[f'New {instance.position} player added to squad'],
            recommendations=[f'Monitor {instance.full_name} integration into team tactics']
        )
    else:
        if instance.is_injured:
            logger.warning(f"Player injury updated: {instance.full_name} - Injured: {instance.is_injured}")
        
        if instance.fitness_level < 75:
            logger.warning(f"Low fitness alert: {instance.full_name} - Fitness: {instance.fitness_level}%")
    
    cache.delete('active_players_list')
    cache.delete('squad_overview')

@receiver(pre_save, sender=Player)
def player_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Player.objects.get(pk=instance.pk)
            
            if old_instance.squad_number != instance.squad_number:
                logger.info(f"Squad number change: {instance.full_name} from #{old_instance.squad_number} to #{instance.squad_number}")
            
            if old_instance.is_injured != instance.is_injured:
                injury_status = "injured" if instance.is_injured else "recovered"
                logger.info(f"Injury status change: {instance.full_name} is now {injury_status}")
                
                Analytics.objects.create(
                    analysis_type='PLAYER_PERFORMANCE',
                    title=f'Injury Status Update: {instance.full_name}',
                    description=f'Player injury status changed to: {injury_status}',
                    related_player=instance,
                    confidence_score=100,
                    insights=[f'Injury status: {injury_status}'],
                    recommendations=[f'Adjust training and match planning for {instance.full_name}']
                )
                
        except Player.DoesNotExist:
            pass

@receiver(post_save, sender=Match)
def match_post_save(sender, instance, created, **kwargs):
    if created:
        logger.info(f"New match created: Chelsea vs {instance.opponent.name} on {instance.scheduled_datetime}")
    else:
        if instance.status in ['COMPLETED', 'FULL_TIME']:
            logger.info(f"Match completed: Chelsea {instance.chelsea_score}-{instance.opponent_score} {instance.opponent.name}")
            
            Analytics.objects.create(
                analysis_type='TACTICAL_ANALYSIS',
                title=f'Match Result: Chelsea vs {instance.opponent.name}',
                description=f'Match completed with result: {instance.result} ({instance.chelsea_score}-{instance.opponent_score})',
                related_match=instance,
                confidence_score=95,
                insights=[
                    f'Result: {instance.result}',
                    f'Goals scored: {instance.chelsea_score}',
                    f'Goals conceded: {instance.opponent_score}'
                ],
                recommendations=generate_match_recommendations(instance)
            )
    
    cache.delete('recent_matches')
    cache.delete('upcoming_fixtures')
    cache.delete('season_statistics')

@receiver(post_save, sender=PlayerStats)
def player_stats_post_save(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Player stats recorded: {instance.player.full_name} - Rating: {instance.rating}")
        
        if instance.rating >= 9.0:
            Analytics.objects.create(
                analysis_type='PLAYER_PERFORMANCE',
                title=f'Outstanding Performance: {instance.player.full_name}',
                description=f'Exceptional performance with rating of {instance.rating}/10',
                related_player=instance.player,
                related_match=instance.match,
                confidence_score=100,
                insights=[
                    f'Rating: {instance.rating}/10',
                    f'Goals: {instance.goals}',
                    f'Assists: {instance.assists}'
                ],
                recommendations=[f'Continue current form and tactical approach for {instance.player.full_name}']
            )
        
        elif instance.rating <= 5.0:
            Analytics.objects.create(
                analysis_type='PLAYER_PERFORMANCE',
                title=f'Performance Concern: {instance.player.full_name}',
                description=f'Below average performance with rating of {instance.rating}/10',
                related_player=instance.player,
                related_match=instance.match,
                confidence_score=95,
                insights=[
                    f'Low rating: {instance.rating}/10',
                    f'Performance needs improvement'
                ],
                recommendations=[
                    f'Review training approach for {instance.player.full_name}',
                    'Consider tactical adjustments or position change'
                ]
            )
    
    cache.delete(f'player_performance_{instance.player.id}')
    cache.delete('top_performers')

@receiver(post_save, sender=TeamStats)
def team_stats_post_save(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Team stats recorded for match: {instance.match}")
        
        if instance.possession_percentage and instance.possession_percentage >= 70:
            logger.info(f"High possession game: {instance.possession_percentage}%")
        
        shots_total = instance.shots_on_target + instance.shots_off_target + instance.shots_blocked
        if shots_total >= 20:
            Analytics.objects.create(
                analysis_type='TACTICAL_ANALYSIS',
                title=f'High Shot Volume: {instance.match}',
                description=f'Team recorded {shots_total} total shots in the match',
                related_match=instance.match,
                confidence_score=90,
                insights=[
                    f'Total shots: {shots_total}',
                    f'Shots on target: {instance.shots_on_target}',
                    f'Shot accuracy: {(instance.shots_on_target/shots_total)*100:.1f}%'
                ],
                recommendations=['Continue aggressive attacking approach']
            )
    
    cache.delete('team_performance_stats')

@receiver(post_save, sender=MatchEvent)
def match_event_post_save(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Match event recorded: {instance.event_type} - {instance.player.full_name if instance.player else 'Unknown'} at {instance.minute}'")
        
        if instance.event_type == 'GOAL':
            logger.info(f"Goal scored by {instance.player.full_name} at {instance.minute}'")
        
        elif instance.event_type == 'RED_CARD':
            logger.warning(f"Red card: {instance.player.full_name} at {instance.minute}'")
            
            Analytics.objects.create(
                analysis_type='TACTICAL_ANALYSIS',
                title=f'Red Card Impact: {instance.match}',
                description=f'{instance.player.full_name} received red card at {instance.minute} minutes',
                related_match=instance.match,
                related_player=instance.player,
                confidence_score=100,
                insights=[
                    f'Red card at {instance.minute} minutes',
                    'Team reduced to 10 players',
                    'Tactical adjustment required'
                ],
                recommendations=[
                    'Implement defensive tactical changes',
                    'Focus on maintaining discipline'
                ]
            )
    
    cache.delete(f'match_events_{instance.match.id}')

@receiver(post_save, sender=Formation)
def formation_post_save(sender, instance, created, **kwargs):
    if created:
        logger.info(f"New formation created: {instance.name}")
        
        Analytics.objects.create(
            analysis_type='FORMATION_EFFECTIVENESS',
            title=f'New Formation: {instance.name}',
            description=f'New tactical formation {instance.name} added to system',
            related_formation=instance,
            confidence_score=80,
            insights=[
                f'Formation structure: {instance.name}',
                f'Defensive line: {instance.defensive_line}',
                f'Midfield line: {instance.midfield_line}',
                f'Attacking line: {instance.attacking_line}'
            ],
            recommendations=[f'Test {instance.name} formation in training and friendly matches']
        )
    
    cache.delete('available_formations')

@receiver(post_save, sender=MatchLineup)
def match_lineup_post_save(sender, instance, created, **kwargs):
    if created and instance.is_starting_eleven:
        logger.info(f"Starting lineup set for {instance.match}: Formation {instance.formation.name}")
        
        Analytics.objects.create(
            analysis_type='TACTICAL_ANALYSIS',
            title=f'Formation Selection: {instance.match}',
            description=f'Formation {instance.formation.name} selected for match against {instance.match.opponent.name}',
            related_match=instance.match,
            related_formation=instance.formation,
            confidence_score=85,
            insights=[
                f'Formation used: {instance.formation.name}',
                f'Starting eleven confirmed'
            ],
            recommendations=[f'Monitor effectiveness of {instance.formation.name} against {instance.match.opponent.name}']
        )
    
    cache.delete(f'match_lineup_{instance.match.id}')

@receiver(post_delete, sender=Player)
def player_post_delete(sender, instance, **kwargs):
    logger.info(f"Player removed from system: {instance.full_name}")
    
    cache.delete('active_players_list')
    cache.delete('squad_overview')

@receiver(post_delete, sender=Match)
def match_post_delete(sender, instance, **kwargs):
    logger.info(f"Match removed from system: Chelsea vs {instance.opponent.name}")
    
    cache.delete('recent_matches')
    cache.delete('upcoming_fixtures')
    cache.delete('season_statistics')

def generate_match_recommendations(match):
    recommendations = []
    
    if match.result == 'WIN':
        recommendations.append('Continue current tactical approach')
        if match.chelsea_score >= 3:
            recommendations.append('Maintain attacking intensity')
    
    elif match.result == 'LOSS':
        recommendations.append('Review tactical approach and team selection')
        if match.opponent_score >= 3:
            recommendations.append('Focus on defensive organization in training')
    
    else:  # DRAW
        recommendations.append('Analyze missed opportunities for converting draws to wins')
    
    if match.chelsea_score == 0:
        recommendations.append('Improve attacking patterns and finishing')
    
    if match.opponent_score >= 2:
        recommendations.append('Strengthen defensive transitions')
    
    return recommendations

@receiver(post_save, sender=Analytics)
def analytics_post_save(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Analytics created: {instance.analysis_type} - {instance.title}")
        
        if instance.confidence_score >= 90:
            logger.info(f"High confidence analytics: {instance.title} ({instance.confidence_score}%)")
    
    cache.delete('recent_analytics')
    cache.delete('high_confidence_analytics')

def clear_player_related_cache(player_id):
    cache_keys = [
        f'player_performance_{player_id}',
        f'player_stats_{player_id}',
        f'player_analytics_{player_id}',
        'active_players_list',
        'squad_overview',
        'top_performers'
    ]
    
    for key in cache_keys:
        cache.delete(key)

def clear_match_related_cache(match_id):
    cache_keys = [
        f'match_analysis_{match_id}',
        f'match_stats_{match_id}',
        f'match_events_{match_id}',
        f'match_lineup_{match_id}',
        'recent_matches',
        'season_statistics'
    ]
    
    for key in cache_keys:
        cache.delete(key)

def clear_formation_related_cache(formation_id):
    cache_keys = [
        f'formation_analysis_{formation_id}',
        f'formation_effectiveness_{formation_id}',
        'available_formations',
        'formation_statistics'
    ]
    
    for key in cache_keys:
        cache.delete(key)

@receiver(post_save, sender=Player)
def update_fitness_alerts(sender, instance, **kwargs):
    if instance.fitness_level < 70:
        logger.warning(f"Fitness alert: {instance.full_name} fitness level is {instance.fitness_level}%")
        
        create_fitness_alert(instance)

@receiver(post_save, sender=Match)
def update_match_preparation_alerts(sender, instance, created, **kwargs):
    if instance.status == 'SCHEDULED':
        days_until_match = (instance.scheduled_datetime.date() - timezone.now().date()).days
        
        if days_until_match <= 3 and days_until_match > 0:
            logger.info(f"Match preparation alert: {days_until_match} days until Chelsea vs {instance.opponent.name}")
            
            create_match_preparation_alert(instance, days_until_match)

def create_fitness_alert(player):
    Analytics.objects.create(
        analysis_type='PLAYER_PERFORMANCE',
        title=f'Fitness Alert: {player.full_name}',
        description=f'Player fitness level is below recommended threshold at {player.fitness_level}%',
        related_player=player,
        confidence_score=100,
        insights=[
            f'Current fitness: {player.fitness_level}%',
            'Below recommended threshold of 70%',
            'Risk of injury or poor performance'
        ],
        recommendations=[
            f'Adjust training intensity for {player.full_name}',
            'Monitor recovery and rest periods',
            'Consider reduced playing time until fitness improves'
        ]
    )

def create_match_preparation_alert(match, days_until):
    Analytics.objects.create(
        analysis_type='TACTICAL_ANALYSIS',
        title=f'Match Preparation: Chelsea vs {match.opponent.name}',
        description=f'Upcoming match in {days_until} days requires preparation focus',
        related_match=match,
        confidence_score=90,
        insights=[
            f'Match in {days_until} days',
            f'Opponent: {match.opponent.name}',
            f'Venue: {"Home" if match.is_home else "Away"}'
        ],
        recommendations=[
            'Finalize tactical preparation',
            'Confirm squad fitness levels',
            'Review opponent analysis',
            'Plan formation and lineup'
        ]
    )

@receiver(post_save, sender=PlayerStats)
def monitor_performance_trends(sender, instance, created, **kwargs):
    if created and instance.rating <= 4.5:
        recent_poor_performances = PlayerStats.objects.filter(
            player=instance.player,
            match__scheduled_datetime__gte=timezone.now() - timedelta(days=30),
            rating__lte=5.0
        ).count()
        
        if recent_poor_performances >= 3:
            Analytics.objects.create(
                analysis_type='PLAYER_PERFORMANCE',
                title=f'Performance Trend Alert: {instance.player.full_name}',
                description=f'Multiple poor performances detected in recent matches',
                related_player=instance.player,
                confidence_score=95,
                insights=[
                    f'Recent poor performances: {recent_poor_performances}',
                    f'Latest rating: {instance.rating}/10',
                    'Declining performance trend'
                ],
                recommendations=[
                    f'Individual performance review for {instance.player.full_name}',
                    'Consider tactical role adjustment',
                    'Evaluate training and preparation methods',
                    'Possible rest period to regain form'
                ]
            )

@receiver(post_save, sender=Match)
def analyze_result_patterns(sender, instance, **kwargs):
    if instance.status in ['COMPLETED', 'FULL_TIME']:
        recent_matches = Match.objects.filter(
            scheduled_datetime__gte=timezone.now() - timedelta(days=30),
            status__in=['COMPLETED', 'FULL_TIME']
        ).order_by('-scheduled_datetime')[:5]
        
        if recent_matches.count() >= 5:
            recent_wins = recent_matches.filter(result='WIN').count()
            recent_losses = recent_matches.filter(result='LOSS').count()
            
            if recent_losses >= 3:
                Analytics.objects.create(
                    analysis_type='TREND_ANALYSIS',
                    title='Performance Concern: Recent Form',
                    description=f'Poor recent form with {recent_losses} losses in last 5 matches',
                    confidence_score=95,
                    insights=[
                        f'Recent wins: {recent_wins}',
                        f'Recent losses: {recent_losses}',
                        'Concerning trend developing'
                    ],
                    recommendations=[
                        'Comprehensive tactical review required',
                        'Analyze recent match patterns',
                        'Consider formation and personnel changes',
                        'Focus on confidence building in training'
                    ]
                )
            
            elif recent_wins >= 4:
                Analytics.objects.create(
                    analysis_type='TREND_ANALYSIS',
                    title='Positive Momentum: Strong Form',
                    description=f'Excellent recent form with {recent_wins} wins in last 5 matches',
                    confidence_score=95,
                    insights=[
                        f'Recent wins: {recent_wins}',
                        f'Recent losses: {recent_losses}',
                        'Strong positive momentum'
                    ],
                    recommendations=[
                        'Maintain current tactical approach',
                        'Keep successful team selection',
                        'Build on current confidence levels'
                    ]
                )