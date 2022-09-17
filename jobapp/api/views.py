import jwt

from django.conf import settings

from rest_framework import response, status, views
from rest_framework.generics import GenericAPIView
# from rest_framework.viewsets import ModelViewSet

from .serializers import (RegisterSerializer,
                          UserSerializer,
                          )
from jobapp.models import User


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
        user_serializer_data = UserSerializer(user).data
        resp_data = {'user': user_serializer_data, 'token': auth_token}
        resp_status = status.HTTP_200_OK
        return response.Response(resp_data, status=resp_status)


class LoginApiByTokenView(GenericAPIView):

    def post(self, request):
        data = request.data
        token = data.get('token')
        if not token:
            return response.Response({"status": "Token's field not provided"}, status=status.HTTP_400_BAD_REQUEST)

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
        user = User.objects.filter(email=payload['email']).first()
        if user:
            user_serializer_data = UserSerializer(user).data
            return response.Response(user_serializer_data, status=status.HTTP_200_OK)
        return response.Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
