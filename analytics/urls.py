# analytics/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard - root URL
    path('', views.dashboard_view, name='dashboard'),

    # Upload page
    path('upload/', views.upload_file, name='upload'),

    # API endpoints
    path('analytics/api/', views.analytics_api, name='analytics_api'),
    path('analytics/api/<str:section>/', views.analytics_section_api, name='analytics_section_api'),

    # Test endpoint for debugging
    path('test-api/', views.test_api, name='test_api'),
]