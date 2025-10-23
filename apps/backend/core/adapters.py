from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from .models import Artist


class AccountAdapter(DefaultAccountAdapter):
    """Custom account adapter for Dead Party Media."""

    def send_mail(self, template_prefix, email, context):
        """Send email using Resend instead of Django's default."""
        context['site'] = Site.objects.get_current()
        subject = render_to_string(f'{template_prefix}_subject.txt', context).strip()
        message = render_to_string(f'{template_prefix}_message.txt', context)

        msg = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.send()

    def save_user(self, request, user, form, commit=True):
        """Save user and create related profiles if needed."""
        user = super().save_user(request, user, form, commit=False)

        # Set email as username if not provided
        if not user.username:
            user.username = user.email

        if commit:
            user.save()

        return user


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter."""

    def populate_user(self, request, sociallogin, data):
        """Populate user data from social login."""
        user = super().populate_user(request, sociallogin, data)

        # Try to match with existing artist profile
        if sociallogin.account.provider == 'spotify':
            spotify_id = data.get('id')
            if spotify_id:
                try:
                    artist = Artist.objects.get(spotify_id=spotify_id)
                    # Link the user to the artist profile
                    artist.user = user
                    artist.save()
                except Artist.DoesNotExist:
                    pass

        return user