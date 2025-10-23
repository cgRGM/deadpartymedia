from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from .models import Artist, Author, Article, Event, InterviewRequest, Comment
from .serializers import (
    ArtistSerializer, AuthorSerializer, ArticleSerializer, ArticleCreateUpdateSerializer,
    EventSerializer, InterviewRequestSerializer, InterviewRequestCreateSerializer,
    CommentSerializer, CommentCreateSerializer
)


class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Artist model."""
    queryset = Artist.objects.all().order_by('name')
    serializer_class = ArtistSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['genre', 'location']
    search_fields = ['name', 'bio']

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Author model."""
    queryset = Author.objects.all().order_by('name')
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']
    search_fields = ['name', 'bio']

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Article model."""
    queryset = Article.objects.select_related('author__user').prefetch_related('artists', 'comments').order_by('-date')
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_featured', 'author', 'artists']
    search_fields = ['title', 'excerpt', 'content']

    @method_decorator(cache_page(60 * 10))  # Cache for 10 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 10))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get the featured article."""
        try:
            article = Article.objects.select_related('author__user').prefetch_related('artists').get(is_featured=True)
            serializer = self.get_serializer(article)
            return Response(serializer.data)
        except Article.DoesNotExist:
            return Response({'detail': 'No featured article found.'}, status=status.HTTP_404_NOT_FOUND)


class ArticleAdminViewSet(viewsets.ModelViewSet):
    """ViewSet for Article model (admin/writer access only)."""
    queryset = Article.objects.select_related('author__user').prefetch_related('artists').order_by('-date')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ArticleCreateUpdateSerializer
        return ArticleSerializer

    def perform_create(self, serializer):
        # Set author based on user's author profile if they have one
        if hasattr(self.request.user, 'author_profile'):
            serializer.save(author=self.request.user.author_profile)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        """Toggle featured status of an article."""
        article = self.get_object()
        article.is_featured = not article.is_featured
        article.save()
        return Response({'is_featured': article.is_featured})


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Event model."""
    queryset = Event.objects.all().order_by('date', 'time')
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['genre', 'date']
    search_fields = ['title', 'artist', 'venue', 'location']

    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 5))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming events."""
        from django.utils import timezone
        upcoming_events = self.queryset.filter(date__gte=timezone.now().date())
        page = self.paginate_queryset(upcoming_events)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(upcoming_events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past(self, request):
        """Get past events."""
        from django.utils import timezone
        past_events = self.queryset.filter(date__lt=timezone.now().date())
        page = self.paginate_queryset(past_events)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(past_events, many=True)
        return Response(serializer.data)


class InterviewRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for InterviewRequest model."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Artists can see requests for themselves, admins can see all
        if user.is_staff or user.is_superuser:
            return InterviewRequest.objects.select_related('artist', 'requester').order_by('-created_at')
        elif hasattr(user, 'artist_profile'):
            return InterviewRequest.objects.filter(artist=user.artist_profile).select_related('requester').order_by('-created_at')
        else:
            return InterviewRequest.objects.filter(requester=user).select_related('artist').order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'create':
            return InterviewRequestCreateSerializer
        return InterviewRequestSerializer

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Comment model."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.select_related('user', 'article').filter(approved=True).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def ratelimit_error(request):
    """Custom rate limit error response."""
    return Response(
        {'error': 'Too many requests. Please try again later.'},
        status=status.HTTP_429_TOO_MANY_REQUESTS
    )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response({'status': 'healthy', 'service': 'deadpartymedia-backend'})