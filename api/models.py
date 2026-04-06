from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    REPORT_TYPES = (
        ('Lost', 'Lost'),
        ('Found', 'Found'),
    )

    type = models.CharField(max_length=10, choices=REPORT_TYPES)
    item_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    contact_info = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)
    status = models.CharField(max_length=20, default='Pending Review')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_items')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type}: {self.item_name}"
