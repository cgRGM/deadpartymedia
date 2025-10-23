from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
from django.core.validators import URLValidator
from django.conf import settings


# Category choices for articles and events
CATEGORY_CHOICES = [
    ('country', 'Country'),
    ('hardcore_rock', 'Hardcore & Rock'),
    ('hiphop_rb', 'Hip-Hop & R&B'),
    ('edm', 'EDM'),
    ('other', 'Other'),
]


class TimeStampedModel(models.Model):
    """Abstract base model with timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Artist(TimeStampedModel):
    """Model for music artists featured in articles."""
    name = models.CharField(max_length=200, unique=True)
    email = models.EmailField(blank=True, null=True)
    spotify_id = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    genre = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    bio = models.TextField(blank=True, null=True)

    # Social media links
    instagram = models.URLField(blank=True, null=True, validators=[URLValidator()])
    twitter = models.URLField(blank=True, null=True, validators=[URLValidator()])
    youtube = models.URLField(blank=True, null=True, validators=[URLValidator()])
    tiktok = models.URLField(blank=True, null=True, validators=[URLValidator()])
    website = models.URLField(blank=True, null=True, validators=[URLValidator()])

    # User relationship for artist dashboard access
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='artist_profile')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def article_count(self):
        return self.articles.count()

    def get_absolute_url(self):
        return reverse('artist_detail', kwargs={'pk': self.pk})


class Author(TimeStampedModel):
    """Model for article authors/writers."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_profile')
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    bio = models.TextField(blank=True, null=True)
    cash_tag = models.CharField(max_length=50, blank=True, null=True, help_text="Cash App tag")

    # Social media links
    instagram = models.URLField(blank=True, null=True, validators=[URLValidator()])

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('author_detail', kwargs={'pk': self.pk})


class Article(TimeStampedModel):
    """Model for blog articles."""
    slug = models.SlugField(max_length=200, unique=True)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    excerpt = models.TextField(help_text="Brief description for SEO and previews")
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    date = models.DateField(default=timezone.now)
    content = CKEditor5Field('Content', config_name='default')
    artists = models.ManyToManyField(Artist, related_name='articles', blank=True)
    is_featured = models.BooleanField(default=False, help_text="Only one article can be featured at a time")

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        # Ensure only one featured article
        if self.is_featured:
            Article.objects.filter(is_featured=True).update(is_featured=False)
        super().save(*args, **kwargs)


class Event(TimeStampedModel):
    """Model for music events."""
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200, help_text="Artist name or 'Various'")
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    venue = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    genre = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    flyer = models.ImageField(upload_to='events/', blank=True, null=True)
    doors = models.TimeField(null=True, blank=True, help_text="Door opening time")
    ticket_url = models.URLField(blank=True, null=True, validators=[URLValidator()])
    description = CKEditor5Field('Description', config_name='default', blank=True, null=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.title} - {self.date}"

    @property
    def is_past(self):
        return self.date < timezone.now().date()

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'pk': self.pk})


class InterviewRequest(TimeStampedModel):
    """Model for interview requests to artists."""
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='interview_requests')
    requester = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='interview_requests')
    message = models.TextField(help_text="Interview request message")
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Interview request for {self.artist.name}"

    def get_absolute_url(self):
        return reverse('interview_request_detail', kwargs={'pk': self.pk})


class Comment(TimeStampedModel):
    """Model for article comments."""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    approved = models.BooleanField(default=True, help_text="Comments are approved by default, can be moderated")

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"