from django.db import models
from django.db.models import Q, Avg, Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

class PlayerManager(models.Manager):
    
    def active_players(self):
        return self.filter(is_active=True)
    
    def fit_players(self):
        return self.filter(is_active=True, is_injured=False)
    
    def injured_players(self):
        return self.filter(is_active=True, is_injured=True)
    
    def by_position(self, position):
        return self.filter(position=position, is_active=True)
    
    def high_fitness(self, threshold=90):
        return self.filter(fitness_level__gte=threshold, is_active=True)
    
    def contract_expiring_soon(self, months=6):
        cutoff_date = timezone.now().date() + timedelta(days=months * 30)
        return self.filter(contract_expiry__lte=cutoff_date, is_active=True)
    
    def young_players(self, max_age=23):
        cutoff_birth_date = timezone.now().date() - timedelta(days=max_age * 365)
        return self.filter(date_of_birth__gte=cutoff_birth_date, is_active=True)
    
    def experienced_players(self, min_age=28):
        cutoff_birth_date = timezone.now().date() - timedelta(days=min_age * 365)
        return self.filter(date_of_birth__lte=cutoff_birth_date, is_active=True)

class MatchManager(models.Manager):
    
    def completed_matches(self):
        return self.filter(status__in=['COMPLETED', 'FULL_TIME'])
    
    def upcoming_matches(self):
        return self.filter(status='SCHEDULED', scheduled_datetime__gte=timezone.now())
    
    def recent_matches(self, days=30):
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(
            scheduled_datetime__gte=cutoff_date,
            status__in=['COMPLETED', 'FULL_TIME']
        )
    
    def home_matches(self):
        return self.filter(is_home=True)
    
    def away_matches(self):
        return self.filter(is_home=False)
    
    def wins(self):
        return self.filter(result='WIN')
    
    def losses(self):
        return self.filter(result='LOSS')
    
    def draws(self):
        return self.filter(result='DRAW')
    
    def by_competition(self, match_type):
        return self.filter(match_type=match_type)
    
    def against_opponent(self, opponent):
        return self.filter(opponent=opponent)
    
    def high_scoring(self, min_total_goals=4):
        return self.filter(chelsea_score__gte=min_total_goals)
    
    def clean_sheets(self):
        return self.filter(opponent_score=0)
    
    def failed_to_score(self):
        return self.filter(chelsea_score=0)
    
    def current_season(self, season_start=None):
        if not season_start:
            season_start = timezone.now().date() - timedelta(days=180)
        return self.filter(scheduled_datetime__date__gte=season_start)

class PlayerStatsManager(models.Manager):
    
    def for_player(self, player):
        return self.filter(player=player)
    
    def recent_performances(self, player, days=30):
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(
            player=player,
            match__scheduled_datetime__gte=cutoff_date,
            match__status__in=['COMPLETED', 'FULL_TIME']
        )
    
    def high_rated_performances(self, min_rating=8.0):
        return self.filter(rating__gte=min_rating)
    
    def goal_scorers(self, match=None):
        queryset = self.filter(goals__gt=0)
        if match:
            queryset = queryset.filter(match=match)
        return queryset
    
    def assist_providers(self, match=None):
        queryset = self.filter(assists__gt=0)
        if match:
            queryset = queryset.filter(match=match)
        return queryset
    
    def defensive_performers(self, min_actions=3):
        return self.filter(
            models.Q(tackles__gte=min_actions) | 
            models.Q(interceptions__gte=min_actions)
        )
    
    def match_statistics(self, match):
        return self.filter(match=match)
    
    def season_statistics(self, player, season_start=None):
        if not season_start:
            season_start = timezone.now().date() - timedelta(days=180)
        return self.filter(
            player=player,
            match__scheduled_datetime__date__gte=season_start,
            match__status__in=['COMPLETED', 'FULL_TIME']
        )

class FormationManager(models.Manager):
    
    def active_formations(self):
        return self.filter(is_active=True)
    
    def by_style(self, defensive_line_count):
        return self.filter(defensive_line=defensive_line_count, is_active=True)
    
    def attacking_formations(self):
        return self.filter(attacking_line__gte=3, is_active=True)
    
    def defensive_formations(self):
        return self.filter(defensive_line__gte=5, is_active=True)
    
    def balanced_formations(self):
        return self.filter(defensive_line=4, midfield_line=4, is_active=True)
    
    def recently_used(self, days=60):
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(
            lineups__match__scheduled_datetime__gte=cutoff_date,
            lineups__is_starting_eleven=True,
            is_active=True
        ).distinct()
    
    def most_successful(self, min_matches=3):
        formations_with_stats = self.filter(is_active=True).annotate(
            total_matches=Count('lineups__match', filter=Q(
                lineups__is_starting_eleven=True,
                lineups__match__status__in=['COMPLETED', 'FULL_TIME']
            )),
            total_wins=Count('lineups__match', filter=Q(
                lineups__is_starting_eleven=True,
                lineups__match__result='WIN'
            ))
        ).filter(total_matches__gte=min_matches)
        
        return formations_with_stats.extra(
            select={'win_rate': 'CAST(total_wins AS FLOAT) / CAST(total_matches AS FLOAT)'}
        ).order_by('-win_rate')

class MatchLineupManager(models.Manager):
    
    def starting_lineups(self):
        return self.filter(is_starting_eleven=True)
    
    def substitute_lineups(self):
        return self.filter(is_starting_eleven=False)
    
    def for_match(self, match):
        return self.filter(match=match)
    
    def with_formation(self, formation):
        return self.filter(formation=formation)
    
    def recent_lineups(self, days=30):
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(
            match__scheduled_datetime__gte=cutoff_date,
            match__status__in=['COMPLETED', 'FULL_TIME']
        )
    
    def successful_lineups(self):
        return self.filter(match__result='WIN', is_starting_eleven=True)

class TeamStatsManager(models.Manager):
    
    def for_match(self, match):
        return self.filter(match=match)
    
    def recent_stats(self, days=30):
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(
            match__scheduled_datetime__gte=cutoff_date,
            match__status__in=['COMPLETED', 'FULL_TIME']
        )
    
    def high_possession_games(self, min_possession=60):
        return self.filter(possession_percentage__gte=min_possession)
    
    def low_possession_games(self, max_possession=40):
        return self.filter(possession_percentage__lte=max_possession)
    
    def attacking_performances(self, min_shots=15):
        return self.filter(
            shots_on_target__gte=min_shots / 2,
            shots_off_target__gte=min_shots / 4
        )
    
    def defensive_performances(self):
        return self.filter(match__opponent_score=0)

class AnalyticsManager(models.Manager):
    
    def by_type(self, analysis_type):
        return self.filter(analysis_type=analysis_type)
    
    def recent_analytics(self, days=30):
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date)
    
    def high_confidence(self, min_confidence=80):
        return self.filter(confidence_score__gte=min_confidence)
    
    def for_player(self, player):
        return self.filter(related_player=player)
    
    def for_match(self, match):
        return self.filter(related_match=match)
    
    def for_formation(self, formation):
        return self.filter(related_formation=formation)
    
    def player_performance_analytics(self):
        return self.filter(analysis_type='PLAYER_PERFORMANCE')
    
    def tactical_analytics(self):
        return self.filter(analysis_type='TACTICAL_ANALYSIS')
    
    def formation_analytics(self):
        return self.filter(analysis_type='FORMATION_EFFECTIVENESS')
    
    def trend_analytics(self):
        return self.filter(analysis_type='TREND_ANALYSIS')
    
    def predictions(self):
        return self.filter(analysis_type='PREDICTION')

class OpponentManager(models.Manager):
    
    def by_league(self, league):
        return self.filter(league__icontains=league)
    
    def by_country(self, country):
        return self.filter(country=country)
    
    def recent_opponents(self, days=90):
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(
            matches_against__scheduled_datetime__gte=cutoff_date,
            matches_against__status__in=['COMPLETED', 'FULL_TIME']
        ).distinct()
    
    def challenging_opponents(self, max_win_rate=50):
        return self.annotate(
            total_matches=Count('matches_against', filter=Q(
                matches_against__status__in=['COMPLETED', 'FULL_TIME']
            )),
            total_wins=Count('matches_against', filter=Q(
                matches_against__result='WIN'
            ))
        ).filter(total_matches__gte=2).extra(
            select={'win_rate': 'CAST(total_wins AS FLOAT) / CAST(total_matches AS FLOAT) * 100'}
        ).extra(where=['win_rate <= %s'], params=[max_win_rate])
    
    def frequent_opponents(self, min_matches=3):
        return self.annotate(
            match_count=Count('matches_against', filter=Q(
                matches_against__status__in=['COMPLETED', 'FULL_TIME']
            ))
        ).filter(match_count__gte=min_matches)

class MatchEventManager(models.Manager):
    
    def for_match(self, match):
        return self.filter(match=match)
    
    def goals(self, match=None):
        queryset = self.filter(event_type='GOAL')
        if match:
            queryset = queryset.filter(match=match)
        return queryset
    
    def cards(self, match=None):
        queryset = self.filter(event_type__in=['YELLOW_CARD', 'RED_CARD'])
        if match:
            queryset = queryset.filter(match=match)
        return queryset
    
    def substitutions(self, match=None):
        queryset = self.filter(event_type='SUBSTITUTION')
        if match:
            queryset = queryset.filter(match=match)
        return queryset
    
    def first_half_events(self, match=None):
        queryset = self.filter(minute__lte=45)
        if match:
            queryset = queryset.filter(match=match)
        return queryset
    
    def second_half_events(self, match=None):
        queryset = self.filter(minute__gt=45)
        if match:
            queryset = queryset.filter(match=match)
        return queryset
    
    def key_events(self, match=None):
        queryset = self.filter(event_type__in=['GOAL', 'RED_CARD', 'PENALTY'])
        if match:
            queryset = queryset.filter(match=match)
        return queryset
    
    def by_player(self, player):
        return self.filter(player=player)
    
    def recent_events(self, days=30):
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(
            match__scheduled_datetime__gte=cutoff_date,
            match__status__in=['COMPLETED', 'FULL_TIME']
        )