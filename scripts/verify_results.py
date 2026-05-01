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
from examinations.models import ExamSession, ExamAnswer
from results.models import ExamResult

User = get_user_model()

def verify_results_logic():
    print("1. Setting up test data for results verification...")
    student, _ = User.objects.get_or_create(username='result_student', email='result@test.com')
    student.set_password('password123')
    student.role = 'student'
    student.save()
    
    exam, _ = Exam.objects.get_or_create(
        title='Result Test Exam',
        defaults={
            'duration_minutes': 60,
            'passing_score': 50,
            'is_active': True,
            'total_points': 100
        }
    )
    
    # Create a completed session
    session, created = ExamSession.objects.get_or_create(
        exam=exam,
        student=student,
        defaults={'status': 'submitted'}
    )
    if not created:
        session.status = 'submitted'
        session.save()
    
    # Create a result using update_or_create to avoid unique constraint violation
    ExamResult.objects.update_or_create(
        session=session,
        defaults={
            'total_points_earned': 80,
            'total_points_possible': 100,
            'percentage_score': 80,
            'passed': True
        }
    )
    
    print("2. Testing API Flow...")
    client = APIClient()
    
    # Login
    response = client.post('/api/auth/login/', {'username': 'result_student', 'password': 'password123'})
    token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    # Get Results
    response = client.get('/api/results/')
    if response.status_code == 200:
        results = response.data['results'] if 'results' in response.data else response.data
        print(f"   [PASS] API returned {len(results)} results")
        if len(results) > 0:
            # Look for the specific result for this exam
            found = False
            for result in results:
                if result['exam_title'] == 'Result Test Exam':
                    found = True
                    print(f"   Result Score: {result['percentage_score']}%")
                    if str(result['percentage_score']).startswith('80') or result['percentage_score'] == 80.0:
                         print("   [PASS] Score matches")
                    else:
                         print(f"   [FAIL] Score mismatch. Expected 80, got {result['percentage_score']}")
                    break
            
            if not found:
                print("   [FAIL] Could not find result for 'Result Test Exam'")
    else:
        print(f"   [FAIL] API failed with status {response.status_code}")

if __name__ == '__main__':
    verify_results_logic()
