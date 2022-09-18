from rest_framework import permissions
from jobapp.models import Corporate


class IsCorporateOrJobOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsCorporateJobOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        corporate = Corporate.objects.filter(user=request.user).first()
        if not corporate:
            return False

        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.corporate.user == request.user
