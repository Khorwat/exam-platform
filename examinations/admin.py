from django.contrib import admin
from .models import ExamSession, ExamAnswer


class ExamAnswerInline(admin.TabularInline):
    model = ExamAnswer
    extra = 0
    readonly_fields = ('is_correct', 'points_earned', 'answered_at')


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'status', 'started_at', 'submitted_at', 'ip_address')
    list_filter = ('status', 'started_at', 'exam')
    search_fields = ('student__username', 'exam__title')
    readonly_fields = ('started_at', 'submitted_at', 'time_elapsed_seconds')
    inlines = [ExamAnswerInline]
    
    def time_elapsed_seconds(self, obj):
        return obj.time_elapsed_seconds
    time_elapsed_seconds.short_description = 'Time Elapsed (seconds)'


@admin.register(ExamAnswer)
class ExamAnswerAdmin(admin.ModelAdmin):
    list_display = ('session', 'question', 'selected_option', 'is_correct', 'points_earned', 'answered_at')
    list_filter = ('is_correct', 'answered_at')
    search_fields = ('session__student__username', 'question__question_text')

