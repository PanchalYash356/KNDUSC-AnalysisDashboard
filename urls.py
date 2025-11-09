# mydash/urls.py (PROJECT level)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("🚀 Dashboard is running! Visit /admin/ or /analytics/")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('analytics.urls')),
    path('', health_check, name='home')
    ,  # This includes all analytics URLs at root
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)