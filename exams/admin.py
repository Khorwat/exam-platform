from django.contrib import admin
from .models import Exam, ExamQuestion, ExamSchedule


class ExamQuestionInline(admin.TabularInline):
    model = ExamQuestion
    extra = 1


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration_minutes', 'passing_score', 'total_points', 
                    'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'allow_retake', 'show_results_immediately', 'created_at')
    search_fields = ('title', 'description')
    inlines = [ExamQuestionInline]
    readonly_fields = ('total_points', 'created_at', 'updated_at')


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ('exam', 'start_date', 'end_date', 'is_published', 'is_active', 'created_at')
    list_filter = ('is_published', 'start_date', 'end_date')
    search_fields = ('exam__title',)


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'question', 'order')
    list_filter = ('exam',)
    search_fields = ('exam__title', 'question__question_text')

