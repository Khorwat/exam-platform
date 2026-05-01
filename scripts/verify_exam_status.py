import os
import django
import sys
from datetime import timedelta
from django.utils import timezone

sys.path.append('c:/Users/mkhor/Downloads/Telegram Desktop/CODES')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from exams.models import Exam, ExamSchedule
from examinations.models import ExamSession
from rest_framework.test import APIClient

User = get_user_model()

def verify_exam_status():
    print("\n--- Verifying Exam Availability Status ---")
    client = APIClient()

    # 1. Setup Student & Instructor
    student, _ = User.objects.get_or_create(username='status_student', email='stat@test.com')
    student.set_password('pass123')
    student.save()
    client.force_authenticate(user=student)
    
    instr, _ = User.objects.get_or_create(username='status_instr', email='inst_stat@test.com', defaults={'role': 'instructor'})
    instr.save()

    # Clear previous test data
    Exam.objects.filter(title__startswith="Status Test").delete()

    # 2. Create Exams in different states
    now = timezone.now()

    # A. Active & Fresh (Standard case)
    exam_active = Exam.objects.create(title="Status Test: Active", duration_minutes=30, created_by=instr, is_active=True)
    ExamSchedule.objects.create(exam=exam_active, start_date=now - timedelta(days=1), end_date=now + timedelta(days=1), is_published=True)

    # B. Already Taken (Submitted)
    exam_taken = Exam.objects.create(title="Status Test: Taken", duration_minutes=30, created_by=instr, is_active=True)
    ExamSchedule.objects.create(exam=exam_taken, start_date=now - timedelta(days=1), end_date=now + timedelta(days=1), is_published=True)
    ExamSession.objects.create(exam=exam_taken, student=student, status='submitted')

    # C. In Progress (Resumable)
    exam_wip = Exam.objects.create(title="Status Test: WIP", duration_minutes=30, created_by=instr, is_active=True)
    ExamSchedule.objects.create(exam=exam_wip, start_date=now - timedelta(days=1), end_date=now + timedelta(days=1), is_published=True)
    ExamSession.objects.create(exam=exam_wip, student=student, status='in_progress', time_remaining_seconds=1000)

    # D. Expired
    exam_expired = Exam.objects.create(title="Status Test: Expired", duration_minutes=30, created_by=instr, is_active=True)
    ExamSchedule.objects.create(exam=exam_expired, start_date=now - timedelta(days=5), end_date=now - timedelta(days=1), is_published=True)

    # E. Future (Not Open Yet)
    exam_future = Exam.objects.create(title="Status Test: Future", duration_minutes=30, created_by=instr, is_active=True)
    ExamSchedule.objects.create(exam=exam_future, start_date=now + timedelta(days=1), end_date=now + timedelta(days=5), is_published=True)

    # 3. Fetch List from API
    response = client.get('/api/exams/')
    if response.status_code != 200:
        print(f"❌ Failed to fetch exams: {response.status_code}")
        return

    exams = response.data.get('results', [])
    print(f"Fetched {len(exams)} exams.")

    # 4. Analyze Results
    for e in exams:
        if not e['title'].startswith("Status Test"): continue
        
        title = e['title']
        status_info = e.get('student_status', 'N/A')
        window = e.get('availability_window', {})
        is_open = window.get('is_open', 'N/A')
        
        print(f"\nExample: {title}")
        print(f"  > Student Status: {status_info}")
        print(f"  > Is Open: {is_open}")

if __name__ == '__main__':
    verify_exam_status()
