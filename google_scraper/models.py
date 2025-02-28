from django.db import models

class Business(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name
