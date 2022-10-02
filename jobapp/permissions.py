from rest_framework.permissions import IsAuthenticated
from jobapp.models import Corporate


class IsCorporate(IsAuthenticated):

    def has_permission(self, request, view):
        corporate = Corporate.objects.filter(user=request.user).first()
        if not corporate:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsCorporateJobOwner(IsAuthenticated):

    def has_permission(self, request, view):
        corporate = Corporate.objects.filter(user=request.user).first()
        if not corporate:
            return False

        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.corporate.user == request.user
