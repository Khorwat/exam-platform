import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("\n" + "="*60)
print("EXISTING USERS IN THE DATABASE")
print("="*60 + "\n")

users = User.objects.all()

if users.exists():
    for user in users:
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Is Staff: {user.is_staff}")
        print(f"Is Superuser: {user.is_superuser}")
        print("-" * 60)
else:
    print("No users found in the database.")

print("\n" + "="*60)
print("TEACHER LOGIN CREDENTIALS")
print("="*60)
print("\nBased on the verification scripts, you can use:")
print("\nUsername: instructor1")
print("Password: password123")
print("Role: Instructor/Teacher")
print("\n" + "="*60 + "\n")
