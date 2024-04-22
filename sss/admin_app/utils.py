from django.core.mail import send_mail
from django.conf import settings
from . models import Email

def send_fire_alert():
    subject = "Fire Alert"
    message = "A fire has been detected at the location. Immediate action is required.'"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = Email.objects.values_list('email', flat=True)  # List of email recipients

    send_mail(subject, message, from_email, recipient_list)
