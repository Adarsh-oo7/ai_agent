from django.db import models

class Message(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Sent', 'Sent'),
    )

    recipient_name = models.CharField(max_length=255)
    recipient_email = models.EmailField()
    company_name = models.CharField(max_length=255)
    message_body = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"{self.recipient_name} - {self.company_name}"
