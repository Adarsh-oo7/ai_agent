from django.urls import path
from .views import send_email, upload_excel, success, home

urlpatterns = [
    path("", home, name="home"),
    path("send_email/", send_email, name="send_email"),
    path("upload/", upload_excel, name="upload_excel"),
    path("success/", success, name="success"),
]
