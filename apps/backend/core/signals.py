from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from .models import InterviewRequest


@receiver(post_save, sender=InterviewRequest)
def send_interview_notifications(sender, instance, created, **kwargs):
    """Send email and SMS notifications when an interview request is created."""
    if not created:
        return

    artist = instance.artist
    message = instance.message

    # Send email notification
    if artist.email and not instance.email_sent:
        try:
            send_mail(
                subject=f"Interview Request from Dead Party Media",
                message=f"""
Hello {artist.name},

You've received a new interview request from Dead Party Media:

{message}

You can respond by replying to this email or contacting us directly.

Best regards,
Dead Party Media Team
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[artist.email],
                fail_silently=True,
            )
            instance.email_sent = True
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Failed to send email notification: {e}")

    # Send SMS notification if Twilio is configured
    if (settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and
        settings.TWILIO_PHONE_NUMBER and artist.user and artist.user.phone and
        not instance.sms_sent):
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"New interview request from Dead Party Media: {message[:100]}...",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=artist.user.phone
            )
            instance.sms_sent = True
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Failed to send SMS notification: {e}")

    # Save the instance if notifications were sent
    if instance.email_sent or instance.sms_sent:
        instance.save(update_fields=['email_sent', 'sms_sent'])