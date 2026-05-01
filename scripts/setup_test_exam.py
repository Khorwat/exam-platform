import os
import sys
import django
import random

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from exams.models import Exam, ExamQuestion
from questions.models import Question, QuestionCategory
from examinations.models import ExamSession

User = get_user_model()

def setup_test_exam():
    print("Setting up Repeatable Test Exam...")
    
    # 1. Get or Create Instructor
    instructor = User.objects.filter(role='instructor').first()
    if not instructor:
        instructor = User.objects.create_user('test_instructor', 'inst@test.com', 'pass', role='instructor')
        print("Created test_instructor")

    # 2. Create/Get Category
    category, _ = QuestionCategory.objects.get_or_create(name="General Knowledge")

    # 3. Ensure we have 5 questions
    existing_questions = list(Question.objects.filter(category=category))
    
    # Prune extra or invalid ones nicely? Or just create needed.
    # We will use get_or_create to avoid unique errors if question_text is unique
    
    if len(existing_questions) < 5:
        print(f"Creating {5 - len(existing_questions)} new questions...")
        for i in range(len(existing_questions), 5):
            q_text = f"Test Question {i+1}: What is likely the answer?"
            q, created = Question.objects.get_or_create(
                question_text=q_text,
                category=category,
                defaults={
                    'question_type': 'multiple_choice',
                    'points': 1,
                    'created_by': instructor
                }
            )
            
            if created:
                # Add options
                q.options.create(option_text="Option A", is_correct=True)
                q.options.create(option_text="Option B", is_correct=False)
            
            existing_questions.append(q)
    
    # 4. Create the Exam
    exam_title = "Repeatable Test Exam (5 Questions)"
    exam, created = Exam.objects.get_or_create(title=exam_title)
    
    # Update fields
    exam.description = "A test exam you can take multiple times."
    exam.duration_minutes = 30
    exam.passing_score = 50
    exam.is_active = True
    exam.allow_retake = True # KEY FEATURE
    exam.show_results_immediately = True
    exam.randomize_questions = True
    exam.created_by = instructor
    exam.save()
    
    # 5. Link Questions
    # Clear existing
    ExamQuestion.objects.filter(exam=exam).delete()
    
    # Add 5 questions
    selected_questions = existing_questions[:5]
    for idx, q in enumerate(selected_questions):
        ExamQuestion.objects.create(
            exam=exam,
            question=q,
            order=idx
        )
        
    # 6. Calculate total points
    exam.calculate_total_points()
    
    print(f"\nSUCCESS! Exam '{exam.title}' is ready.")
    print(f"ID: {exam.id}")
    print(f"Questions: {exam.exam_questions.count()}")
    print("You can verify this in the frontend now.")

if __name__ == "__main__":
    try:
        setup_test_exam()
    except Exception as e:
        import traceback
        traceback.print_exc()
