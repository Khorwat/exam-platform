import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from django.utils import timezone
from exams.models import Exam, ExamSchedule
from questions.models import Question

print("\n" + "="*60)
print("EXAM VISIBILITY DIAGNOSTIC")
print("="*60 + "\n")

exams = Exam.objects.all()

if exams.exists():
    print(f"Total exams in database: {exams.count()}\n")
    
    for exam in exams:
        print(f"Exam: {exam.title}")
        print(f"  ID: {exam.id}")
        print(f"  Description: {exam.description}")
        print(f"  Is Active: {exam.is_active}")
        print(f"  Duration: {exam.duration_minutes} minutes")
        print(f"  Passing Score: {exam.passing_score}%")
        print(f"  Questions: {exam.exam_questions.count()}")
        
        # Check if exam has a schedule
        has_schedule = hasattr(exam, 'schedule')
        if has_schedule:
            try:
                schedule = exam.schedule
                print(f"  Has Schedule: YES")
                print(f"    Start Date: {schedule.start_date}")
                print(f"    End Date: {schedule.end_date}")
                print(f"    Is Published: {schedule.is_published}")
                print(f"    Schedule Active: {schedule.is_active}")
                
                now = timezone.now()
                if not schedule.is_published:
                    print(f"  [!] ISSUE: Schedule exists but NOT PUBLISHED")
                elif now < schedule.start_date:
                    print(f"  [!] ISSUE: Exam hasn't started yet")
                elif now > schedule.end_date:
                    print(f"  [!] ISSUE: Exam has ended")
                else:
                    print(f"  [OK] Exam is currently available")
            except:
                print(f"  Has Schedule: NO")
                print(f"  [!] ISSUE: No schedule - students can't see this exam")
        else:
            print(f"  Has Schedule: NO")
            print(f"  [!] ISSUE: No schedule - students can't see this exam")
        
        print("-" * 60)
else:
    print("No exams found in the database.\n")

print("\n" + "="*60)
print("FIXING EXAM VISIBILITY ISSUES")
print("="*60 + "\n")

# Fix all exams
for exam in exams:
    # Make sure exam is active
    if not exam.is_active:
        exam.is_active = True
        exam.save()
        print(f"[OK] Activated exam: {exam.title}")
    
    # Create or update schedule
    schedule_created = False
    try:
        schedule = exam.schedule
        # Update existing schedule
        schedule.is_published = True
        if schedule.end_date < timezone.now():
            schedule.end_date = timezone.now() + timedelta(days=30)
        if schedule.start_date > timezone.now():
            schedule.start_date = timezone.now() - timedelta(hours=1)
        schedule.save()
        print(f"[OK] Updated schedule for: {exam.title}")
    except:
        # Create new schedule
        schedule = ExamSchedule.objects.create(
            exam=exam,
            start_date=timezone.now() - timedelta(hours=1),  # Started 1 hour ago
            end_date=timezone.now() + timedelta(days=30),    # Ends in 30 days
            is_published=True
        )
        print(f"[OK] Created schedule for: {exam.title}")

print("\n" + "="*60)
print("VERIFICATION")
print("="*60 + "\n")

available_exams = []
for exam in exams:
    if exam.is_active:
        try:
            schedule = exam.schedule
            if schedule.is_active:
                available_exams.append(exam.title)
        except:
            pass

if available_exams:
    print(f"[OK] {len(available_exams)} exam(s) now available to students:")
    for title in available_exams:
        print(f"  - {title}")
else:
    print("[!] No exams are currently available")

print("\n" + "="*60)
print("DONE!")
print("="*60)
print("\nStudents should now be able to see the exams.")
print("Try refreshing the student dashboard.\n")
