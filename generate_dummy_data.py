
import os
import sys
import django
import random
from django.core.files.base import ContentFile
from django.db import transaction

# Setup Django environment manually if needed (though shell does it)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from exams.models import Exam
from examinations.models import ExamSession, ProctoringSnapshot

User = get_user_model()

def create_dummy_data():
    try:
        print("Starting dummy data generation...", flush=True)
        
        # 1. Get or create a student
        student, created = User.objects.get_or_create(username='student_monitor_test', defaults={'email': 'monitor_test@example.com'})
        if created:
            student.set_password('password123')
            student.save()
            print(f"Created student: {student.username}", flush=True)
        else:
            print(f"Using existing student: {student.username}", flush=True)
        
        # 2. Get an active exam (or create one)
        exam = Exam.objects.filter(is_active=True).first()
        if not exam:
            print("No active exam found! Creating one Temporarily...", flush=True)
            exam = Exam.objects.create(
                title="Live Monitor Test Exam",
                duration_minutes=60,
                is_active=True,
                created_by=student # Just to assign someone
            )
        
        print(f"Using exam: {exam.title} (ID: {exam.id})", flush=True)

        # 3. Create an active session
        session, created = ExamSession.objects.get_or_create(
            exam=exam,
            student=student,
            defaults={'status': 'in_progress'}
        )
        # Force status to in_progress just in case
        session.status = 'in_progress'
        session.save()
            
        print(f"Active session ID: {session.id}", flush=True)

        # 4. Create dummy snapshots
        dummy_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        # Create a few snapshots
        for i in range(5):
            snapshot = ProctoringSnapshot.objects.create(
                session=session,
                trust_score=random.uniform(0.5, 1.0),
                issue_type=random.choice([None, None, 'looking_away', 'multiple_faces']),
                face_data={'x': 0.5, 'y': 0.5, 'width': 0.2, 'height': 0.2}
            )
            snapshot.image.save(f'dummy_{session.id}_{i}.png', ContentFile(dummy_image_content), save=True)
            print(f"Created snapshot {snapshot.id}", flush=True)
            
        print("Dummy data generation COMPLETED SUCCESSFULLY.", flush=True)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_dummy_data()
