import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_platform.settings')
django.setup()

from questions.models import QuestionCategory

categories = QuestionCategory.objects.all()
print(f"Total Categories: {categories.count()}")
for c in categories:
    print(f" - {c.id}: {c.name}")
