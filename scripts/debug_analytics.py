import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from results.views import PerformanceAnalyticsListView, exam_statistics
from exams.models import Exam

User = get_user_model()

def test_analytics():
    print("Testing Analytics API...")
    try:
        # Get a user (instructor)
        user = User.objects.filter(role='instructor').first()
        if not user:
            print("No instructor found, creating one.")
            user = User.objects.create_user(username='test_inst', password='password', role='instructor')
        else:
            print(f"Using instructor: {user.username}")

        factory = APIRequestFactory()

        # 1. Check Data Existence
        from results.models import ExamResult, PerformanceAnalytics
        from examinations.models import ExamSession

        print(f"Total Sessions: {ExamSession.objects.count()}")
        print(f"Total Results: {ExamResult.objects.count()}")
        print(f"Total Analytics Records: {PerformanceAnalytics.objects.count()}")

        # 2. Test Analytics List
        view = PerformanceAnalyticsListView.as_view()
        request = factory.get('/api/results/analytics/')
        force_authenticate(request, user=user)
        response = view(request)
        print(f"Analytics List Status: {response.status_code}")
        # print(f"Analytics List Data: {response.data}")

        # 3. Test Exam Stats (Pick an exam OWNED by this user)
        exam = Exam.objects.filter(created_by=user).first()
        if exam:
            print(f"Testing stats for exam: {exam.title} (ID: {exam.id})")
            request = factory.get(f'/api/results/exams/{exam.id}/statistics/')
            force_authenticate(request, user=user)
            response = exam_statistics(request, exam_id=exam.id)
            print(f"Exam Stats Status: {response.status_code}")
            print(f"Exam Stats Data: {response.data}")
        else:
            print("No exams owned by this user found. Picking ANY exam to check permission error...")
            exam = Exam.objects.first()
            if exam:
                print(f"Testing stats for exam: {exam.title} (Owned by {exam.created_by.username})")
                request = factory.get(f'/api/results/exams/{exam.id}/statistics/')
                force_authenticate(request, user=user)
                response = exam_statistics(request, exam_id=exam.id)
                print(f"Exam Stats Status: {response.status_code}")
                # Expected 403 if not owner
            else:
                print("No exams found at all.")


        # 4. Create Dummy Analytics and Fetch
        print("Creating dummy analytics record...")
        try:
             # Ensure we have an exam and student
            exam = Exam.objects.first()
            student = User.objects.filter(role='student').first()
            if not student:
                 student = User.objects.create_user(username='test_student', password='password', role='student')
            
            if exam and student:
                 pa, created = PerformanceAnalytics.objects.get_or_create(
                     exam=exam,
                     student=student,
                     defaults={'average_score': 85.5, 'total_exams_taken': 1}
                 )
                 print(f"Analytics Record ID: {pa.id}")
                 
                 # Now fetch as ADMIN to see if serialization works
                 admin_user = User.objects.filter(role='administrator').first()
                 if not admin_user:
                     print("Creating admin user...")
                     admin_user = User.objects.create_user(username='test_admin', password='password', role='administrator')
                 
                 request = factory.get('/api/results/analytics/')
                 force_authenticate(request, user=admin_user)
                 response = view(request)
                 print(f"Admin Analytics List Status: {response.status_code}")
                 print(f"Admin Analytics List Data: {response.data}")
            else:
                 print("Missing exam or student for dummy data.")

        except Exception as e:
            print(f"Error during dummy creation: {e}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_analytics()
