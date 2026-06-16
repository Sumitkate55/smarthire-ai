from django.contrib import admin

from .models import ScoreRecord


@admin.register(ScoreRecord)
class ScoreRecordAdmin(admin.ModelAdmin):
    list_display = ('best_role', 'user', 'match_percentage', 'resume_score', 'scored_at')
    list_filter = ('scored_at',)
    search_fields = ('best_role', 'user__username', 'resume_id')
    ordering = ('-scored_at',)
