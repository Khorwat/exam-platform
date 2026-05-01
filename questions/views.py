from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Question, QuestionCategory
from .serializers import (
    QuestionSerializer, QuestionListSerializer, QuestionCategorySerializer
)
from accounts.permissions import IsInstructor, IsAdministrator


class QuestionCategoryListCreateView(generics.ListCreateAPIView):
    """List all categories or create a new category"""
    queryset = QuestionCategory.objects.all()
    serializer_class = QuestionCategorySerializer
    permission_classes = [IsAuthenticated, IsInstructor]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class QuestionCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a category"""
    queryset = QuestionCategory.objects.all()
    serializer_class = QuestionCategorySerializer
    permission_classes = [IsAuthenticated, IsInstructor]


class QuestionListCreateView(generics.ListCreateAPIView):
    """List all questions or create a new question"""
    queryset = Question.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated, IsInstructor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['question_type', 'difficulty', 'category', 'is_active']
    search_fields = ['question_text', 'explanation']
    ordering_fields = ['created_at', 'points', 'difficulty']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return QuestionListSerializer
        return QuestionSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a question"""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsInstructor]
    
    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdministrator])
def bulk_delete_questions(request):
    """Bulk delete questions"""
    question_ids = request.data.get('question_ids', [])
    if not question_ids:
        return Response({'error': 'No question IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    deleted_count = Question.objects.filter(id__in=question_ids).delete()[0]
    return Response({'message': f'{deleted_count} questions deleted successfully'})

