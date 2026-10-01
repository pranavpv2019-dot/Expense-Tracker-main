from django.core.mail import send_mail
from django.conf import settings

def send_project_email(subject, message, to_email):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # sender (project mail)
        [to_email],                  # receiver (user mail)
        fail_silently=False,
    )
