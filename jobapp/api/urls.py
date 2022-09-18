from django.urls import path
from .views import (
    RegisterAPiView,
    LoginApiView,
    UserInfoByTokenView,
    CorporateViewset,
    JobViewset,
    ViewJobsView,
    ShowInterestJobView,
    ProfileViewset,
)
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns


router = routers.SimpleRouter(trailing_slash=False)
router.register(r"corporate", CorporateViewset, basename="corporate")
router.register(r"job", JobViewset, basename="job")
router.register(r"profile", ProfileViewset, basename="profile")

urlpatterns = [
    # Authentication Urls
    path('register/', RegisterAPiView.as_view(), name='register'),
    path('login/', LoginApiView.as_view(), name='login'),
    path('user_info_by_token/', UserInfoByTokenView.as_view(), name='login-by-token'),
    path('all_jobs/', ViewJobsView.as_view(), name='view-jobs'),
    path('job_interest/', ShowInterestJobView.as_view(), name='like-job'),
]

urlpatterns += router.urls
urlpatterns = format_suffix_patterns(urlpatterns)
