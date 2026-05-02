from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_admin2(apps, schema_editor):
    # No longer needed as User Management is fixed
    pass

def remove_admin2(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0004_item_category'),
    ]

    operations = [
        migrations.RunPython(create_admin2, remove_admin2),
    ]
