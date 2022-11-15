import jwt

from django.conf import settings

from rest_framework import response, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django_filters import rest_framework as filters

from .serializers import (
    CorporateSerializer,
    CorporateWithJobSerializer,
    JobSerializer,
    JobsWithIntrestedProfileerializer,
    JobInterestSerializer,
    LoginSerializer,
    ProfileSerializer,
    ProfileWithUserSerializer,
    RegisterUserSerializer,
    RegisterSerializer,
    TokenSerializer,
    UserSerializer,
)
from jobapp.models import User, Corporate, Profile, Job
from jobapp.permissions import IsCorporate, IsCorporateJobOwner


class UserViewset(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = ()

    # def get_permissions(self):
    #     user_permission_map = {
    #         "update": UserPermission
    #     }
    #     if user_permission_map.get(self.action.lower()):
    #         self.permission_classes = user_permission_map.get(self.action.lower())
    #     return super().get_permissions()

    def get_serializer_class(self):
        user_serializer_map = {
            "register_user": RegisterUserSerializer,
            "register": RegisterSerializer,
            "login": LoginSerializer,
            "user_info_by_token": TokenSerializer,
        }
        return user_serializer_map.get(self.action.lower(), UserSerializer)

    @action(detail=False, methods=['post'])
    def register_user(self, request):
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.filter(email=serializer.data.get('email')).first()
        user_serializer = UserSerializer(user)
        return response.Response(user_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def register(self, request):
        data = request.data
        serializer = self.get_serializer_class()
        serializer = serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.filter(email=serializer.data['email']).first()
        if not user:
            return response.Response({'error': 'Register error. Try again'}, status=status.HTTP_400_BAD_REQUEST)

        auth_token = jwt.encode({'email': user.email}, settings.SECRET_KEY, algorithm='HS256')
        user_serializer = UserSerializer(user)
        resp_data = {'user': user_serializer.data, 'token': auth_token}

        corporate = Corporate.objects.filter(user=user).first()
        if corporate:
            resp_data['is_corporate'] = True
            corporate_serializer = CorporateSerializer(corporate)
            resp_data['data'] = corporate_serializer.data

        profile = Profile.objects.filter(user=user).first()
        if profile:
            resp_data['is_corporate'] = False
            profile_serializer = ProfileSerializer(profile)
            resp_data['data'] = profile_serializer.data

        resp_status = status.HTTP_201_CREATED
        return response.Response(resp_data, status=resp_status)

    @action(detail=False, methods=['put'])
    def login(self, request):
        data = request.data
        email = data.get('email', '')
        password = data.get('password', '')
        user = User.objects.filter(email=email).first()
        if not user:
            return response.Response({'error': 'User does not exist'}, status=status.HTTP_401_UNAUTHORIZED)

        authenticated = user.check_password(password)
        if not authenticated:
            return response.Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        auth_token = jwt.encode({'email': user.email}, settings.SECRET_KEY, algorithm='HS256')
        resp_data = {'token': auth_token}

        profile = Profile.objects.filter(user=user).first()
        if profile:
            profile_serializer_data = ProfileSerializer(profile).data
            resp_data['data'] = profile_serializer_data
            resp_data['is_corporate'] = False

        corporate = Corporate.objects.filter(user=user).first()
        if corporate:
            corporate_serializer_data = CorporateWithJobSerializer(corporate).data
            resp_data['data'] = corporate_serializer_data
            resp_data['is_corporate'] = True

        resp_status = status.HTTP_200_OK
        return response.Response(resp_data, status=resp_status)

    @action(detail=False, methods=['put'])
    def user_info_by_token(self, request):
        data = request.data
        token = data.get('token')
        if not token:
            return response.Response({"status": "Token's field not provided"}, status=status.HTTP_400_BAD_REQUEST)

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
        resp_data = {'token': token}
        user = User.objects.filter(email=payload['email']).first()
        if not user:
            return response.Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        profile = Profile.objects.filter(user=user).first()
        if profile:
            profile_serializer_data = ProfileSerializer(profile).data
            resp_data['data'] = profile_serializer_data

        corporate = Corporate.objects.filter(user=user).first()
        if corporate:
            corporate_serializer_data = CorporateWithJobSerializer(corporate).data
            resp_data['data'] = corporate_serializer_data

        resp_status = status.HTTP_200_OK
        return response.Response(resp_data, status=resp_status)


class CorporateViewset(ModelViewSet):
    queryset = Corporate.objects.all()
    permission_classes = (IsCorporate, )
    serializer_class = CorporateSerializer

    def get_serializer_class(self):
        corporate_serializer_map = {
            "list": CorporateWithJobSerializer,
            "retrieve": CorporateWithJobSerializer,
            "jobs": CorporateWithJobSerializer,
        }
        return corporate_serializer_map.get(self.action.lower(), CorporateSerializer)

    @action(detail=True, methods=['get'])
    def jobs(self, request, pk=None):
        corporate = self.get_object()
        serializer = self.get_serializer_class()
        serializer = serializer(corporate)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class JobViewset(ModelViewSet):
    queryset = Job.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = JobSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('id', 'corporate', 'title', 'description', 'total_interest')

    def get_permissions(self):
        job_permission_map = {
            "destroy": IsCorporateJobOwner,
            "update": IsCorporateJobOwner,
            "partial_update": IsCorporateJobOwner,
            "create": IsCorporate,
        }
        permission_classes = [job_permission_map.get(self.action.lower(), IsAuthenticated)]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        job_serializer_map = {
            "job_interest": JobInterestSerializer,
        }

        if self.request.user.is_authenticated and Corporate.objects.filter(user=self.request.user).exists():
            job_serializer_map['list'] = JobsWithIntrestedProfileerializer

        return job_serializer_map.get(self.action.lower(), JobSerializer)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Job.objects.none()

        corporate = Corporate.objects.filter(user=user).first()
        if not corporate:
            return Job.objects.all()

        return corporate.job_set.all()

    @action(detail=True, methods=['put'])
    def job_interest(self, request, pk=None):
        job = self.get_object()
        data = request.data
        action = data.get('action', 'add')
        profile = Profile.objects.filter(user=request.user).first()
        if not profile:
            return response.Response({'error': 'Invalid Profile'}, status=status.HTTP_400_BAD_REQUEST)

        if job.profile_set.filter(pk=profile.pk).exists() and action == 'add':
            return response.Response({'error': 'Job already in intrested'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'remove':
            profile.interest_jobs.remove(job)
            profile.save()

            job.total_interest -= 1
            job.interested_users.remove(profile)
            job.save()
        else:
            profile.interest_jobs.add(job)
            profile.save()

            job.total_interest += 1
            job.interested_users.add(profile)
            job.save()

        job_serializer = JobSerializer(job)
        return response.Response(job_serializer.data, status=status.HTTP_200_OK)


class ProfileViewset(ModelViewSet):
    queryset = Profile.objects.all()
    permission_classes = (IsAuthenticated, IsCorporate)
    serializer_class = ProfileWithUserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('id', 'user')

    def get_serializer_class(self):
        profile_serializer_map = {
            "create": ProfileSerializer,
        }
        return profile_serializer_map.get(self.action.lower(), ProfileSerializer)
