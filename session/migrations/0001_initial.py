from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('title', models.CharField(max_length=200, blank=True, default='')),
                ('status', models.CharField(max_length=20, choices=[('active', 'Active'), ('completed', 'Completed'), ('archived', 'Archived')], default='active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_activity_at', models.DateTimeField(auto_now=True)),
                ('total_tokens_used', models.IntegerField(default=0)),
                ('message_count', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='session',
            index=models.Index(fields=['user', 'created_at'], name='session_user_created_idx'),
        ),
        migrations.AddIndex(
            model_name='session',
            index=models.Index(fields=['status'], name='session_status_idx'),
        ),
    ]