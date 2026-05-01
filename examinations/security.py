"""
Security utilities for examination system
"""
import hashlib
import time
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone


def generate_session_token(user_id, exam_id):
    """Generate a unique session token"""
    timestamp = str(time.time())
    data = f"{user_id}_{exam_id}_{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()


def check_rate_limit(user_id, action, limit=10, window=60):
    """Check if user has exceeded rate limit for an action"""
    key = f"rate_limit_{user_id}_{action}"
    count = cache.get(key, 0)
    
    if count >= limit:
        return False
    
    cache.set(key, count + 1, window)
    return True


def log_suspicious_activity(user_id, exam_id, activity_type, details):
    """Log suspicious activity for review"""
    # In production, this should write to a secure log or database
    cache_key = f"suspicious_{user_id}_{exam_id}_{int(time.time())}"
    cache.set(cache_key, {
        'user_id': user_id,
        'exam_id': exam_id,
        'activity_type': activity_type,
        'details': details,
        'timestamp': timezone.now().isoformat()
    }, 86400)  # Keep for 24 hours


def validate_exam_access(user, exam, session=None):
    """Validate if user can access the exam"""
    from exams.models import ExamSchedule
    
    # Check if exam is active
    if not exam.is_active:
        return False, "Exam is not active"
    
    # Check schedule
    if hasattr(exam, 'schedule'):
        schedule = exam.schedule
        if not schedule.is_published:
            return False, "Exam is not published"
        
        now = timezone.now()
        if now < schedule.start_date:
            return False, "Exam has not started yet"
        if now > schedule.end_date:
            return False, "Exam has ended"
    
    # Check if retake is allowed
    if not exam.allow_retake and session:
        existing_sessions = ExamSession.objects.filter(
            exam=exam,
            student=user,
            status__in=['submitted', 'time_up']
        ).exists()
        if existing_sessions:
            return False, "You have already taken this exam"
    
    return True, "Access granted"

