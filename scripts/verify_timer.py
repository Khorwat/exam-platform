import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
from django.utils import timezone
from datetime import timedelta
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from exams.models import Exam
from examinations.models import ExamSession

User = get_user_model()

def verify_timer_logic():
    print("1. Setting up test data for timer verification...")
    student, _ = User.objects.get_or_create(username='timer_student', email='timer@test.com')
    student.set_password('password123')
    student.role = 'student'
    student.save()
    
    # Create a short exam (1 minute)
    exam, _ = Exam.objects.get_or_create(
        title='Timer Test Exam',
        defaults={
            'duration_minutes': 1,
            'passing_score': 50,
            'is_active': True
        }
    )
    
    # Create a session that started 61 seconds ago
    print("2. Creating expired session...")
    session = ExamSession.objects.create(
        exam=exam,
        student=student,
        status='in_progress',
        time_remaining_seconds=60
    )
    
    # Manually backdate the start time
    session.started_at = timezone.now() - timedelta(seconds=65)
    session.save()
    
    print(f"   Session started at: {session.started_at}")
    print(f"   Current time: {timezone.now()}")
    print(f"   Elapsed: {session.time_elapsed_seconds}s")
    print(f"   Duration: {exam.duration_minutes * 60}s")
    
    print("3. Checking time limit...")
    is_expired = session.check_time_limit()
    
    if is_expired:
        print("   [PASS] check_time_limit() returned True")
    else:
        print("   [FAIL] check_time_limit() returned False")
        
    session.refresh_from_db()
    print(f"   Session status: {session.status}")
    
    if session.status == 'time_up':
        print("   [PASS] Session status updated to 'time_up'")
    else:
        print(f"   [FAIL] Session status is '{session.status}', expected 'time_up'")

if __name__ == '__main__':
    verify_timer_logic()
