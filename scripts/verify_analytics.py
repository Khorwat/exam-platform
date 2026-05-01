import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from exams.models import Exam
from questions.models import Question, QuestionCategory
from results.models import ExamResult, PerformanceAnalytics

User = get_user_model()

def verify_analytics():
    print("1. Setting up Environment...")
    instructor, _ = User.objects.get_or_create(username='instr_analytics', email='instr_an@test.com')
    instructor.set_password('password123')
    instructor.role = 'instructor'
    instructor.save()
    
    student, _ = User.objects.get_or_create(username='stud_analytics', email='stud_an@test.com')
    student.set_password('password123')
    student.role = 'student'
    student.save()
    
    category, _ = QuestionCategory.objects.get_or_create(name='Analytics Test')
    
    # Create Question
    question = Question.objects.create(
        question_text='Analytics Q1',
        question_type='true_false',
        points=10,
        category=category,
        difficulty='easy',
        created_by=instructor,
        is_active=True
    )
    
    # Create Exam
    exam = Exam.objects.create(
        title='Analytics Exam',
        description='Testing Analytics',
        duration_minutes=30,
        passing_score=50,
        created_by=instructor,
        is_active=True
    )
    exam.exam_questions.create(question=question, order=0)
    exam.calculate_total_points()

    print("2. Student taking exam...")
    client = APIClient()
    
    # Login Student
    response = client.post('/api/auth/login/', {'username': 'stud_analytics', 'password': 'password123'})
    token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    # Start Exam
    response = client.post('/api/examinations/start/', {'exam_id': exam.id})
    if response.status_code != 201 and response.status_code != 200:
        print(f"[FAIL] Start Exam failed: {response.data}")
        return
    
    session_data = response.data
    session_id = session_data['id']
    print(f"   [PASS] Exam Started (Session: {session_id})")
    
    # Submit Answer (Correct)
    # Need option ID for T/F
    # For T/F implementation, usually options are created automatically or user defined?
    # Checking implementation... assuming manual options for now from previous files
    # Actually T/F usually creates options. Let's create options manually if not present
    if question.options.count() == 0:
        question.options.create(option_text='True', is_correct=True, order=1)
        question.options.create(option_text='False', is_correct=False, order=2)
        
    correct_option = question.options.get(is_correct=True)
    
    response = client.post(f'/api/examinations/sessions/{session_id}/submit-answer/', {
        'question_id': question.id,
        'selected_option_id': correct_option.id
    })
    
    if response.status_code != 200:
        print(f"[FAIL] Submit Answer failed: {response.data}")
        return
    print("   [PASS] Answer Submitted")
    
    # Submit Exam
    response = client.post(f'/api/examinations/sessions/{session_id}/submit/')
    if response.status_code != 200:
        print(f"[FAIL] Submit Exam failed: {response.data}")
        return
    
    print("   [PASS] Exam Submitted")
    print(f"   Response: {response.data}")
    
    print("3. Verifying Results & Analytics...")
    
    # Check ExamResult
    if ExamResult.objects.filter(session_id=session_id).exists():
        result = ExamResult.objects.get(session_id=session_id)
        print(f"   [PASS] ExamResult found. Score: {result.percentage_score}%")
        if result.percentage_score == 100:
             print("   [PASS] Score calculation correct")
        else:
             print(f"   [FAIL] Score mismatch. Expected 100, got {result.percentage_score}")
    else:
        print("   [FAIL] ExamResult NOT found in DB")
        
    # Check PerformanceAnalytics
    if PerformanceAnalytics.objects.filter(student=student, exam=exam).exists():
        analytics = PerformanceAnalytics.objects.get(student=student, exam=exam)
        print(f"   [PASS] Analytics found. Exams Taken: {analytics.total_exams_taken}")
        if analytics.total_exams_taken >= 1:
             print("   [PASS] Analytics updated correctly")
        else:
             print("   [FAIL] Analytics count incorrect")
    else:
        print("   [FAIL] PerformanceAnalytics NOT found in DB")

if __name__ == '__main__':
    verify_analytics()
