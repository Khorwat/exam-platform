import os
import django
import sys
from django.utils import timezone

sys.path.append('c:/Users/mkhor/Downloads/Telegram Desktop/CODES')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from exams.models import Exam
from rest_framework.test import APIClient

User = get_user_model()

def debug_list_crash():
    print("\n--- Debugging Exam List Crash ---")
    client = APIClient()

    # 1. Setup Student
    student, _ = User.objects.get_or_create(username='crash_student', email='crash@test.com')
    student.set_password('pass123')
    student.save()
    client.force_authenticate(user=student)

    # 2. Create an Exam WITHOUT a schedule
    # This is the suspect case: OneToOne relation is missing
    unsafe_exam = Exam.objects.create(
        title="Unsafe Exam No Schedule", 
        duration_minutes=30, 
        created_by=student, # created_by doesn't matter much for crash
        is_active=True
    )
    # Ensure no schedule exists (just in case signals created one? No signals for schedule yet)
    if hasattr(unsafe_exam, 'schedule'):
        unsafe_exam.schedule.delete()

    print(f"Created Exam {unsafe_exam.id} without schedule.")

    # 3. Hit the API
    url = '/api/exams/'
    print(f"GETing {url} ...")
    try:
        response = client.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print("Response Content:")
            print(response.content.decode('utf-8')[:500])
        else:
            print("✅ Success! No crash.")
            data = response.data.get('results', [])
            for ex in data:
                if ex['id'] == unsafe_exam.id:
                    print(f"Exam {ex['id']} data: {ex.get('availability_window')}")

    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == '__main__':
    debug_list_crash()
