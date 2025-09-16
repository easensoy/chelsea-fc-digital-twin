from django.urls import path
from . import simple_views

app_name = 'core'

urlpatterns = [
    path('', simple_views.home, name='home'),
    path('dashboard/', simple_views.DashboardView.as_view(), name='dashboard'),
    path('football-field/', simple_views.FootballFieldView.as_view(), name='football_field'),
]