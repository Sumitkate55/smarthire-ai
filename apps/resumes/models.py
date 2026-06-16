import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class ResumeRecord(models.Model):
    resume_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resume_records',
    )
    username = models.CharField(max_length=150, blank=True)
    label = models.CharField(max_length=255, blank=True)
    filename = models.CharField(max_length=255)
    raw_text = models.TextField()
    extracted_skills = models.JSONField(default=list, blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['user', 'uploaded_at']),
            models.Index(fields=['resume_id']),
        ]

    def __str__(self):
        return self.label or self.filename

    def to_document(self):
        return {
            'resume_id': str(self.resume_id),
            'user_id': self.user_id,
            'username': self.username,
            'label': self.label,
            'filename': self.filename,
            'raw_text': self.raw_text,
            'extracted_skills': self.extracted_skills,
            'uploaded_at': self.uploaded_at.isoformat(),
        }
