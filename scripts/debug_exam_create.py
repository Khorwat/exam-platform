import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
import json
import sys

# Setup Django before other imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from questions.models import Question, QuestionCategory
from exams.models import Exam

User = get_user_model()
try:
    user = User.objects.get(username='instructor1')
except User.DoesNotExist:
    user = User.objects.create_user('instructor1', 'instructor1@example.com', 'password123', role='instructor')

client = APIClient()
client.force_authenticate(user=user)

def print_resp(resp):
    print(f"Status: {resp.status_code}")
    try:
        if hasattr(resp, 'json'):
            print(f"Data: {json.dumps(resp.json(), indent=2)}")
        else:
            print(f"Data: {resp.content}")
    except:
        print(f"Data: {resp.data}")

# 1. Ensure questions exist
category, _ = QuestionCategory.objects.get_or_create(name="Exam Debug Cat")

q1, _ = Question.objects.get_or_create(
    question_text="Exam Debug Q1",
    defaults={'question_type': 'true_false', 'category': category, 'points': 5, 'created_by': user}
)
q2, _ = Question.objects.get_or_create(
    question_text="Exam Debug Q2",
    defaults={'question_type': 'true_false', 'category': category, 'points': 5, 'created_by': user}
)

print(f"Using questions: {q1.id}, {q2.id}")

# 2. Test Exam Creation Payload
print("\n--- Testing Exam Creation ---")
payload = {
    "title": "Debug Exam Creation",
    "description": "Test exam via script",
    "duration_minutes": 60,
    "passing_score": 50,
    "randomize_questions": True,
    "randomize_options": False,
    "allow_retake": True,
    "show_results_immediately": True,
    "is_active": True,
    "question_ids": [q1.id, q2.id]
}

resp = client.post('/api/exams/', payload, format='json')
print_resp(resp)

if resp.status_code == 201:
    exam_id = resp.json()['id']
    print(f"\nCreated Exam ID: {exam_id}")
    exam = Exam.objects.get(id=exam_id)
    print(f"Exam Question Count: {exam.exam_questions.count()}")
    if exam.exam_questions.count() == 2:
         print("SUCCESS: Questions linked correctly.")
    else:
         print("FAILURE: Question count mismatch.")
