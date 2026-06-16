from django.contrib import admin

from .models import ResumeRecord


@admin.register(ResumeRecord)
class ResumeRecordAdmin(admin.ModelAdmin):
    list_display = ('label', 'username', 'user', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('label', 'filename', 'username', 'user__username')
    ordering = ('-uploaded_at',)
