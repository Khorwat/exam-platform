import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from exams.models import Exam
from questions.models import Question, QuestionCategory

User = get_user_model()

def verify_teacher_workflow():
    print("1. Setting up Instructor...")
    instructor, _ = User.objects.get_or_create(username='instructor1', email='instructor@test.com')
    instructor.set_password('password123')
    instructor.role = 'instructor'
    instructor.save()
    
    category, _ = QuestionCategory.objects.get_or_create(name='General')
    
    print("2. Testing Question Creation API...")
    client = APIClient()
    
    # Login
    response = client.post('/api/auth/login/', {'username': 'instructor1', 'password': 'password123'})
    token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    # Create Question
    question_data = {
        'question_text': 'What is 2+2?',
        'question_type': 'multiple_choice',
        'points': 5,
        'category': category.id,
        'difficulty': 'easy',
        'is_active': True,
        'options': [
            {'option_text': '3', 'is_correct': False, 'order': 1},
            {'option_text': '4', 'is_correct': True, 'order': 2}
        ]
    }
    
    response = client.post('/api/questions/', question_data, format='json')
    if response.status_code == 201:
        question_id = response.data['id']
        print(f"   [PASS] Question created (ID: {question_id})")
    else:
        print(f"   [FAIL] Question creation failed: {response.data}")
        return

    print("3. Testing Exam Creation API...")
    exam_data = {
        'title': 'Math 101',
        'description': 'Basic Math',
        'duration_minutes': 30,
        'passing_score': 60,
        'is_active': True,
        'question_ids': [question_id]
    }
    
    response = client.post('/api/exams/', exam_data, format='json')
    if response.status_code == 201:
        exam_id = response.data['id']
        print(f"   [PASS] Exam created (ID: {exam_id})")
        
        # Verify linkage
        exam = Exam.objects.get(id=exam_id)
        if exam.exam_questions.filter(question_id=question_id).exists():
             print("   [PASS] Question correctly linked to Exam")
        else:
             print("   [FAIL] Question NOT linked to Exam")
    else:
        print(f"   [FAIL] Exam creation failed: {response.data}")
        return

    print("4. Testing Exam Deletion API...")
    response = client.delete(f'/api/exams/{exam_id}/')
    if response.status_code == 204:
        print("   [PASS] Exam deleted successfully")
        if Exam.objects.filter(id=exam_id).exists():
             print("   [FAIL] Exam still exists in DB")
        else:
             print("   [PASS] Exam confirmed removed from DB")
    else:
        print(f"   [FAIL] Exam deletion failed: {response.status_code}")

if __name__ == '__main__':
    verify_teacher_workflow()
