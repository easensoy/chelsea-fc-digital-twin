from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.http import JsonResponse
from .football_api_service import FootballAPIService
import logging

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'index_modern.html')

def football_field(request):
    return render(request, 'football_field_demo.html')

@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Chelsea FC Digital Twin'
        return context

class FootballFieldView(TemplateView):
    template_name = 'football_field_demo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Interactive Football Field'
        return context

class TeamManagementView(TemplateView):
    template_name = 'team_management.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Team Management'
        return context

class TacticalAnalysisView(TemplateView):
    template_name = 'tactical_analysis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Tactical Analysis'
        return context

class AnalyticsView(TemplateView):
    template_name = 'analytics_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Analytics Dashboard'

        # Initialize API service
        api_service = FootballAPIService()

        # Get real data
        context['players'] = api_service.get_chelsea_players()
        context['matches'] = api_service.get_chelsea_matches(limit=5)
        context['team_stats'] = api_service.get_team_statistics()

        return context

# API endpoints for AJAX requests
def api_chelsea_players(request):
    """Get Chelsea players data as JSON"""
    api_service = FootballAPIService()
    players = api_service.get_chelsea_players()
    return JsonResponse({'players': players})

def api_formation_433(request):
    """Get Chelsea players arranged in 4-3-3 formation"""
    api_service = FootballAPIService()
    formation = api_service.get_formation_433()
    return JsonResponse({'formation': formation})

class PlayerProfilesView(TemplateView):
    template_name = 'player_profiles.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Player Profiles & Management'
        return context