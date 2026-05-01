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
from exams.models import Exam, ExamQuestion
from questions.models import Question, QuestionOption
from examinations.models import ExamSession, ExamAnswer
from rest_framework.test import APIClient

User = get_user_model()

def run_test():
    print("\n--- Verifying Full Exam Session Flow ---")
    client = APIClient()

    # 1. Setup Data
    # Student
    student, _ = User.objects.get_or_create(username='flow_student', email='flow@test.com')
    student.set_password('pass123')
    student.save()
    
    # Instructor
    instr, _ = User.objects.get_or_create(username='flow_instr', email='inst@test.com', defaults={'role': 'instructor'})
    instr.save()

    # Exam
    exam = Exam.objects.create(
        title="Full Flow Exam",
        duration_minutes=30,
        created_by=instr,
        is_active=True
    )
    from exams.models import ExamSchedule
    ExamSchedule.objects.create(
        exam=exam,
        start_date=timezone.now() - timedelta(hours=1),
        end_date=timezone.now() + timedelta(hours=5),
        is_published=True
    )
    
    # Questions (MCQ + Code)
    q1 = Question.objects.create(
        question_text="What is 2+2?",
        question_type="multiple_choice",
        points=5,
        created_by=instr
    )
    opt1 = QuestionOption.objects.create(question=q1, option_text="3", is_correct=False, order=1)
    opt2 = QuestionOption.objects.create(question=q1, option_text="4", is_correct=True, order=2)
    
    q2 = Question.objects.create(
        question_text="Write a python function",
        question_type="code",
        points=10,
        created_by=instr
    )
    
    # Link to Exam
    ExamQuestion.objects.create(exam=exam, question=q1, order=1)
    ExamQuestion.objects.create(exam=exam, question=q2, order=2)
    
    # Authenticate
    client.force_authenticate(user=student)
    print("Locked and Loaded. Starting sequence...")

    # 2. Start Exam
    print(f"\n[STEP 1] Starting Exam {exam.id}...")
    resp = client.post('/api/examinations/start/', {'exam_id': exam.id}, format='json')
    if resp.status_code != 201:
        print(f"❌ Failed to start exam: {resp.status_code} {resp.data}")
        return
    else:
        print("✅ Exam Started")
        session_id = resp.data['id']
        # Check integrity of questions returned
        returned_qs = resp.data.get('questions', [])
        print(f"   Received {len(returned_qs)} questions in payload.")

    # 3. Submit MCQ Answer
    print(f"\n[STEP 2] Submitting MCQ Answer...")
    payload_mcq = {
        'question_id': q1.id,
        'selected_option_id': opt2.id, # Correct answer
        'short_answer_text': None
    }
    resp = client.post(f'/api/examinations/sessions/{session_id}/submit-answer/', payload_mcq, format='json')
    if resp.status_code != 200:
        print(f"❌ Failed to submit MCQ: {resp.status_code} {resp.data}")
    else:
        print(f"✅ MCQ Answer Submitted. Points: {resp.data.get('points_earned')}")

    # 4. Submit Code Answer
    print(f"\n[STEP 3] Submitting Code Answer...")
    payload_code = {
        'question_id': q2.id,
        'short_answer_text': "def hello(): print('world')",
        'selected_option_id': None
    }
    resp = client.post(f'/api/examinations/sessions/{session_id}/submit-answer/', payload_code, format='json')
    if resp.status_code != 200:
        print(f"❌ Failed to submit Code: {resp.status_code} {resp.data}")
    else:
        # Code questions should have 0 points initially (awaiting manual grade)
        print(f"✅ Code Answer Submitted. Points (Expect 0): {resp.data.get('points_earned')}")

    # 5. Finish Exam
    print(f"\n[STEP 4] Submitting Exam...")
    resp = client.post(f'/api/examinations/sessions/{session_id}/submit/', {}, format='json')
    if resp.status_code != 200:
        print(f"❌ Failed to finish exam: {resp.status_code} {resp.data}")
    else:
        print("✅ Exam Finished.")
        print(f"   Status (Session): {resp.data.get('session', {}).get('status')}")
        print(f"   Percentage: {resp.data.get('percentage')}")
        print(f"   Passed: {resp.data.get('passed')}")

    # Cleanup
    # user/exam deletion if needed

if __name__ == '__main__':
    run_test()
