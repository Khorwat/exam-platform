from rest_framework import permissions


class IsAdministrator(permissions.BasePermission):
    """Permission check for administrators"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_administrator


class IsInstructor(permissions.BasePermission):
    """Permission check for instructors"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_instructor or request.user.is_administrator
        )


class IsStudent(permissions.BasePermission):
    """Permission check for students"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_student


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission check for object owners or administrators"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_administrator:
            return True
        return obj == request.user

