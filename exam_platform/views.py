"""
Views for serving frontend files
"""
from django.shortcuts import render
from django.conf import settings
import os


def serve_frontend(request, path=''):
    """Serve frontend HTML files"""
    if not path or path == '/':
        path = 'index.html'
    
    # Remove leading slash if present
    path = path.lstrip('/')
    
    # If path doesn't end with .html, assume it's a directory or needs extension
    if not path.endswith('.html'):
        path = f"{path}.html"
        
    # Check if template exists
    template_path = f"frontend/{path}"
    
    try:
        return render(request, template_path)
    except Exception:
        # Return 404 if file not found, to prevent redirect loops
        from django.http import Http404
        raise Http404(f"Frontend template {path} not found")

