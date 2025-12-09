from django.urls import path
from .api import (
    UserProfileAPIView,
    UserProfileCreateAPIView,
    UserProfileUpdateAPIView,
    UserProfileDeleteAPIView,
)

urlpatterns = [
    path("api/user/", UserProfileAPIView.as_view(), name="user_api"),
    path(
        "api/user/create/", UserProfileCreateAPIView.as_view(), name="user_create_api"
    ),
    path(
        "api/user/update/", UserProfileUpdateAPIView.as_view(), name="user_update_api"
    ),
    path(
        "api/user/delete/", UserProfileDeleteAPIView.as_view(), name="user_delete_api"
    ),
]
