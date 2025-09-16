from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'index.html')

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