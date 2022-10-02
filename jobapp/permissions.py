from rest_framework.permissions import IsAuthenticated
from jobapp.models import Corporate


class IsCorporate(IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        corporate = Corporate.objects.filter(user=request.user).first()
        if not corporate:
            return False
        return obj.user == request.user


class IsCorporateJobOwner(IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        corporate = Corporate.objects.filter(user=request.user).first()
        if not corporate:
            return False
        return obj.corporate.user == request.user
