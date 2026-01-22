from django.db import models
from django.conf import settings
import uuid

# Create your models here.
class ActivityLog(models.Model):
    
    ACTIVITY_TYPE_CHOICES = (
        ('login', 'Login'),
        ('session_start', 'Session Start'),
        ('session_end', 'Session End'),
        ('command_executed', 'Command Executed'),
        ('message_sent', 'Message Sent'),
        ('error', 'Error'),
    )

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='activity_logs')
    activity_type = models.CharField(max_length=30,choices=ACTIVITY_TYPE_CHOICES)
    description = models.TextField(blank=True)
    metadata = models.JSONField(null=True,blank=True)
    ip_address = models.GenericIPAddressField(null=True,blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activity_logs'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['activity_type']),
        ]

    def __str__(self):
        return f"{self.user} | {self.activity_type} | {self.created_at}"
