from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.user.username} ({self.role})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

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
    category = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)
    status = models.CharField(max_length=20, default='Pending Review')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_items')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type}: {self.item_name}"

class Claim(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Released', 'Released'),
    )
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='claims')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claims', null=True, blank=True)
    claimant_name = models.CharField(max_length=255)
    proof = models.TextField()
    contact_info = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    release_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Claim by {self.claimant_name} for {self.item.item_name}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    target_page = models.CharField(max_length=100) # e.g. /items or /claims
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

@receiver(post_save, sender=Item)
def notify_item_changes(sender, instance, created, **kwargs):
    try:
        if created:
            # Notify admins of new post
            admins = User.objects.filter(is_staff=True)
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    title="New Item Reported",
                    message=f"A new {instance.type.lower()} item '{instance.item_name}' has been reported and needs review.",
                    target_page="/items"
                )
        else:
            # Only notify if status changed (heuristic: if not Pending Review anymore)
            # and avoid notifying if it was just deleted or something similar
            if instance.status != 'Pending Review':
                Notification.objects.get_or_create(
                    user=instance.reporter,
                    title="Post Status Updated",
                    message=f"Your post '{instance.item_name}' has been {instance.status.lower()}.",
                    target_page="/profile",
                    is_read=False
                )
    except Exception as e:
        print(f"Notification Error: {e}")

@receiver(post_save, sender=Claim)
def notify_claim_changes(sender, instance, created, **kwargs):
    try:
        if created:
            # Notify admins of new claim
            admins = User.objects.filter(is_staff=True)
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    title="New Claim Submitted",
                    message=f"A new claim has been submitted for '{instance.item.item_name}' by {instance.claimant_name}.",
                    target_page="/claims"
                )
        else:
            # Notify user who made the claim if status changed
            if instance.user and instance.status != 'Pending':
                Notification.objects.get_or_create(
                    user=instance.user,
                    title="Claim Status Updated",
                    message=f"Your claim for '{instance.item.item_name}' has been {instance.status.lower()}.",
                    target_page="/profile",
                    is_read=False
                )
    except Exception as e:
        print(f"Notification Error: {e}")
