from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

class Player(models.Model):
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('CB', 'Centre Back'),
        ('LB', 'Left Back'),
        ('RB', 'Right Back'),
        ('CDM', 'Centre Defensive Midfielder'),
        ('CM', 'Centre Midfielder'),
        ('CAM', 'Centre Attacking Midfielder'),
        ('LM', 'Left Midfielder'),
        ('RM', 'Right Midfielder'),
        ('LW', 'Left Winger'),
        ('RW', 'Right Winger'),
        ('ST', 'Striker'),
    ]
    
    FOOT_CHOICES = [
        ('L', 'Left'),
        ('R', 'Right'),
        ('B', 'Both'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    squad_number = models.PositiveIntegerField(unique=True, validators=[MinValueValidator(1), MaxValueValidator(99)])
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.CharField(max_length=3, choices=POSITION_CHOICES)
    preferred_foot = models.CharField(max_length=1, choices=FOOT_CHOICES, default='R')
    date_of_birth = models.DateField()
    height = models.PositiveIntegerField(help_text='Height in centimetres')
    weight = models.PositiveIntegerField(help_text='Weight in kilograms')
    market_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    contract_expiry = models.DateField()
    is_active = models.BooleanField(default=True)
    is_injured = models.BooleanField(default=False)
    fitness_level = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'players'
        ordering = ['squad_number']
        indexes = [
            models.Index(fields=['position']),
            models.Index(fields=['is_active']),
            models.Index(fields=['squad_number']),
        ]

    def __str__(self):
        return f"{self.squad_number}. {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        return (timezone.now().date() - self.date_of_birth).days // 365

class Opponent(models.Model):
    name = models.CharField(max_length=100, unique=True)
    league = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    typical_formation = models.CharField(max_length=10, default='4-4-2')
    playing_style = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'opponents'
        ordering = ['name']

    def __str__(self):
        return self.name

class Match(models.Model):
    MATCH_TYPE_CHOICES = [
        ('LEAGUE', 'Premier League'),
        ('UCL', 'UEFA Champions League'),
        ('UEL', 'UEFA Europa League'),
        ('FA', 'FA Cup'),
        ('CARABAO', 'Carabao Cup'),
        ('FRIENDLY', 'Friendly'),
        ('TRAINING', 'Training Match'),
    ]
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('LIVE', 'Live'),
        ('HALF_TIME', 'Half Time'),
        ('FULL_TIME', 'Full Time'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opponent = models.ForeignKey(Opponent, on_delete=models.CASCADE, related_name='matches_against')
    match_type = models.CharField(max_length=20, choices=MATCH_TYPE_CHOICES)
    is_home = models.BooleanField(default=True)
    scheduled_datetime = models.DateTimeField()
    actual_kickoff = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    chelsea_score = models.PositiveIntegerField(default=0)
    opponent_score = models.PositiveIntegerField(default=0)
    venue = models.CharField(max_length=100, default='Stamford Bridge')
    attendance = models.PositiveIntegerField(null=True, blank=True)
    weather_conditions = models.CharField(max_length=100, blank=True)
    referee = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'matches'
        ordering = ['-scheduled_datetime']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['match_type']),
            models.Index(fields=['scheduled_datetime']),
        ]

    def __str__(self):
        home_away = 'vs' if self.is_home else 'at'
        return f"Chelsea {home_away} {self.opponent.name} - {self.scheduled_datetime.strftime('%d/%m/%Y')}"

    @property
    def result(self):
        if self.status not in ['FULL_TIME', 'COMPLETED']:
            return 'TBD'
        if self.chelsea_score > self.opponent_score:
            return 'WIN'
        elif self.chelsea_score < self.opponent_score:
            return 'LOSS'
        return 'DRAW'

class Formation(models.Model):
    name = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    defensive_line = models.PositiveIntegerField()
    midfield_line = models.PositiveIntegerField()
    attacking_line = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'formations'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_outfield_players(self):
        return self.defensive_line + self.midfield_line + self.attacking_line

class FormationPosition(models.Model):
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='positions')
    position = models.CharField(max_length=3)
    x_coordinate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    y_coordinate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    is_core_position = models.BooleanField(default=True)

    class Meta:
        db_table = 'formation_positions'
        unique_together = ['formation', 'position', 'x_coordinate', 'y_coordinate']

class MatchLineup(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='lineups')
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    is_starting_eleven = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'match_lineups'
        unique_together = ['match', 'is_starting_eleven']

class MatchLineupPlayer(models.Model):
    lineup = models.ForeignKey(MatchLineup, on_delete=models.CASCADE, related_name='lineup_players')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    position = models.CharField(max_length=3)
    is_captain = models.BooleanField(default=False)
    minutes_played = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(120)])

    class Meta:
        db_table = 'match_lineup_players'
        unique_together = ['lineup', 'player']

class PlayerStats(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='stats')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='player_stats')
    minutes_played = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(120)])
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    passes_completed = models.PositiveIntegerField(default=0)
    passes_attempted = models.PositiveIntegerField(default=0)
    pass_accuracy = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    distance_covered = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    sprints = models.PositiveIntegerField(default=0)
    top_speed = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    tackles_won = models.PositiveIntegerField(default=0)
    tackles_attempted = models.PositiveIntegerField(default=0)
    interceptions = models.PositiveIntegerField(default=0)
    clearances = models.PositiveIntegerField(default=0)
    shots_on_target = models.PositiveIntegerField(default=0)
    shots_off_target = models.PositiveIntegerField(default=0)
    shots_blocked = models.PositiveIntegerField(default=0)
    crosses_completed = models.PositiveIntegerField(default=0)
    crosses_attempted = models.PositiveIntegerField(default=0)
    fouls_committed = models.PositiveIntegerField(default=0)
    fouls_won = models.PositiveIntegerField(default=0)
    yellow_cards = models.PositiveIntegerField(default=0)
    red_cards = models.PositiveIntegerField(default=0)
    offsides = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    class Meta:
        db_table = 'player_stats'
        unique_together = ['player', 'match']
        indexes = [
            models.Index(fields=['player', 'match']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"{self.player.full_name} - {self.match}"

class TeamStats(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='team_stats')
    possession_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=50)
    total_passes = models.PositiveIntegerField(default=0)
    pass_accuracy = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    shots_total = models.PositiveIntegerField(default=0)
    shots_on_target = models.PositiveIntegerField(default=0)
    shots_off_target = models.PositiveIntegerField(default=0)
    corners = models.PositiveIntegerField(default=0)
    offsides = models.PositiveIntegerField(default=0)
    fouls_committed = models.PositiveIntegerField(default=0)
    yellow_cards = models.PositiveIntegerField(default=0)
    red_cards = models.PositiveIntegerField(default=0)
    distance_covered_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    sprints_total = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'team_stats'

class MatchEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('GOAL', 'Goal'),
        ('ASSIST', 'Assist'),
        ('YELLOW_CARD', 'Yellow Card'),
        ('RED_CARD', 'Red Card'),
        ('SUBSTITUTION', 'Substitution'),
        ('CORNER', 'Corner'),
        ('OFFSIDE', 'Offside'),
        ('FOUL', 'Foul'),
        ('PENALTY', 'Penalty'),
        ('SAVE', 'Save'),
        ('INJURY', 'Injury'),
    ]

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='events')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    minute = models.PositiveIntegerField(validators=[MaxValueValidator(120)])
    description = models.TextField(blank=True)
    x_coordinate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    y_coordinate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'match_events'
        ordering = ['minute', 'created_at']
        indexes = [
            models.Index(fields=['match', 'minute']),
            models.Index(fields=['event_type']),
        ]

class Analytics(models.Model):
    ANALYSIS_TYPE_CHOICES = [
        ('PLAYER_PERFORMANCE', 'Player Performance'),
        ('FORMATION_EFFECTIVENESS', 'Formation Effectiveness'),
        ('TACTICAL_ANALYSIS', 'Tactical Analysis'),
        ('OPPOSITION_ANALYSIS', 'Opposition Analysis'),
        ('TREND_ANALYSIS', 'Trend Analysis'),
        ('PREDICTION', 'Prediction'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis_type = models.CharField(max_length=30, choices=ANALYSIS_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    data_points = models.JSONField(default=dict)
    insights = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    related_match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics')
    related_player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics')
    related_formation = models.ForeignKey(Formation, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'analytics'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['analysis_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['confidence_score']),
        ]

    def __str__(self):
        return f"{self.analysis_type}: {self.title}"