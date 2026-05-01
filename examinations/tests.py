"""
Tests for examinations app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from exams.models import Exam, ExamSchedule
from questions.models import Question, QuestionOption
from .models import ExamSession, ExamAnswer

User = get_user_model()


class ExamSessionTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='student',
            password='testpass123',
            role='student'
        )
        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123',
            role='instructor'
        )
        self.exam = Exam.objects.create(
            title='Test Exam',
            duration_minutes=60,
            passing_score=60,
            created_by=self.instructor
        )
        self.schedule = ExamSchedule.objects.create(
            exam=self.exam,
            start_date=timezone.now() - timedelta(hours=1),
            end_date=timezone.now() + timedelta(hours=1),
            is_published=True
        )
    
    def test_start_exam_session(self):
        client = APIClient()
        client.force_authenticate(user=self.student)
        
        response = client.post('/api/examinations/start/', {
            'exam_id': self.exam.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ExamSession.objects.filter(
            exam=self.exam,
            student=self.student,
            status='in_progress'
        ).exists())
    
    def test_time_limit_check(self):
        session = ExamSession.objects.create(
            exam=self.exam,
            student=self.student,
            status='in_progress',
            started_at=timezone.now() - timedelta(minutes=61)
        )
        self.assertTrue(session.check_time_limit())
        session.refresh_from_db()
        self.assertEqual(session.status, 'time_up')

