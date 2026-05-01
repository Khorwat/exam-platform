import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from exams.models import Exam, ExamQuestion
from questions.models import Question, QuestionOption
from examinations.models import ExamSession
from rest_framework.test import APIClient

User = get_user_model()

def run_verification():
    print("1. Setting up test data...")
    # Create Student
    student, created = User.objects.get_or_create(username='student1', email='student1@test.com')
    student.set_password('password123')
    student.role = 'student'
    student.save()
    
    # Create Exam
    exam, _ = Exam.objects.get_or_create(
        title='Test Exam',
        defaults={
            'duration_minutes': 60,
            'passing_score': 50,
            'is_active': True
        }
    )
    
    # Create Question
    # Cleanup duplicates first
    Question.objects.filter(question_text='What is 2+2?').delete()
    
    question, _ = Question.objects.get_or_create(
        question_text='What is 2+2?',
        defaults={
            'question_type': 'multiple_choice',
            'points': 10
        }
    )
    
    # Create Options
    opt1, _ = QuestionOption.objects.get_or_create(question=question, option_text='3', defaults={'is_correct': False, 'order': 1})
    opt2, _ = QuestionOption.objects.get_or_create(question=question, option_text='4', defaults={'is_correct': True, 'order': 2})
    
    # Link Question to Exam
    ExamQuestion.objects.get_or_create(exam=exam, question=question)
    exam.calculate_total_points()
    
    print("2. Testing API Flow...")
    # Clear previous sessions for this test
    ExamSession.objects.filter(student=student, exam=exam).delete()
    
    client = APIClient()
    
    # Login
    response = client.post('/api/auth/login/', {'username': 'student1', 'password': 'password123'})
    if response.status_code != 200:
        print(f"FAILED: Login failed. {response.data}")
        return
    
    token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    print("   [PASS] Login successful")
    
    # Start Exam
    response = client.post('/api/examinations/start/', {'exam_id': exam.id})
    if response.status_code != 201:
        # Might be already started
        if 'active session' in str(response.data):
             print("   [INFO] Session already active")
             session_id = ExamSession.objects.get(student=student, exam=exam, status='in_progress').id
        else:
            print(f"FAILED: Start exam failed. {response.data}")
            return
    else:
        session_id = response.data['id']
    print(f"   [PASS] Exam started (Session ID: {session_id})")
    
    # Submit Answer
    response = client.post(f'/api/examinations/sessions/{session_id}/submit-answer/', {
        'question_id': question.id,
        'selected_option_id': opt2.id
    })
    if response.status_code != 200:
        print(f"FAILED: Submit answer failed. {response.data}")
        return
    print("   [PASS] Answer submitted")
    
    # Submit Exam
    response = client.post(f'/api/examinations/sessions/{session_id}/submit/')
    if response.status_code != 200:
        print(f"FAILED: Submit exam failed. {response.data}")
        return
    
    result = response.data
    print(f"   [PASS] Exam submitted. Score: {result['total_points']}/{result['max_points']}")
    
    if result['passed']:
        print("\nSUCCESS: Full exam flow verified!")
    else:
        print("\nWARNING: Flow worked, but student failed (expected if logic is correct).")

if __name__ == '__main__':
    try:
        run_verification()
    except Exception as e:
        print(f"\nERROR: Verification script crashed: {e}")
