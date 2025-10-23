from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Artist, Author, Article, Event, InterviewRequest, Comment


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class ArtistSerializer(serializers.ModelSerializer):
    """Serializer for Artist model."""
    article_count = serializers.ReadOnlyField()

    class Meta:
        model = Artist
        fields = [
            'id', 'name', 'email', 'spotify_id', 'location', 'genre', 'bio',
            'instagram', 'twitter', 'youtube', 'tiktok', 'website',
            'article_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'article_count', 'created_at', 'updated_at']


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for Author model."""
    user = UserSerializer(read_only=True)
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            'id', 'user', 'name', 'category', 'bio', 'cash_tag', 'instagram',
            'article_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'article_count', 'created_at', 'updated_at']

    def get_article_count(self, obj):
        return obj.articles.count()


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model."""
    author = AuthorSerializer(read_only=True)
    artists = ArtistSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'slug', 'title', 'category', 'image', 'excerpt', 'author',
            'date', 'content', 'artists', 'is_featured', 'comment_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'comment_count', 'created_at', 'updated_at']

    def get_comment_count(self, obj):
        return obj.comments.filter(approved=True).count()


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating articles (admin/writer only)."""

    class Meta:
        model = Article
        fields = [
            'id', 'slug', 'title', 'category', 'image', 'excerpt', 'author',
            'date', 'content', 'artists', 'is_featured', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model."""
    is_past = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'artist', 'date', 'time', 'venue', 'location',
            'genre', 'flyer', 'doors', 'ticket_url', 'description', 'is_past',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_past', 'created_at', 'updated_at']


class InterviewRequestSerializer(serializers.ModelSerializer):
    """Serializer for InterviewRequest model."""
    artist = ArtistSerializer(read_only=True)
    requester = UserSerializer(read_only=True)

    class Meta:
        model = InterviewRequest
        fields = [
            'id', 'artist', 'requester', 'message', 'email_sent', 'sms_sent',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email_sent', 'sms_sent', 'created_at', 'updated_at']


class InterviewRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating interview requests."""

    class Meta:
        model = InterviewRequest
        fields = ['artist', 'message']

    def create(self, validated_data):
        validated_data['requester'] = self.context['request'].user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model."""
    user = UserSerializer(read_only=True)
    article = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'article', 'user', 'content', 'approved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'approved', 'created_at', 'updated_at']


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments."""

    class Meta:
        model = Comment
        fields = ['article', 'content']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)