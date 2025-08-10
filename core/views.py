from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Avg, Sum, Count, F
from django.utils import timezone
from django.core.cache import cache
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
import json
import logging

from .models import (
    Player, Match, Formation, Opponent, Analytics, PlayerStats, 
    TeamStats, MatchEvent, MatchLineup, MatchLineupPlayer, FormationPosition
)
from .serializers import (
    PlayerSerializer, MatchSerializer, FormationSerializer, OpponentSerializer,
    AnalyticsSerializer, PlayerStatsSerializer, TeamStatsSerializer, MatchEventSerializer
)
from .performance_tracker import PerformanceTracker
from .fitness_monitor import FitnessMonitor
from .career_analyzer import CareerAnalyzer
from .live_tracker import LiveTracker
from .result_analyzer import ResultAnalyzer
from .opponent_scout import OpponentScout
from .formation_engine import FormationEngine
from .tactical_analyzer import TacticalAnalyzer
from .recommendation_system import RecommendationSystem
from .performance_calculator import PerformanceCalculator
from .trend_analyzer import TrendAnalyzer
from .comparison_engine import ComparisonEngine
from .prediction_models import PredictionModels
from .data_exporters import DataExporters
from .report_generators import ReportGenerators
from .powerbi_connector import PowerBIConnector
from .chart_generators import ChartGenerators
from .data_aggregators import DataAggregators
from .widget_managers import WidgetManagers

logger = logging.getLogger(__name__)

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.filter(is_active=True)
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Player.objects.filter(is_active=True)
        position = self.request.query_params.get('position', None)
        if position:
            queryset = queryset.filter(position=position)
        return queryset.order_by('squad_number')
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        player = self.get_object()
        tracker = PerformanceTracker()
        performance_data = tracker.get_player_performance(player)
        return Response(performance_data)
    
    @action(detail=True, methods=['get'])
    def fitness(self, request, pk=None):
        player = self.get_object()
        monitor = FitnessMonitor()
        fitness_data = monitor.get_fitness_status(player)
        return Response(fitness_data)

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Match.objects.all()
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by('-scheduled_datetime')
    
    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        match = self.get_object()
        analyzer = ResultAnalyzer()
        analysis_data = analyzer.analyze_match(match)
        return Response(analysis_data)
    
    @action(detail=True, methods=['post'])
    def update_live(self, request, pk=None):
        match = self.get_object()
        live_tracker = LiveTracker()
        update_data = live_tracker.update_match(match, request.data)
        return Response(update_data)

class FormationViewSet(viewsets.ModelViewSet):
    queryset = Formation.objects.filter(is_active=True)
    serializer_class = FormationSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def effectiveness(self, request, pk=None):
        formation = self.get_object()
        analyzer = TacticalAnalyzer()
        effectiveness_data = analyzer.analyze_formation_effectiveness(formation)
        return Response(effectiveness_data)
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        engine = RecommendationSystem()
        recommendations = engine.get_formation_recommendations()
        return Response(recommendations)

class OpponentViewSet(viewsets.ModelViewSet):
    queryset = Opponent.objects.all()
    serializer_class = OpponentSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def scout_report(self, request, pk=None):
        opponent = self.get_object()
        scout = OpponentScout()
        scout_data = scout.generate_report(opponent)
        return Response(scout_data)

class AnalyticsViewSet(viewsets.ModelViewSet):
    queryset = Analytics.objects.all()
    serializer_class = AnalyticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Analytics.objects.all()
        analysis_type = self.request.query_params.get('type', None)
        if analysis_type:
            queryset = queryset.filter(analysis_type=analysis_type)
        return queryset.order_by('-created_at')

class PlayerStatsViewSet(viewsets.ModelViewSet):
    queryset = PlayerStats.objects.all()
    serializer_class = PlayerStatsSerializer
    permission_classes = [IsAuthenticated]

class TeamStatsViewSet(viewsets.ModelViewSet):
    queryset = TeamStats.objects.all()
    serializer_class = TeamStatsSerializer
    permission_classes = [IsAuthenticated]

@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'main.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        widget_manager = WidgetManagers()
        context['widgets'] = widget_manager.get_dashboard_widgets()
        return context

@method_decorator(login_required, name='dispatch')
class PlayersPageView(TemplateView):
    template_name = 'players.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['players'] = Player.objects.filter(is_active=True).order_by('squad_number')
        return context

@method_decorator(login_required, name='dispatch')
class MatchesPageView(TemplateView):
    template_name = 'matches.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_matches'] = Match.objects.filter(
            status='SCHEDULED',
            scheduled_datetime__gte=timezone.now()
        ).order_by('scheduled_datetime')[:5]
        context['recent_matches'] = Match.objects.filter(
            status__in=['COMPLETED', 'FULL_TIME']
        ).order_by('-scheduled_datetime')[:5]
        return context

@method_decorator(login_required, name='dispatch')
class FormationsPageView(TemplateView):
    template_name = 'formations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formations'] = Formation.objects.filter(is_active=True)
        return context

@method_decorator(login_required, name='dispatch')
class AnalyticsPageView(TemplateView):
    template_name = 'analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_analytics'] = Analytics.objects.order_by('-created_at')[:10]
        return context

@method_decorator(login_required, name='dispatch')
class DataCentreView(TemplateView):
    template_name = 'data-center.html'

@method_decorator(login_required, name='dispatch')
class PowerBIGuideView(TemplateView):
    template_name = 'powerbi-guide.html'

class LiveTrackingView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        live_matches = Match.objects.filter(status__in=['LIVE', 'HALF_TIME'])
        tracker = LiveTracker()
        tracking_data = tracker.get_live_data(live_matches)
        return Response(tracking_data)
    
    def post(self, request):
        match_id = request.data.get('match_id')
        event_data = request.data.get('event_data')
        match = get_object_or_404(Match, id=match_id)
        tracker = LiveTracker()
        result = tracker.record_event(match, event_data)
        return Response(result)

class FormationRecommendationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        opponent_id = request.query_params.get('opponent_id')
        match_type = request.query_params.get('match_type', 'LEAGUE')
        
        engine = RecommendationSystem()
        recommendations = engine.get_formation_recommendations(
            opponent_id=opponent_id,
            match_type=match_type
        )
        return Response(recommendations)

class PlayerPerformanceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, player_id):
        player = get_object_or_404(Player, id=player_id)
        tracker = PerformanceTracker()
        analyzer = CareerAnalyzer()
        
        performance_data = {
            'current_performance': tracker.get_player_performance(player),
            'career_analysis': analyzer.get_career_overview(player),
            'recent_trends': tracker.get_performance_trends(player)
        }
        return Response(performance_data)

class MatchAnalysisView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, match_id):
        match = get_object_or_404(Match, id=match_id)
        analyzer = ResultAnalyzer()
        tactical_analyzer = TacticalAnalyzer()
        
        analysis_data = {
            'match_summary': analyzer.analyze_match(match),
            'tactical_analysis': tactical_analyzer.analyze_match_tactics(match),
            'player_ratings': analyzer.get_player_ratings(match)
        }
        return Response(analysis_data)

class TacticalInsightsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        analyzer = TacticalAnalyzer()
        insights = analyzer.generate_tactical_insights()
        return Response(insights)

class PerformanceTrendsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        trend_analyzer = TrendAnalyzer()
        trends = trend_analyzer.analyze_performance_trends()
        return Response(trends)

class PowerBIExportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        export_type = request.data.get('export_type', 'all')
        exporter = DataExporters()
        powerbi_connector = PowerBIConnector()
        
        try:
            export_data = exporter.export_for_powerbi(export_type)
            result = powerbi_connector.upload_data(export_data)
            
            logger.info(f"PowerBI export completed: {export_type}")
            return Response(result)
        except Exception as e:
            logger.error(f"PowerBI export failed: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CSVExportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        export_type = request.data.get('export_type', 'all')
        date_range = request.data.get('date_range', None)
        
        exporter = DataExporters()
        csv_data = exporter.export_to_csv(export_type, date_range)
        
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="chelsea_fc_{export_type}_{timezone.now().strftime("%Y%m%d")}.csv"'
        return response

class ExcelExportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        export_type = request.data.get('export_type', 'all')
        date_range = request.data.get('date_range', None)
        
        exporter = DataExporters()
        excel_data = exporter.export_to_excel(export_type, date_range)
        
        response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="chelsea_fc_{export_type}_{timezone.now().strftime("%Y%m%d")}.xlsx"'
        return response

class ScheduledExportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        schedule_config = request.data
        exporter = DataExporters()
        result = exporter.schedule_export(schedule_config)
        return Response(result)

class MatchEventsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, match_id):
        match = get_object_or_404(Match, id=match_id)
        events = MatchEvent.objects.filter(match=match).order_by('minute', 'created_at')
        serializer = MatchEventSerializer(events, many=True)
        return Response(serializer.data)
    
    def post(self, request, match_id):
        match = get_object_or_404(Match, id=match_id)
        event_data = request.data
        event_data['match'] = match.id
        
        serializer = MatchEventSerializer(data=event_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MatchLineupView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, match_id):
        match = get_object_or_404(Match, id=match_id)
        lineup = MatchLineup.objects.filter(match=match).first()
        if lineup:
            lineup_data = {
                'formation': lineup.formation.name,
                'players': [
                    {
                        'player': player.player.full_name,
                        'position': player.position,
                        'is_captain': player.is_captain
                    }
                    for player in lineup.lineup_players.all()
                ]
            }
            return Response(lineup_data)
        return Response({'message': 'No lineup found'}, status=status.HTTP_404_NOT_FOUND)

class LiveMatchUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, match_id):
        match = get_object_or_404(Match, id=match_id)
        update_data = request.data
        
        live_tracker = LiveTracker()
        result = live_tracker.update_match_live(match, update_data)
        return Response(result)

class DashboardWidgetsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        widget_manager = WidgetManagers()
        widgets_data = widget_manager.get_all_widgets()
        return Response(widgets_data)

class DashboardChartsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        chart_generator = ChartGenerators()
        charts_data = chart_generator.generate_dashboard_charts()
        return Response(charts_data)

class LoginView(TemplateView):
    template_name = 'login.html'
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({'success': True, 'redirect': '/'})
        return JsonResponse({'success': False, 'error': 'Invalid credentials'})

class RegisterView(TemplateView):
    template_name = 'register.html'

class LogoutView(View):
    def post(self, request):
        logout(request)
        return JsonResponse({'success': True, 'redirect': '/login/'})