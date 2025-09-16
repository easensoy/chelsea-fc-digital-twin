from django.urls import path
from . import simple_views

app_name = 'core'

urlpatterns = [
    path('', simple_views.home, name='home'),
    path('dashboard/', simple_views.DashboardView.as_view(), name='dashboard'),
    path('football-field/', simple_views.FootballFieldView.as_view(), name='football_field'),
    path('team-management/', simple_views.TeamManagementView.as_view(), name='team_management'),
    path('tactical-analysis/', simple_views.TacticalAnalysisView.as_view(), name='tactical_analysis'),
    path('analytics/', simple_views.AnalyticsView.as_view(), name='analytics'),
    path('player-profiles/', simple_views.PlayerProfilesView.as_view(), name='player_profiles'),
    path('manage-players/', simple_views.PlayerProfilesView.as_view(), name='manage_players'),
    # API endpoints
    path('api/players/', simple_views.api_chelsea_players, name='api_players'),
    path('api/formation-433/', simple_views.api_formation_433, name='api_formation_433'),
]