"""
URL configuration for deadpartymedia backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from core.views import (
    ArtistViewSet, AuthorViewSet, ArticleViewSet, ArticleAdminViewSet,
    EventViewSet, InterviewRequestViewSet, CommentViewSet, health_check
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'artists', ArtistViewSet)
router.register(r'authors', AuthorViewSet)
router.register(r'articles', ArticleViewSet)
router.register(r'events', EventViewSet)
router.register(r'interview-requests', InterviewRequestViewSet)
router.register(r'comments', CommentViewSet)

# Admin-only router for content management
admin_router = DefaultRouter()
admin_router.register(r'articles', ArticleAdminViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/admin/', include(admin_router.urls)),
    path('api/auth/', include('rest_framework.urls')),
    path('accounts/', include('allauth.urls')),
    path('health/', health_check, name='health_check'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)