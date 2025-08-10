from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Avg, Sum, Count

from .models import (
    Player, Opponent, Match, Formation, FormationPosition, MatchLineup, 
    MatchLineupPlayer, PlayerStats, TeamStats, MatchEvent, Analytics
)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['squad_number', 'full_name', 'position', 'age', 'fitness_level', 'market_value', 'is_active', 'is_injured']
    list_filter = ['position', 'is_active', 'is_injured', 'preferred_foot']
    search_fields = ['first_name', 'last_name', 'squad_number']
    ordering = ['squad_number']
    readonly_fields = ['id', 'age', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('squad_number', 'first_name', 'last_name', 'date_of_birth', 'age')
        }),
        ('Physical Attributes', {
            'fields': ('height', 'weight', 'preferred_foot')
        }),
        ('Position & Role', {
            'fields': ('position',)
        }),
        ('Contract & Value', {
            'fields': ('market_value', 'contract_expiry')
        }),
        ('Status', {
            'fields': ('is_active', 'is_injured', 'fitness_level')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'
    
    def age(self, obj):
        return obj.age
    age.short_description = 'Age'

@admin.register(Opponent)
class OpponentAdmin(admin.ModelAdmin):
    list_display = ['name', 'league', 'country', 'typical_formation', 'matches_played']
    list_filter = ['league', 'country']
    search_fields = ['name', 'league']
    ordering = ['name']
    readonly_fields = ['created_at', 'matches_played']
    
    def matches_played(self, obj):
        return obj.matches_against.count()
    matches_played.short_description = 'Matches Played'

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'match_type', 'status', 'result_display', 'scheduled_datetime', 'attendance']
    list_filter = ['status', 'match_type', 'is_home', 'scheduled_datetime']
    search_fields = ['opponent__name', 'venue']
    ordering = ['-scheduled_datetime']
    readonly_fields = ['id', 'result', 'created_at', 'updated_at']
    date_hierarchy = 'scheduled_datetime'
    
    fieldsets = (
        ('Match Details', {
            'fields': ('opponent', 'match_type', 'is_home', 'venue')
        }),
        ('Schedule', {
            'fields': ('scheduled_datetime', 'actual_kickoff')
        }),
        ('Status & Score', {
            'fields': ('status', 'chelsea_score', 'opponent_score', 'result')
        }),
        ('Additional Information', {
            'fields': ('attendance', 'weather_conditions', 'referee')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def result_display(self, obj):
        if obj.status not in ['COMPLETED', 'FULL_TIME']:
            return format_html('<span style="color: gray;">-</span>')
        
        color = 'green' if obj.result == 'WIN' else 'orange' if obj.result == 'DRAW' else 'red'
        return format_html(
            '<span style="color: {};">{} ({})</span>',
            color, obj.result, f"{obj.chelsea_score}-{obj.opponent_score}"
        )
    result_display.short_description = 'Result'

class FormationPositionInline(admin.TabularInline):
    model = FormationPosition
    extra = 0
    fields = ['position', 'x_coordinate', 'y_coordinate', 'is_core_position']

@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_outfield_players', 'defensive_line', 'midfield_line', 'attacking_line', 'is_active', 'usage_count']
    list_filter = ['is_active', 'defensive_line', 'midfield_line', 'attacking_line']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['total_outfield_players', 'created_at', 'usage_count']
    inlines = [FormationPositionInline]
    
    fieldsets = (
        ('Formation Details', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Structure', {
            'fields': ('defensive_line', 'midfield_line', 'attacking_line', 'total_outfield_players')
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'usage_count'),
            'classes': ('collapse',)
        })
    )
    
    def usage_count(self, obj):
        return MatchLineup.objects.filter(formation=obj).count()
    usage_count.short_description = 'Times Used'

class MatchLineupPlayerInline(admin.TabularInline):
    model = MatchLineupPlayer
    extra = 0
    fields = ['player', 'position', 'is_captain', 'minutes_played']
    autocomplete_fields = ['player']

@admin.register(MatchLineup)
class MatchLineupAdmin(admin.ModelAdmin):
    list_display = ['match', 'formation', 'is_starting_eleven', 'players_count']
    list_filter = ['formation', 'is_starting_eleven', 'match__status']
    search_fields = ['match__opponent__name', 'formation__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'players_count']
    inlines = [MatchLineupPlayerInline]
    
    def players_count(self, obj):
        return obj.lineup_players.count()
    players_count.short_description = 'Players'

@admin.register(PlayerStats)
class PlayerStatsAdmin(admin.ModelAdmin):
    list_display = ['player', 'match', 'position', 'rating', 'goals', 'assists', 'minutes_played', 'pass_accuracy']
    list_filter = ['player__position', 'match__status', 'rating']
    search_fields = ['player__first_name', 'player__last_name', 'match__opponent__name']
    ordering = ['-match__scheduled_datetime', 'player__squad_number']
    readonly_fields = ['pass_accuracy_display']
    
    fieldsets = (
        ('Match Information', {
            'fields': ('player', 'match', 'minutes_played', 'rating')
        }),
        ('Goals & Assists', {
            'fields': ('goals', 'assists')
        }),
        ('Passing', {
            'fields': ('passes_completed', 'passes_attempted', 'pass_accuracy_display')
        }),
        ('Physical Performance', {
            'fields': ('distance_covered', 'sprints', 'top_speed')
        }),
        ('Defensive Actions', {
            'fields': ('tackles_won', 'tackles_attempted', 'interceptions', 'clearances')
        }),
        ('Attacking Actions', {
            'fields': ('shots_on_target', 'shots_off_target', 'shots_blocked', 'crosses_completed', 'crosses_attempted')
        }),
        ('Disciplinary', {
            'fields': ('fouls_committed', 'fouls_won', 'yellow_cards', 'red_cards', 'offsides')
        })
    )
    
    def pass_accuracy_display(self, obj):
        if obj.passes_attempted == 0:
            return '0%'
        accuracy = (obj.passes_completed / obj.passes_attempted) * 100
        color = 'green' if accuracy >= 85 else 'orange' if accuracy >= 75 else 'red'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, accuracy)
    pass_accuracy_display.short_description = 'Pass Accuracy'
    
    def position(self, obj):
        return obj.player.position
    position.short_description = 'Position'

@admin.register(TeamStats)
class TeamStatsAdmin(admin.ModelAdmin):
    list_display = ['match', 'possession_percentage', 'pass_accuracy', 'shots_total', 'shots_on_target', 'corners']
    list_filter = ['match__status', 'match__is_home']
    search_fields = ['match__opponent__name']
    ordering = ['-match__scheduled_datetime']
    
    fieldsets = (
        ('Match Information', {
            'fields': ('match',)
        }),
        ('Possession & Passing', {
            'fields': ('possession_percentage', 'total_passes', 'pass_accuracy')
        }),
        ('Attacking Statistics', {
            'fields': ('shots_total', 'shots_on_target', 'shots_off_target', 'corners')
        }),
        ('Disciplinary', {
            'fields': ('offsides', 'fouls_committed', 'yellow_cards', 'red_cards')
        }),
        ('Physical Performance', {
            'fields': ('distance_covered_total', 'sprints_total')
        })
    )

@admin.register(MatchEvent)
class MatchEventAdmin(admin.ModelAdmin):
    list_display = ['match', 'player', 'event_type', 'minute', 'description_short']
    list_filter = ['event_type', 'match__status']
    search_fields = ['player__first_name', 'player__last_name', 'match__opponent__name', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Event Details', {
            'fields': ('match', 'player', 'event_type', 'minute')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Location', {
            'fields': ('x_coordinate', 'y_coordinate'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def description_short(self, obj):
        if obj.description and len(obj.description) > 50:
            return obj.description[:50] + '...'
        return obj.description or '-'
    description_short.short_description = 'Description'

@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ['title', 'analysis_type', 'confidence_score', 'created_by', 'created_at']
    list_filter = ['analysis_type', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'insights_preview', 'recommendations_preview']
    
    fieldsets = (
        ('Analysis Information', {
            'fields': ('analysis_type', 'title', 'description', 'confidence_score')
        }),
        ('Relationships', {
            'fields': ('related_match', 'related_player', 'related_formation')
        }),
        ('Content Preview', {
            'fields': ('insights_preview', 'recommendations_preview'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def insights_preview(self, obj):
        if obj.insights:
            insights_text = '<br>'.join([f"• {insight}" for insight in obj.insights[:3]])
            if len(obj.insights) > 3:
                insights_text += f"<br><em>... and {len(obj.insights) - 3} more</em>"
            return mark_safe(insights_text)
        return 'No insights available'
    insights_preview.short_description = 'Insights Preview'
    
    def recommendations_preview(self, obj):
        if obj.recommendations:
            recommendations_text = '<br>'.join([f"• {rec}" for rec in obj.recommendations[:3]])
            if len(obj.recommendations) > 3:
                recommendations_text += f"<br><em>... and {len(obj.recommendations) - 3} more</em>"
            return mark_safe(recommendations_text)
        return 'No recommendations available'
    recommendations_preview.short_description = 'Recommendations Preview'

# Customise admin site header and title
admin.site.site_header = "Chelsea FC Digital Twin Administration"
admin.site.site_title = "Chelsea FC Admin"
admin.site.index_title = "Welcome to Chelsea FC Digital Twin Administration"

# Custom admin actions
@admin.action(description='Mark selected players as injured')
def mark_as_injured(modeladmin, request, queryset):
    updated = queryset.update(is_injured=True)
    modeladmin.message_user(request, f'{updated} players marked as injured.')

@admin.action(description='Mark selected players as fit')
def mark_as_fit(modeladmin, request, queryset):
    updated = queryset.update(is_injured=False, fitness_level=100)
    modeladmin.message_user(request, f'{updated} players marked as fit.')

@admin.action(description='Deactivate selected players')
def deactivate_players(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f'{updated} players deactivated.')

PlayerAdmin.actions = [mark_as_injured, mark_as_fit, deactivate_players]

@admin.action(description='Mark selected matches as completed')
def mark_matches_completed(modeladmin, request, queryset):
    updated = queryset.update(status='COMPLETED')
    modeladmin.message_user(request, f'{updated} matches marked as completed.')

MatchAdmin.actions = [mark_matches_completed]