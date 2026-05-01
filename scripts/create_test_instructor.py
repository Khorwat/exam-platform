
import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

User = get_user_model()

# Create Instructor User
username = 'test_instructor'
password = 'password123'
email = 'instructor@test.com'

try:
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, email=email, password=password)
        user.role = 'instructor'
        user.is_staff = True
        user.save()
        print(f"User {username} created successfully.")
    else:
        print(f"User {username} already exists.")
except Exception as e:
    print(f"Error creating user: {e}")
