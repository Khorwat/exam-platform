import os
import django
import sys
import json
from datetime import timedelta
from django.utils import timezone

sys.path.append('c:/Users/mkhor/Downloads/Telegram Desktop/CODES')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from exams.models import Exam
from rest_framework.test import APIClient

User = get_user_model()

def debug_exam_start(exam_id=None):
    print("\n--- Debugging Exam Start ---")
    client = APIClient()

    # 1. Setup User (Student)
    student, _ = User.objects.get_or_create(username='debug_student_2', email='std2@debug.com', defaults={'role': 'student'})
    student.set_password('pass123')
    student.save()
    client.force_authenticate(user=student)
    print(f"Authenticated as: {student.username}")

    # 2. Get or Create Exam
    if exam_id:
        try:
            exam = Exam.objects.get(id=exam_id)
            print(f"Using existing exam: {exam.title} (ID: {exam.id})")
        except Exam.DoesNotExist:
            print(f"Exam {exam_id} not found.")
            return
    else:
        # Create a dummy exam if none provided
        exam = Exam.objects.create(
            title="Debug Exam",
            description="Test",
            duration_minutes=60,
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=10),
            created_by=student # technically should be instructor but fine for FK
        )
        print(f"Created temp exam: {exam.title} (ID: {exam.id})")

    # 3. Hit the Endpoint
    url = '/api/examinations/start/'
    print(f"POSTing to {url} with exam_id={exam.id}")
    
    try:
        response = client.post(url, {'exam_id': exam.id}, format='json')
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code != 201:
            print("Response Content (First 1000 chars):")
            # Decode if bytes
            content = response.content.decode('utf-8') if isinstance(response.content, bytes) else str(response.content)
            print(content[:1000])
        else:
            print("✅ Exam Started Successfully (JSON received)")
            print(json.dumps(response.data, indent=2))

    except Exception as e:
        print(f"Exception calling client: {e}")

if __name__ == '__main__':
    # Try with the ID from the screenshot first (28), fallback to auto-create
    try:
        # Pass 28 to test the specific user case
        debug_exam_start(28)
    except:
        debug_exam_start()
