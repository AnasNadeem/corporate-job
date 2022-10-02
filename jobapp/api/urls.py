from .views import (
    CorporateViewset,
    JobViewset,
    ProfileViewset,
    UserViewset,
)
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns


router = routers.SimpleRouter(trailing_slash=False)
router.register(r"corporate", CorporateViewset, basename="corporate")
router.register(r"job", JobViewset, basename="job")
router.register(r"profile", ProfileViewset, basename="profile")
router.register(r"user", UserViewset, basename="user")

urlpatterns = []

urlpatterns += router.urls
urlpatterns = format_suffix_patterns(urlpatterns)
