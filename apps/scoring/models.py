import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class ScoreRecord(models.Model):
    score_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='score_records',
    )
    resume_id = models.CharField(max_length=36, db_index=True)
    best_role = models.CharField(max_length=255)
    match_percentage = models.FloatField(default=0)
    matched_skills = models.JSONField(default=list, blank=True)
    missing_skills = models.JSONField(default=list, blank=True)
    top_roles = models.JSONField(default=list, blank=True)
    ai_suggestion = models.TextField(blank=True)
    resume_score = models.PositiveIntegerField(default=0)
    scored_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-scored_at']
        indexes = [
            models.Index(fields=['user', 'scored_at']),
            models.Index(fields=['resume_id']),
        ]

    def __str__(self):
        return f'{self.best_role} ({self.match_percentage}%)'

    def to_document(self):
        return {
            'score_id': str(self.score_id),
            'user_id': self.user_id,
            'resume_id': self.resume_id,
            'best_role': self.best_role,
            'match_percentage': self.match_percentage,
            'matched_skills': self.matched_skills,
            'missing_skills': self.missing_skills,
            'top_roles': self.top_roles,
            'ai_suggestion': self.ai_suggestion,
            'resume_score': self.resume_score,
            'scored_at': self.scored_at.isoformat(),
        }
