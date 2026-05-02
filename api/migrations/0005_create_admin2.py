from django.db import migrations
from django.contrib.auth.models import User

def create_admin2(apps, schema_editor):
    if not User.objects.filter(username='admin2').exists():
        User.objects.create_superuser('admin2', 'admin2@example.com', 'password123')

def remove_admin2(apps, schema_editor):
    User.objects.filter(username='admin2').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0004_item_category'),
    ]

    operations = [
        migrations.RunPython(create_admin2, remove_admin2),
    ]
