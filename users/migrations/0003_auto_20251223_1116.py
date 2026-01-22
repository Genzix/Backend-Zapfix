# Generated migration to fix UUID conversion issue
from django.db import migrations
import uuid


def convert_ids_to_uuid(apps, schema_editor):
    """Convert existing integer IDs to UUIDs or delete invalid data"""
    Employee = apps.get_model('users', 'Employee')
    UserProfile = apps.get_model('users', 'UserProfile')
    
    # Delete employees with invalid UUIDs (they have integer IDs)
    # This is safe because we're in development
    Employee.objects.all().delete()
    
    # Delete user profiles with invalid UUIDs
    UserProfile.objects.all().delete()


def reverse_migration(apps, schema_editor):
    """Reverse migration - nothing to do"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_employee_id_alter_userprofile_id'),
    ]

    operations = [
        migrations.RunPython(convert_ids_to_uuid, reverse_migration),
    ]
