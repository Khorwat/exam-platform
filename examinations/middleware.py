"""
Security middleware for examination sessions
"""
from django.utils import timezone
from django.http import JsonResponse
from .models import ExamSession


class ExamSessionSecurityMiddleware:
    """
    Middleware to enforce security during exam sessions
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is in an active exam session
        if request.user.is_authenticated:
            active_sessions = ExamSession.objects.filter(
                student=request.user,
                status='in_progress'
            )
            
            for session in active_sessions:
                # Check time limit
                if session.check_time_limit():
                    continue
                
                # Log IP address changes (potential security issue)
                current_ip = request.META.get('REMOTE_ADDR')
                if session.ip_address and session.ip_address != current_ip:
                    # Log this as a potential security issue
                    # In production, you might want to invalidate the session
                    pass
        
        response = self.get_response(request)
        return response

