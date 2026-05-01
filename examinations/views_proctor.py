from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import ExamSession, ProctoringSnapshot
from .serializers import ProctoringSnapshotSerializer

class IsInstructorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_instructor or request.user.is_administrator or request.user.is_superuser)

from .utils_proctor import analyze_snapshot

class SnapshotUploadView(generics.CreateAPIView):
    """
    Upload a webcam snapshot for an active exam session.
    Expects 'image' file in multipart/form-data.
    """
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProctoringSnapshotSerializer

    def post(self, request, session_id):
        session = get_object_or_404(ExamSession, id=session_id)
        
        # Verify user owns this session
        if session.student != request.user:
            return Response({"error": "Unauthorized access to session"}, status=status.HTTP_403_FORBIDDEN)
        
        # Verify session is active
        if not session.is_active:
             return Response({"error": "Session is not active"}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES.get('image')
        if not image_file:
             return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Analyzes the snapshot (AI or Client-reported)
        client_data = {
            'trust_score': float(request.data.get('trust_score', 1.0)),
            'issue_type': request.data.get('issue_type'),
            'face_data': request.data.get('face_data') # Expected as JSON or dict
        }
        
        # Handle JSON string if sent as form-data string
        import json
        if isinstance(client_data['face_data'], str):
            try:
                client_data['face_data'] = json.loads(client_data['face_data'])
            except:
                pass

        trust_score, issue_type, face_data = analyze_snapshot(image_file, client_data)
        
        # Rewind file for saving
        image_file.seek(0)

        snapshot = ProctoringSnapshot.objects.create(
            session=session,
            image=image_file,
            trust_score=trust_score,
            issue_type=issue_type,
            face_data=face_data
        )
        
        serializer = ProctoringSnapshotSerializer(snapshot)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ExamLiveFeedView(generics.ListAPIView):
    """
    Get latest snapshots for all students in a specific exam (Instructor only).
    """
    serializer_class = ProctoringSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        exam_id = self.kwargs['exam_id']
        print(f"DEBUG: LiveFeed for exam {exam_id}, User: {self.request.user}")
        # Return recent 100 snapshots for the exam
        return ProctoringSnapshot.objects.filter(
            session__exam_id=exam_id
        ).select_related('session', 'session__student').order_by('-timestamp')[:100]
