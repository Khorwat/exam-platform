from django.urls import path
from .views import (
    grade_exam_session, ExamResultListView, ExamResultDetailView,
    exam_statistics, student_dashboard_stats, PerformanceAnalyticsListView
)

urlpatterns = [
    path('sessions/<int:session_id>/grade/', grade_exam_session, name='grade-session'),
    path('', ExamResultListView.as_view(), name='result-list'),
    path('<int:pk>/', ExamResultDetailView.as_view(), name='result-detail'),
    path('exams/<int:exam_id>/statistics/', exam_statistics, name='exam-statistics'),
    path('dashboard/stats/', student_dashboard_stats, name='dashboard-stats'),
    path('analytics/', PerformanceAnalyticsListView.as_view(), name='analytics-list'),
]

