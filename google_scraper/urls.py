from django.urls import path
from . import views

urlpatterns = [
    path("", views.scraper_page, name="scrape_form"),
    path("export/", views.scrape_and_process, name="export_to_excel"),  # This should work!
]
