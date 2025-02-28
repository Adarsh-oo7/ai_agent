from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient_name', 'recipient_email', 'company_name', 'message_body']


class UploadFileForm(forms.Form):
    file = forms.FileField()