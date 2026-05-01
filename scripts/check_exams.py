import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from django.utils import timezone
from exams.models import Exam
from questions.models import Question

print("\n" + "="*60)
print("EXAM VISIBILITY CHECK")
print("="*60 + "\n")

exams = Exam.objects.all()

if exams.exists():
    print(f"Total exams in database: {exams.count()}\n")
    
    for exam in exams:
        print(f"Exam: {exam.title}")
        print(f"  ID: {exam.id}")
        print(f"  Description: {exam.description}")
        print(f"  Is Active: {exam.is_active}")
        print(f"  Start Time: {exam.start_time}")
        print(f"  End Time: {exam.end_time}")
        print(f"  Duration: {exam.duration_minutes} minutes")
        print(f"  Passing Score: {exam.passing_score}%")
        print(f"  Questions: {exam.exam_questions.count()}")
        
        # Check if exam is currently available
        now = timezone.now()
        if exam.start_time and exam.end_time:
            if now < exam.start_time:
                print(f"  Status: NOT YET STARTED (starts in {exam.start_time - now})")
            elif now > exam.end_time:
                print(f"  Status: ENDED (ended {now - exam.end_time} ago)")
            else:
                print(f"  Status: ACTIVE AND AVAILABLE")
        elif exam.start_time:
            if now < exam.start_time:
                print(f"  Status: NOT YET STARTED")
            else:
                print(f"  Status: STARTED (no end time set)")
        else:
            print(f"  Status: NO SCHEDULE SET (start_time is None)")
        
        print("-" * 60)
else:
    print("No exams found in the database.\n")

print("\n" + "="*60)
print("FIXING EXAM VISIBILITY")
print("="*60 + "\n")

# Update all exams to be visible
for exam in exams:
    exam.is_active = True
    if not exam.start_time:
        exam.start_time = timezone.now() - timedelta(hours=1)  # Started 1 hour ago
    if not exam.end_time:
        exam.end_time = timezone.now() + timedelta(days=30)  # Ends in 30 days
    exam.save()
    print(f"✓ Updated '{exam.title}' - Now active and available")

print("\n" + "="*60)
print("QUESTIONS CHECK")
print("="*60 + "\n")

questions = Question.objects.all()
print(f"Total questions in database: {questions.count()}\n")

if questions.count() > 0:
    for q in questions[:5]:  # Show first 5
        print(f"Question: {q.question_text[:50]}...")
        print(f"  Type: {q.question_type}")
        print(f"  Points: {q.points}")
        print(f"  Active: {q.is_active}")
        print("-" * 60)

print("\nDone! Exams should now be visible to students.")
