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

def verify_exam_edit():
    print("1. Setting up Environment...")
    instructor, _ = User.objects.get_or_create(username='instr_edit', email='instr_edit@test.com')
    instructor.set_password('password123')
    instructor.role = 'instructor'
    instructor.save()
    
    category, _ = QuestionCategory.objects.get_or_create(name='Edit Test')
    
    q1 = Question.objects.create(
        question_text='Edit Q1', question_type='true_false', points=5, category=category, 
        difficulty='easy', created_by=instructor, is_active=True
    )
    q2 = Question.objects.create(
        question_text='Edit Q2', question_type='true_false', points=5, category=category, 
        difficulty='easy', created_by=instructor, is_active=True
    )

    client = APIClient()
    response = client.post('/api/auth/login/', {'username': 'instr_edit', 'password': 'password123'})
    token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    print("2. Creating Exam...")
    exam_data = {
        'title': 'Original Title',
        'description': 'Desc',
        'duration_minutes': 60,
        'passing_score': 50,
        'is_active': True,
        'question_ids': [q1.id]
    }
    response = client.post('/api/exams/', exam_data, format='json')
    if response.status_code != 201:
        print(f"[FAIL] Exam creation failed: {response.data}")
        return
    exam_id = response.data['id']
    print(f"   [PASS] Exam Created (ID: {exam_id})")

    print("3. Editing Exam (Update Title & Add Question)...")
    edit_data = {
        'title': 'Updated Title',
        'description': 'Updated Desc',
        'duration_minutes': 90,
        'passing_score': 50,
        'is_active': True,
        'question_ids': [q1.id, q2.id]
    }
    response = client.put(f'/api/exams/{exam_id}/', edit_data, format='json')
    if response.status_code != 200:
        print(f"[FAIL] Exam edit failed: {response.data}")
        return
    
    # Verify in DB
    exam = Exam.objects.get(id=exam_id)
    if exam.title != 'Updated Title':
        print(f"   [FAIL] Title update failed. Got: {exam.title}")
    else:
        print("   [PASS] Title updated")
        
    if exam.exam_questions.count() != 2:
         print(f"   [FAIL] Question count mismatch. Expected 2, got {exam.exam_questions.count()}")
    else:
         print("   [PASS] Question added successfully")

    print("4. Deleting Exam...")
    response = client.delete(f'/api/exams/{exam_id}/')
    if response.status_code != 204:
        print(f"[FAIL] Exam release failed: {response.status_code}")
        return
        
    if Exam.objects.filter(id=exam_id).exists():
        print("   [FAIL] Exam still in DB")
    else:
        print("   [PASS] Exam deleted successfully")

if __name__ == '__main__':
    verify_exam_edit()
