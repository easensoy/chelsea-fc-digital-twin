from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'players', views.PlayerViewSet)
router.register(r'matches', views.MatchViewSet)
router.register(r'formations', views.FormationViewSet)
router.register(r'opponents', views.OpponentViewSet)
router.register(r'analytics', views.AnalyticsViewSet)
router.register(r'player-stats', views.PlayerStatsViewSet)
router.register(r'team-stats', views.TeamStatsViewSet)

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('players/', views.PlayersPageView.as_view(), name='players'),
    path('matches/', views.MatchesPageView.as_view(), name='matches'),
    path('formations/', views.FormationsPageView.as_view(), name='formations'),
    path('analytics/', views.AnalyticsPageView.as_view(), name='analytics'),
    path('data-centre/', views.DataCentreView.as_view(), name='data_centre'),
    path('powerbi-guide/', views.PowerBIGuideView.as_view(), name='powerbi_guide'),
    
    path('api/', include(router.urls)),
    
    path('api/live-tracking/', views.LiveTrackingView.as_view(), name='live_tracking'),
    path('api/formation-recommendations/', views.FormationRecommendationView.as_view(), name='formation_recommendations'),
    path('api/player-performance/<uuid:player_id>/', views.PlayerPerformanceView.as_view(), name='player_performance'),
    path('api/match-analysis/<uuid:match_id>/', views.MatchAnalysisView.as_view(), name='match_analysis'),
    path('api/tactical-insights/', views.TacticalInsightsView.as_view(), name='tactical_insights'),
    path('api/performance-trends/', views.PerformanceTrendsView.as_view(), name='performance_trends'),
    
    path('api/exports/powerbi/', views.PowerBIExportView.as_view(), name='powerbi_export'),
    path('api/exports/csv/', views.CSVExportView.as_view(), name='csv_export'),
    path('api/exports/excel/', views.ExcelExportView.as_view(), name='excel_export'),
    path('api/exports/schedule/', views.ScheduledExportView.as_view(), name='scheduled_export'),
    
    path('api/match/<uuid:match_id>/events/', views.MatchEventsView.as_view(), name='match_events'),
    path('api/match/<uuid:match_id>/lineup/', views.MatchLineupView.as_view(), name='match_lineup'),
    path('api/match/<uuid:match_id>/live-update/', views.LiveMatchUpdateView.as_view(), name='live_match_update'),
    
    path('api/dashboard/widgets/', views.DashboardWidgetsView.as_view(), name='dashboard_widgets'),
    path('api/dashboard/charts/', views.DashboardChartsView.as_view(), name='dashboard_charts'),
    
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]