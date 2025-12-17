from django.urls import path
from .api import (
    UserProfileAPIView,
    UserProfileCreateAPIView,
    UserProfileUpdateAPIView,
    UserProfileDeleteAPIView,
)
from .views import UserListView

urlpatterns = [
    path("users/", UserListView.as_view(), name="user_list"),
    # API
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
