from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, Q, Max, Min
from django.utils import timezone
from .models import ExamResult, PerformanceAnalytics
from .serializers import ExamResultSerializer, PerformanceAnalyticsSerializer
from examinations.models import ExamSession
from accounts.permissions import IsStudent, IsInstructor, IsAdministrator


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def grade_exam_session(request, session_id):
    """Grade an exam session and create result"""
    try:
        session = ExamSession.objects.get(id=session_id)
    except ExamSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check permissions
    if request.user.is_student and session.student != request.user:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    if session.status not in ['submitted', 'time_up']:
        return Response({'error': 'Exam session is not completed'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if result already exists
    if hasattr(session, 'result'):
        return Response(ExamResultSerializer(session.result).data)
    
    # Create result
    result = ExamResult.objects.create(
        session=session,
        graded_by=request.user if not request.user.is_student else None
    )
    result.calculate_score()
    
    # Update analytics
    analytics, created = PerformanceAnalytics.objects.get_or_create(
        exam=session.exam,
        student=session.student
    )
    analytics.update_analytics()
    
    return Response(ExamResultSerializer(result).data, status=status.HTTP_201_CREATED)


class ExamResultListView(generics.ListAPIView):
    """List all exam results"""
    serializer_class = ExamResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = ExamResult.objects.all()
        
        if user.is_student:
            queryset = queryset.filter(session__student=user)
        elif user.is_instructor:
            # Instructors see results for exams they created
            queryset = queryset.filter(session__exam__created_by=user)
        
        # Filter by exam if provided
        exam_id = self.request.query_params.get('exam_id')
        if exam_id:
            queryset = queryset.filter(session__exam_id=exam_id)
        
        return queryset.select_related('session', 'session__exam', 'session__student')


class ExamResultDetailView(generics.RetrieveAPIView):
    """Retrieve a specific exam result"""
    queryset = ExamResult.objects.all()
    serializer_class = ExamResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = ExamResult.objects.all()
        
        if user.is_student:
            queryset = queryset.filter(session__student=user)
        elif user.is_instructor:
            queryset = queryset.filter(session__exam__created_by=user)
        
        return queryset


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsInstructor])
def exam_statistics(request, exam_id):
    """Get statistics for a specific exam"""
    from exams.models import Exam
    
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return Response({'error': 'Exam not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check permissions
    if not request.user.is_administrator and exam.created_by != request.user:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    results = ExamResult.objects.filter(session__exam=exam)
    
    stats = {
        'total_students': ExamSession.objects.filter(exam=exam).values('student').distinct().count(),
        'total_completed': results.count(),
        'total_passed': results.filter(passed=True).count(),
        'total_failed': results.filter(passed=False).count(),
        'average_score': results.aggregate(avg=Avg('percentage_score'))['avg'] or 0,
        'highest_score': results.aggregate(max=Max('percentage_score'))['max'] or 0,
        'lowest_score': results.aggregate(min=Min('percentage_score'))['min'] or 0,
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard_stats(request):
    """Get dashboard statistics for the current student"""
    if not request.user.is_student:
        return Response({'error': 'Only students can access this endpoint'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    results = ExamResult.objects.filter(session__student=request.user)
    
    stats = {
        'total_exams_taken': results.count(),
        'total_passed': results.filter(passed=True).count(),
        'total_failed': results.filter(passed=False).count(),
        'average_score': results.aggregate(avg=Avg('percentage_score'))['avg'] or 0,
        'upcoming_exams': ExamSession.objects.filter(
            student=request.user,
            status='not_started',
            exam__schedule__start_date__gte=timezone.now()
        ).count(),
    }
    
    return Response(stats)


class PerformanceAnalyticsListView(generics.ListAPIView):
    """List performance analytics"""
    serializer_class = PerformanceAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = PerformanceAnalytics.objects.all()
        
        if user.is_student:
            queryset = queryset.filter(student=user)
        elif user.is_instructor:
            queryset = queryset.filter(exam__created_by=user)
        
        return queryset

