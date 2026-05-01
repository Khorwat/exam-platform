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
    # Use create_user not create_superuser for more realistic test unless needed
    user = User.objects.create_user('instructor1', 'instructor1@example.com', 'password123', role='instructor')
    print("Created user instructor1")

client = APIClient()
client.force_authenticate(user=user)

def print_resp(resp):
    print(f"Status: {resp.status_code}")
    try:
        if hasattr(resp, 'json'):
            print(f"Data: {json.dumps(resp.json(), indent=2)}")
        else:
            print(f"Data: {resp.content}")
    except:
        print(f"Data: {resp.data}")

# 1. Ensure a category exists
category_count = QuestionCategory.objects.count()
print(f"Total categories: {category_count}")

category = QuestionCategory.objects.first()
if not category:
    category = QuestionCategory.objects.create(name="Debug Category")
    print("Created new category")

print(f"Using category: {category.id} - {category.name}")

# Valid payload template
valid_payload = {
    "question_text": "Debug Question Valid",
    "question_type": "multiple_choice",
    "difficulty": "medium",
    "category": category.id,
    "points": 5,
    "explanation": "test",
    "is_active": True,
    "options": [
        {"option_text": "A", "is_correct": True, "order": 1},
        {"option_text": "B", "is_correct": False, "order": 2}
    ]
}

# 2. Test payload with VALID category
print("\n--- Testing Valid Creation ---")
resp = client.post('/api/questions/', valid_payload, format='json')
print_resp(resp)

# 3. Test payload with EMPTY STRING category
print("\n--- Testing Empty String Category ---")
invalid_payload = valid_payload.copy()
invalid_payload['category'] = "" 
resp = client.post('/api/questions/', invalid_payload, format='json')
print_resp(resp)

# 4. Test payload without category
print("\n--- Testing Missing Category ---")
missing_payload = valid_payload.copy()
del missing_payload['category']
resp = client.post('/api/questions/', missing_payload, format='json')
print_resp(resp)
