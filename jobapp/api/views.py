import jwt

from django.conf import settings

from rest_framework import response, status, views
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django_filters import rest_framework as filters

from .serializers import (ProfileSerializer,
                          RegisterSerializer,
                          UserSerializer,
                          CorporateSerializer,
                          CorporateWithJobSerializer,
                          JobSerializer,
                          )
from jobapp.models import User, Corporate, Profile, Job
from jobapp.permissions import IsCorporateOrJobOwner, IsCorporateJobOwner


class RegisterAPiView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(views.APIView):

    def post(self, request):
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
        profile = Profile.objects.filter(user=user).first()
        if profile:
            profile_serializer_data = ProfileSerializer(profile).data
            resp_data = {'profile': profile_serializer_data, 'token': auth_token}
            resp_status = status.HTTP_200_OK
            return response.Response(resp_data, status=resp_status)
        user_serializer_data = UserSerializer(user).data
        resp_data = {'user': user_serializer_data, 'token': auth_token}
        resp_status = status.HTTP_200_OK
        return response.Response(resp_data, status=resp_status)


class UserInfoByTokenView(views.APIView):

    def post(self, request):
        data = request.data
        token = data.get('token')
        if not token:
            return response.Response({"status": "Token's field not provided"}, status=status.HTTP_400_BAD_REQUEST)

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
        user = User.objects.filter(email=payload['email']).first()
        if not user:
            return response.Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        profile = Profile.objects.filter(user=user).first()
        if profile:
            profile_serializer_data = ProfileSerializer(profile).data
            resp_data = {'profile': profile_serializer_data}
            return response.Response(resp_data, status=status.HTTP_200_OK)
        user_serializer_data = UserSerializer(user).data
        return response.Response(user_serializer_data, status=status.HTTP_200_OK)


class CorporateViewset(ModelViewSet):
    queryset = Corporate.objects.all()
    permission_classes = (IsAuthenticated, IsCorporateOrJobOwner,)
    serializer_class = CorporateSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CorporateWithJobSerializer
        return self.serializer_class


class JobViewset(ModelViewSet):
    queryset = Job.objects.all()
    permission_classes = (IsAuthenticated, IsCorporateJobOwner,)
    serializer_class = JobSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('id', 'corporate', 'title', 'description', 'total_interest')


class ProfileViewset(ModelViewSet):
    queryset = Profile.objects.all()
    permission_classes = (IsAuthenticated, IsCorporateOrJobOwner,)
    serializer_class = ProfileSerializer


class ViewJobsView(ListAPIView):
    queryset = Job.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = JobSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('id', 'corporate', 'title', 'description', 'total_interest')

    # def get(self, request, *args, **kwargs):
    #     profile = Profile.objects.filter(user=request.user).first()
    #     response = super().get(request, *args, **kwargs)
    #     response.data['interest'] =


class ShowInterestJobView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        job = data.get('job')
        action = data.get('action', 'add')
        if not job:
            return response.Response({'error': 'Job id cannot be blank'}, status=status.HTTP_400_BAD_REQUEST)
        job = Job.objects.filter(pk=job).first()
        if not job:
            return response.Response({'error': 'No such job exist'}, status=status.HTTP_400_BAD_REQUEST)

        profile = Profile.objects.filter(user=request.user).first()
        if not profile:
            return response.Response({'error': 'Invalid Profile'}, status=status.HTTP_400_BAD_REQUEST)

        if job not in profile.interest_jobs:
            return response.Response({'error': 'Invalid request. Job already unintrested'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'remove':
            profile.interest_jobs.remove(job)
            profile.save()
            job.total_interest -= 1
            job.save()
        else:
            profile.interest_jobs.add(job)
            profile.save()
            job.total_interest += 1
            job.save()
        job_serializer = JobSerializer(job)
        return response.Response(job_serializer.data, status=status.HTTP_200_OK)
