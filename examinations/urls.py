from django.urls import path
from .views import (
    start_exam, get_exam_session, submit_answer, submit_exam, log_activity, update_answer_score,
    ExamSessionListView
)
from .views_proctor import SnapshotUploadView, ExamLiveFeedView

urlpatterns = [
    path('start/', start_exam, name='start-exam'),
    path('sessions/', ExamSessionListView.as_view(), name='session-list'),
    path('sessions/<int:session_id>/', get_exam_session, name='session-detail'),
    path('sessions/<int:session_id>/submit-answer/', submit_answer, name='submit-answer'),
    path('sessions/<int:session_id>/submit/', submit_exam, name='submit-exam'),
    path('sessions/<int:session_id>/log/', log_activity, name='log-activity'),
    path('sessions/<int:session_id>/answers/<int:answer_id>/grade/', update_answer_score, name='update-answer-score'),
    
    # Proctoring Routes
    path('sessions/<int:session_id>/snapshot/', SnapshotUploadView.as_view(), name='upload-snapshot'),
    path('exams/<int:exam_id>/live-feed/', ExamLiveFeedView.as_view(), name='exam-live-feed'),
]

