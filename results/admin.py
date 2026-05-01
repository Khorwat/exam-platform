from django.contrib import admin
from .models import ExamResult, PerformanceAnalytics


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('session', 'total_points_earned', 'total_points_possible', 
                    'percentage_score', 'passed', 'graded_at', 'graded_by')
    list_filter = ('passed', 'graded_at', 'session__exam')
    search_fields = ('session__student__username', 'session__exam__title')
    readonly_fields = ('graded_at',)


@admin.register(PerformanceAnalytics)
class PerformanceAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'average_score', 'total_exams_taken', 
                    'total_passed', 'total_failed', 'last_updated')
    list_filter = ('exam', 'last_updated')
    search_fields = ('student__username', 'exam__title')
    readonly_fields = ('last_updated',)

