from django.urls import path
from . import simple_views

app_name = 'core'

urlpatterns = [
    # Main pages matching navigation
    path('', simple_views.DashboardView.as_view(), name='dashboard'),
    path('players/', simple_views.PlayerProfilesView.as_view(), name='players'),
    path('matches/', simple_views.MatchesView.as_view(), name='matches'),
    path('formations/', simple_views.FootballFieldView.as_view(), name='formations'),
    path('analytics/', simple_views.AnalyticsView.as_view(), name='analytics'),
    path('data-centre/', simple_views.DataCentreView.as_view(), name='data_centre'),

    # Legacy URLs for compatibility
    path('dashboard/', simple_views.DashboardView.as_view(), name='dashboard_legacy'),
    path('football-field/', simple_views.FootballFieldView.as_view(), name='football_field'),
    path('team-management/', simple_views.TeamManagementView.as_view(), name='team_management'),
    path('tactical-analysis/', simple_views.TacticalAnalysisView.as_view(), name='tactical_analysis'),
    path('player-profiles/', simple_views.PlayerProfilesView.as_view(), name='player_profiles'),
    path('manage-players/', simple_views.PlayerProfilesView.as_view(), name='manage_players'),

    # API endpoints
    path('api/players/', simple_views.api_chelsea_players, name='api_players'),
    path('api/formation-433/', simple_views.api_formation_433, name='api_formation_433'),
    path('api/formation-352/', simple_views.api_formation_352, name='api_formation_352'),
    path('api/formation-442/', simple_views.api_formation_442, name='api_formation_442'),
    path('api/formation-4231/', simple_views.api_formation_4231, name='api_formation_4231'),
]