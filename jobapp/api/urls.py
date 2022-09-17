from django.urls import path
from .views import (
    RegisterAPiView,
    LoginApiView,
    LoginApiByTokenView,
)

urlpatterns = [
    # Authentication Urls
    path('register/', RegisterAPiView.as_view(), name='register'),
    path('login/', LoginApiView.as_view(), name='login'),
    path('login_by_token/', LoginApiByTokenView.as_view(), name='login-by-token'),
]
