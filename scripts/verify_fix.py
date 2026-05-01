import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
import json
import sys

# Setup Django before other imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from questions.models import QuestionCategory

User = get_user_model()
try:
    user = User.objects.get(username='instructor1')
except User.DoesNotExist:
    user = User.objects.create_user('instructor1', 'instructor1@example.com', 'password123', role='instructor')

client = APIClient()
client.force_authenticate(user=user)

def print_resp(resp):
    print(f"Status: {resp.status_code}")
    if resp.status_code == 201:
        print("SUCCESS: Question created.")
    else:
        print("FAILURE: Question mock creation failed.")
        try:
             print(f"Data: {json.dumps(resp.json(), indent=2)}")
        except:
             print(f"Data: {resp.content}")

# 1. Ensure a category exists
category = QuestionCategory.objects.first()
if not category:
    category = QuestionCategory.objects.create(name="Debug Category")

print(f"Using category: {category.id} - {category.name}")

# This payload represents what the FIXED frontend will send (guaranteed to have a category)
print("\n--- Testing FIXED Frontend Payload (Valid Category) ---")
valid_payload = {
    "question_text": "Detailed Verification Question",
    "question_type": "multiple_choice",
    "difficulty": "medium",
    "category": category.id,
    "points": 5,
    "explanation": "This simulates a correct submission.",
    "is_active": True,
    "options": [
        {"option_text": "Correct Option", "is_correct": True, "order": 1},
        {"option_text": "Wrong Option", "is_correct": False, "order": 2}
    ]
}
resp = client.post('/api/questions/', valid_payload, format='json')
print_resp(resp)
