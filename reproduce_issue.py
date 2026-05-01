
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.request import Request
from django.contrib.auth import get_user_model
from exams.views import ExamListCreateView
from results.views import student_dashboard_stats
from exams.models import Exam, ExamSchedule
from examinations.models import ExamSession
from django.utils import timezone

User = get_user_model()

def run_test():
    print("--- Starting Reproduction Script ---")
    
    # 1. Get student1
    try:
        user = User.objects.get(username='student1')
    except User.DoesNotExist:
        print("User 'student1' not found! Using 'test_student'")
        user, _ = User.objects.get_or_create(username='test_student', defaults={'role': 'student'})
    
    print(f"User: {user.username} (Role: {user.role})")

    # 2. Ensure at least one exam exists
    exam, created = Exam.objects.get_or_create(title="Test Exam", defaults={
        'duration_minutes': 60,
        'passing_score': 50,
        'description': 'Test Exam Description',
        'is_active': True
    })
    # Ensure schedule exists or doesn't (to test robustness)
    # Let's clean up schedules for this exam to test the "Missing Schedule" case which might be the cause
    ExamSchedule.objects.filter(exam=exam).delete()
    print(f"Exam: {exam.title} (ID: {exam.id}) - No Schedule")

    factory = APIRequestFactory()

    # 3. Test Exam List View
    print("\n[TEST] Testing ExamListCreateView...")
    view = ExamListCreateView.as_view()
    request = factory.get('/api/exams/')
    force_authenticate(request, user=user)
    
    try:
        response = view(request)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            results = response.data['results'] if isinstance(response.data, dict) and 'results' in response.data else response.data
            print(f"Got {len(results)} exams.")
            for i, ex in enumerate(results):
                # Access fields to ensure no lazy crash
                _ = ex.get('availability_window')
                _ = ex.get('student_status')
                # print(f"Exam {i}: ID {ex.get('id')} OK")
        else:
            print("Error:", response.data)
    except Exception as e:
        print(f"EXCEPTION in ExamListCreateView: {e}")
        import traceback
        traceback.print_exc()

    # 4. Test Student Dashboard Stats
    print("\n[TEST] Testing student_dashboard_stats...")
    request = factory.get('/api/results/dashboard/stats/')
    force_authenticate(request, user=user)
    
    # We need to wrap the function view to handle the request properly as DRF view
    # But for a function based view @api_view, we can call it directly with the requested object?
    # No, @api_view wraps it. Let's call it direct.
    try:
        response = student_dashboard_stats(request)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
             print("Data:", response.data)
        else:
             print("Error:", response.data)
    except Exception as e:
        print(f"EXCEPTION in student_dashboard_stats: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_test()
