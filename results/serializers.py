from rest_framework import serializers
from .models import ExamResult, PerformanceAnalytics
from examinations.serializers import ExamSessionSerializer


class ExamResultSerializer(serializers.ModelSerializer):
    session = ExamSessionSerializer(read_only=True)
    graded_by_name = serializers.CharField(source='graded_by.username', read_only=True)
    
    class Meta:
        model = ExamResult
        fields = ('id', 'session', 'total_points_earned', 'total_points_possible',
                  'percentage_score', 'passed', 'graded_at', 'graded_by', 'graded_by_name')
        read_only_fields = ('id', 'graded_at', 'graded_by')


class PerformanceAnalyticsSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(source='exam.title', read_only=True)
    student_name = serializers.CharField(source='student.username', read_only=True)
    
    class Meta:
        model = PerformanceAnalytics
        fields = ('id', 'exam', 'exam_title', 'student', 'student_name',
                  'average_score', 'total_exams_taken', 'total_passed',
                  'total_failed', 'last_updated')
        read_only_fields = ('id', 'last_updated')

