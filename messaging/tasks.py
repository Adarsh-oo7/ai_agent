from celery import shared_task
from django.core.mail import send_mail
from .models import Message

@shared_task
def send_scheduled_emails():
    messages = Message.objects.filter(status="Pending")
    for message in messages:
        try:
            send_mail(
                subject=f"Message from {message.company_name}",
                message=message.message_body,
                from_email="your_email@example.com",
                recipient_list=[message.recipient_email],
                fail_silently=False,
            )
            message.status = "Sent"
        except Exception as e:
            print(f"Failed to send email: {e}")
        message.save()
