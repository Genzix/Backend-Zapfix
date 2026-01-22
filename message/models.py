from django.db import models
import uuid

class Message(models.Model):
    """Message model for session messages"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey('session.Session', on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    tokens_used = models.IntegerField(default=0)
    model_used = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sequence_number = models.IntegerField(default=0)

    class Meta:
        ordering = ['sequence_number', 'created_at']
        indexes = [
            models.Index(fields=['session', 'sequence_number']),
        ]
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
    
    def save(self, *args, **kwargs):
        """Auto-increment sequence_number"""
        is_new = self._state.adding
        
        if is_new and not self.sequence_number:
            # Get next sequence number for this session
            last_message = Message.objects.filter(session=self.session).order_by('-sequence_number').first()
            self.sequence_number = (last_message.sequence_number + 1) if last_message else 1
        
        super().save(*args, **kwargs)
