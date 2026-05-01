from django.urls import path
from .views import (
    ExamListCreateView, ExamDetailView, ExamScheduleView,
    publish_exam, unpublish_exam
)

urlpatterns = [
    path('', ExamListCreateView.as_view(), name='exam-list'),
    path('<int:pk>/', ExamDetailView.as_view(), name='exam-detail'),
    path('<int:exam_id>/schedule/', ExamScheduleView.as_view(), name='exam-schedule'),
    path('<int:exam_id>/publish/', publish_exam, name='exam-publish'),
    path('<int:exam_id>/unpublish/', unpublish_exam, name='exam-unpublish'),
]

