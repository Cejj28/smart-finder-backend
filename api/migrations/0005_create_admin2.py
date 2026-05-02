from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_admin2(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    if not User.objects.filter(username='admin2').exists():
        User.objects.create(
            username='admin2',
            email='admin2@example.com',
            password=make_password('password123'),
            is_superuser=True,
            is_staff=True,
            is_active=True
        )

def remove_admin2(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username='admin2').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0004_item_category'),
    ]

    operations = [
        migrations.RunPython(create_admin2, remove_admin2),
    ]
