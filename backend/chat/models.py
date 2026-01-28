import uuid
from django.db import models
from django.conf import settings


class ChatChannel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    context_type = models.CharField(max_length=255)
    context_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "CHAT_CHANNELS"
        verbose_name = "Chat channel"
        indexes = [
            models.Index(fields=["context_type", "context_id"]),
        ]

    def __str__(self):
        return f"{self.context_type} - {self.context_id}"


class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(
        ChatChannel, on_delete=models.CASCADE, related_name="messages"
    )
    sender_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sent_messages",
    )
    message_body = models.TextField()
    attachment_url = models.CharField(max_length=500, blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    read_by_ids = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "CHAT_MESSAGES"
        verbose_name = "ChatMessage"
        ordering = ["sent_at"]

    def __str__(self):
        return f"Message {self.id} in {self.channel}"


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(max_length=100)
    payload = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "NOTIFICATIONS"
        verbose_name = "Notification"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type} for {self.user}"
