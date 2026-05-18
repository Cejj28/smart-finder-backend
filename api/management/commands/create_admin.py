"""
Custom management command to create a superuser from environment variables.
This is used during Render deployment since the free tier has no Shell access.

Usage (in buildCommand):
    python manage.py create_admin

Required environment variables on Render:
    DJANGO_ADMIN_USERNAME  — e.g. admin
    DJANGO_ADMIN_EMAIL     — e.g. admin@smartfinder.com
    DJANGO_ADMIN_PASSWORD  — e.g. YourSecurePassword123
"""

import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a superuser from environment variables (idempotent — safe to run on every deploy)"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("DJANGO_ADMIN_USERNAME", "admin")
        email    = os.environ.get("DJANGO_ADMIN_EMAIL",    "admin@gmail.com")
        password = os.environ.get("DJANGO_ADMIN_PASSWORD", "admin123")

        if not password:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  DJANGO_ADMIN_PASSWORD is not set. Skipping superuser creation."
                )
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅  Superuser '{username}' already exists — no action taken."
                )
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"✅  Superuser '{username}' created successfully."
            )
        )
