"""
Custom middleware for authentication and security
"""
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta


class SecurityHeadersMiddleware:
    """Add security headers to responses"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Only add Strict-Transport-Security in production with HTTPS
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class ActivityLoggingMiddleware:
    """Log user activity for security monitoring"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Log login activity
            if request.path.startswith('/api/auth/login/'):
                cache_key = f"last_login_{request.user.id}"
                cache.set(cache_key, timezone.now().isoformat(), 86400)
        
        response = self.get_response(request)
        return response

