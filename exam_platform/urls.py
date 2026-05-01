"""
URL configuration for exam_platform project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.views.generic import RedirectView
from .views import serve_frontend

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/questions/', include('questions.urls')),
    path('api/exams/', include('exams.urls')),
    path('api/examinations/', include('examinations.urls')),
    path('api/results/', include('results.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Frontend routes
    re_path(r'^frontend/(?P<path>.*)$', serve_frontend, name='frontend'),
    re_path(r'^$', RedirectView.as_view(url='/frontend/login.html', permanent=False), name='index'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

