import os
import django
import sys
import json

sys.path.append('c:/Users/mkhor/Downloads/Telegram Desktop/CODES')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse

User = get_user_model()

def debug_login():
    print("\n--- Debugging Login & Roles ---")
    client = APIClient()

    # 1. Check/Create Utilities
    try:
        student, _ = User.objects.get_or_create(username='debug_student', email='std@debug.com', defaults={'role': 'student'})
        student.set_password('pass123')
        student.save()
        
        instructor, _ = User.objects.get_or_create(username='debug_instructor', email='inst@debug.com', defaults={'role': 'instructor'})
        instructor.set_password('pass123')
        instructor.save()
        
        admin, _ = User.objects.get_or_create(username='debug_admin', email='adm@debug.com', defaults={'role': 'administrator'})
        admin.set_password('pass123')
        admin.save()
    except Exception as e:
        print(f"Error setting up users: {e}")
        return

    # 2. Test Logic
    for username, expected_role in [('debug_student', 'student'), ('debug_instructor', 'instructor'), ('debug_admin', 'administrator')]:
        print(f"\nTesting login for: {username} (Expect: {expected_role})")
        
        url = '/api/auth/login/' # Assuming this is the endpoint
        response = client.post(url, {'username': username, 'password': 'pass123'}, format='json')
        
        if response.status_code == 200:
            data = response.data
            user_data = data.get('user', {})
            actual_role = user_data.get('role')
            print(f"Login Success. Token acquired.")
            print(f"Role in response: '{actual_role}'")
            
            if actual_role == expected_role:
                print("✅ Role matches expected.")
            else:
                print(f"❌ ROLE MISMATCH! Expected '{expected_role}', got '{actual_role}'")
                
            # Check keys
            print("Keys in user object:", list(user_data.keys()))
        else:
            print(f"❌ Login Failed: {response.status_code} - {response.data}")

    # 3. Test Registration
    print("\n--- Testing Registration ---")
    reg_data = {
        'username': 'new_instructor_v2',
        'email': 'new_inst_v2@test.com',
        'password': 'ComplexPassword123!',
        'password_confirm': 'ComplexPassword123!',
        'first_name': 'New',
        'last_name': 'Instructor',
        'role': 'instructor'
    }
    
    try:
        # Clean up if exists
        try:
            u = User.objects.get(username='new_instructor_v2')
            u.delete()
        except User.DoesNotExist:
            pass
            
        # Clean up debug_instructor too to verify creation
        try:
            u = User.objects.get(username='debug_instructor')
            u.delete()
        except User.DoesNotExist:
            pass
        
        # Re-create debug_instructor freshly
        instructor, _ = User.objects.get_or_create(username='debug_instructor', email='inst@debug.com', defaults={'role': 'instructor'})
        instructor.set_password('ComplexPassword123!')
        instructor.save()
        print(f"debug_instructor Re-created. Role in object: '{instructor.role}'")


        response = client.post('/api/auth/register/', reg_data, format='json')
        if response.status_code == 201:
            user_data = response.data.get('user', {})
            actual_role = user_data.get('role')
            print(f"Registration Success. Role: '{actual_role}'")
            if actual_role == 'instructor':
                print("✅ Registration Role Correct.")
            else:
                print(f"❌ REGISTRATION ROLE MISMATCH! Expected 'instructor', got '{actual_role}'")
                
            # Verify DB Persistence
            db_user = User.objects.get(username='new_instructor_v2')
            print(f"DB Check Role: '{db_user.role}'")
            if db_user.role == 'instructor':
                print("✅ DB Persistence Correct.")
            else:
                 print("❌ DB PERSISTENCE FAILED.")

        else:
             print(f"❌ Registration Failed: {response.status_code} - {response.data}")

    except Exception as e:
        print(f"Registration Test Error: {e}")

if __name__ == '__main__':
    debug_login()
