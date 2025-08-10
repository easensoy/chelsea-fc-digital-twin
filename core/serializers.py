from rest_framework import serializers
from .models import (
    Player, Match, Formation, Opponent, Analytics, PlayerStats, 
    TeamStats, MatchEvent, MatchLineup, MatchLineupPlayer, FormationPosition
)

class PlayerSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Player
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class OpponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opponent
        fields = '__all__'
        read_only_fields = ['created_at']

class MatchSerializer(serializers.ModelSerializer):
    opponent_name = serializers.CharField(source='opponent.name', read_only=True)
    result = serializers.ReadOnlyField()
    
    class Meta:
        model = Match
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class FormationPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormationPosition
        fields = '__all__'

class FormationSerializer(serializers.ModelSerializer):
    positions = FormationPositionSerializer(many=True, read_only=True)
    total_outfield_players = serializers.ReadOnlyField()
    
    class Meta:
        model = Formation
        fields = '__all__'
        read_only_fields = ['created_at']

class MatchLineupPlayerSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source='player.full_name', read_only=True)
    squad_number = serializers.IntegerField(source='player.squad_number', read_only=True)
    
    class Meta:
        model = MatchLineupPlayer
        fields = '__all__'

class MatchLineupSerializer(serializers.ModelSerializer):
    lineup_players = MatchLineupPlayerSerializer(many=True, read_only=True)
    formation_name = serializers.CharField(source='formation.name', read_only=True)
    
    class Meta:
        model = MatchLineup
        fields = '__all__'
        read_only_fields = ['created_at']

class PlayerStatsSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source='player.full_name', read_only=True)
    match_info = serializers.CharField(source='match.__str__', read_only=True)
    
    class Meta:
        model = PlayerStats
        fields = '__all__'

class TeamStatsSerializer(serializers.ModelSerializer):
    match_info = serializers.CharField(source='match.__str__', read_only=True)
    
    class Meta:
        model = TeamStats
        fields = '__all__'

class MatchEventSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source='player.full_name', read_only=True)
    
    class Meta:
        model = MatchEvent
        fields = '__all__'
        read_only_fields = ['created_at']

class AnalyticsSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    related_match_info = serializers.CharField(source='related_match.__str__', read_only=True)
    related_player_name = serializers.CharField(source='related_player.full_name', read_only=True)
    related_formation_name = serializers.CharField(source='related_formation.name', read_only=True)
    
    class Meta:
        model = Analytics
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']