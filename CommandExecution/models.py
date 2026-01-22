from django.db import models
from django.conf import settings
import uuid


class CommandExecution(models.Model):
    """Command execution tracking model"""
    COMMAND_TYPE_CHOICES = [
        ('shell', 'Shell'),
        ('file_read', 'File Read'),
        ('file_write', 'File Write'),
        ('file_edit', 'File Edit'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('error', 'Error'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='command_executions')
    session = models.ForeignKey('session.Session', on_delete=models.SET_NULL, null=True, blank=True, related_name='command_executions')
    command = models.TextField()
    command_type = models.CharField(max_length=20, choices=COMMAND_TYPE_CHOICES)
    output = models.TextField(blank=True)
    exit_code = models.IntegerField(null=True, blank=True)
    execution_time_ms = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    hostname = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'command_executions'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['command_type']),
            models.Index(fields=['status']),
            models.Index(fields=['session']),
        ]

    def __str__(self):
        return f"{self.command_type} | {self.status} | {self.user.username}"
