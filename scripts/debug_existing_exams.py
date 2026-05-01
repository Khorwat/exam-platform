import os
import django
import sys
import json
sys.path.append('c:/Users/mkhor/Downloads/Telegram Desktop/CODES')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from exams.models import Exam
from exams.serializers import ExamListSerializer

User = get_user_model()

def check_all_exams():
    print("\n--- Checking All Existing Exams for Serialization Errors ---")
    
    # Get a user context
    try:
        user = User.objects.filter(role='student').first()
        if not user:
            user = User.objects.create(username='debug_scan_student', role='student')
            print("Created temp student user.")
    except Exception as e:
        print(f"Error getting user: {e}")
        return

    # Create mock request context
    factory = APIRequestFactory()
    request = factory.get('/')
    request.user = user

    exams = Exam.objects.all()
    print(f"Found {exams.count()} exams in database.")
    
    context = {'request': request}
    
    for exam in exams:
        try:
            # Manually invoke fields that might crash
            print(f"Checking Exam ID {exam.id}: {exam.title[:30]}...", end='')
            
            serializer = ExamListSerializer(exam, context=context)
            data = serializer.data # Accessing .data triggers the serialization
            
            # Specifically check new fields
            # (although .data access calculates them)
            # print(f" [Win: {data.get('availability_window') is not None}]", end='')
            
            print(" ✅ OK")
            
        except Exception as e:
            print(f"\n❌ CRASH on Exam {exam.id} ({exam.title}): {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    check_all_exams()
