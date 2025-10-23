from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from .models import Artist, Author, Article, Event, InterviewRequest, Comment


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'genre', 'location', 'email', 'article_count', 'created_at']
    list_filter = ['genre', 'created_at', 'location']
    search_fields = ['name', 'email', 'bio']
    ordering = ['name']
    readonly_fields = ['article_count', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'genre', 'location', 'bio')
        }),
        ('Social Media', {
            'fields': ('instagram', 'twitter', 'youtube', 'tiktok', 'website'),
            'classes': ('collapse',)
        }),
        ('User Account', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('article_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('articles')


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'category', 'article_count', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'user__username', 'user__email', 'bio']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'category', 'bio', 'cash_tag')
        }),
        ('Social Media', {
            'fields': ('instagram',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'


class ArticleArtistInline(admin.TabularInline):
    model = Article.artists.through
    extra = 0
    verbose_name = "Featured Artist"
    verbose_name_plural = "Featured Artists"


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'date', 'is_featured', 'comment_count', 'created_at']
    list_filter = ['category', 'is_featured', 'date', 'created_at', 'author']
    search_fields = ['title', 'slug', 'excerpt', 'content']
    ordering = ['-date', '-created_at']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ArticleArtistInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'author', 'date', 'is_featured')
        }),
        ('Content', {
            'fields': ('image', 'excerpt', 'content')
        }),
        ('Artists', {
            'fields': ('artists',),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Comments'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('artists', 'comments')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'venue', 'date', 'time', 'genre', 'is_past', 'created_at']
    list_filter = ['genre', 'date', 'created_at', 'is_past']
    search_fields = ['title', 'artist', 'venue', 'location', 'description']
    ordering = ['date', 'time']
    readonly_fields = ['created_at', 'updated_at', 'is_past']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'artist', 'genre', 'date', 'time', 'doors')
        }),
        ('Venue & Location', {
            'fields': ('venue', 'location')
        }),
        ('Media & Links', {
            'fields': ('flyer', 'ticket_url')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Metadata', {
            'fields': ('is_past', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_past(self, obj):
        return obj.is_past
    is_past.boolean = True
    is_past.short_description = 'Past Event'


@admin.register(InterviewRequest)
class InterviewRequestAdmin(admin.ModelAdmin):
    list_display = ['artist', 'requester', 'email_sent', 'sms_sent', 'created_at']
    list_filter = ['email_sent', 'sms_sent', 'created_at', 'artist']
    search_fields = ['artist__name', 'requester__username', 'message']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Request Details', {
            'fields': ('artist', 'requester', 'message')
        }),
        ('Notifications', {
            'fields': ('email_sent', 'sms_sent')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_email_sent', 'mark_sms_sent']

    def mark_email_sent(self, request, queryset):
        queryset.update(email_sent=True)
        self.message_user(request, f"Marked {queryset.count()} interview requests as email sent.")
    mark_email_sent.short_description = "Mark selected requests as email sent"

    def mark_sms_sent(self, request, queryset):
        queryset.update(sms_sent=True)
        self.message_user(request, f"Marked {queryset.count()} interview requests as SMS sent.")
    mark_sms_sent.short_description = "Mark selected requests as SMS sent"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'article_link', 'content_preview', 'approved', 'created_at']
    list_filter = ['approved', 'created_at', 'article__category']
    search_fields = ['user__username', 'content', 'article__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_comments', 'disapprove_comments']

    fieldsets = (
        ('Comment Details', {
            'fields': ('article', 'user', 'content', 'approved')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def article_link(self, obj):
        url = reverse('admin:core_article_change', args=[obj.article.id])
        return format_html('<a href="{}">{}</a>', url, obj.article.title)
    article_link.short_description = 'Article'

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, f"Approved {queryset.count()} comments.")
    approve_comments.short_description = "Approve selected comments"

    def disapprove_comments(self, request, queryset):
        queryset.update(approved=False)
        self.message_user(request, f"Disapproved {queryset.count()} comments.")
    disapprove_comments.short_description = "Disapprove selected comments"


# Extend User admin to show related profiles
class AuthorInline(admin.StackedInline):
    model = Author
    can_delete = False
    verbose_name_plural = 'Author Profile'

class ArtistInline(admin.StackedInline):
    model = Artist
    can_delete = False
    verbose_name_plural = 'Artist Profile'

class CustomUserAdmin(UserAdmin):
    inlines = [AuthorInline, ArtistInline]
    list_display = UserAdmin.list_display + ('is_author', 'is_artist')

    def is_author(self, obj):
        return hasattr(obj, 'author_profile')
    is_author.boolean = True
    is_author.short_description = 'Author'

    def is_artist(self, obj):
        return hasattr(obj, 'artist_profile')
    is_artist.boolean = True
    is_artist.short_description = 'Artist'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)