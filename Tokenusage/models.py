from django.db import models
from django.conf import settings
import uuid

class TokenUsage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='token_usages')
    session = models.ForeignKey('session.Session', on_delete=models.SET_NULL, null=True, blank=True, related_name='token_usages')
    message = models.ForeignKey('message.Message', on_delete=models.SET_NULL, null=True, blank=True, related_name='token_usages')
    model_used = models.CharField(max_length=100)
    tokens_input = models.IntegerField(default=0)
    tokens_output = models.IntegerField(default=0)
    tokens_total = models.IntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'token_usage'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['session']),
            models.Index(fields=['model_used']),
        ]

    def save(self, *args, **kwargs):
        self.tokens_total = (self.tokens_input or 0) + (self.tokens_output or 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{getattr(self.user, 'username', str(getattr(self.user, 'id', 'unknown')))} | {self.model_used} | {self.tokens_total} tokens"
