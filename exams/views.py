from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Exam, ExamSchedule
from .serializers import ExamSerializer, ExamListSerializer, ExamScheduleSerializer
from accounts.permissions import IsInstructor, IsAdministrator, IsStudent


class ExamListCreateView(generics.ListCreateAPIView):
    """List all exams or create a new exam"""
    # Permission handled in get_permissions
    filter_backends = []
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsInstructor()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Exam.objects.all()
        # Ensure user is authenticated before checking attributes
        if not self.request.user.is_authenticated:
            return Exam.objects.none()
            
        if self.request.user.is_student:
            # Students only see active, scheduled exams
            queryset = queryset.filter(
                is_active=True,
                # Simple availability check - complex scheduling might need more logic
                # For now assuming active exams are visible
            )
        elif self.request.user.is_instructor:
            # Instructors only see exams they created
            queryset = queryset.filter(created_by=self.request.user)
            
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ExamListSerializer
        return ExamSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ExamDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an exam"""
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    # Permission handled in get_permissions
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsInstructor()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Exam.objects.all()
        user = self.request.user
        
        if user.is_authenticated and user.is_instructor:
            # Instructors can only view/edit/delete their own exams
            queryset = queryset.filter(created_by=user)
            
        return queryset
    
    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)


class ExamScheduleView(generics.RetrieveUpdateAPIView):
    """Retrieve or update exam schedule"""
    queryset = ExamSchedule.objects.all()
    serializer_class = ExamScheduleSerializer
    permission_classes = [IsAuthenticated, IsInstructor]
    
    def get_object(self):
        exam_id = self.kwargs.get('exam_id')
        schedule, created = ExamSchedule.objects.get_or_create(exam_id=exam_id)
        return schedule


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsInstructor])
def publish_exam(request, exam_id):
    """Publish an exam (make it available)"""
    try:
        exam = Exam.objects.get(id=exam_id)
        schedule, created = ExamSchedule.objects.get_or_create(exam=exam)
        schedule.is_published = True
        schedule.save()
        return Response({'message': 'Exam published successfully'})
    except Exam.DoesNotExist:
        return Response({'error': 'Exam not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsInstructor])
def unpublish_exam(request, exam_id):
    """Unpublish an exam (make it unavailable)"""
    try:
        exam = Exam.objects.get(id=exam_id)
        schedule, created = ExamSchedule.objects.get_or_create(exam=exam)
        schedule.is_published = False
        schedule.save()
        return Response({'message': 'Exam unpublished successfully'})
    except Exam.DoesNotExist:
        return Response({'error': 'Exam not found'}, status=status.HTTP_404_NOT_FOUND)

