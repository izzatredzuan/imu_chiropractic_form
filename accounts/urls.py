from django.urls import path
from accounts import views, api
# from .api import (
#     UserProfileAPIView,
#     UserProfileCreateAPIView,
#     UserProfileUpdateAPIView,
#     UserProfileDeleteAPIView,
# )
# from .views import UserListView

urlpatterns = [
    path("users/", views.UserListView.as_view(), name="user_list"),
    # API
    path("api/user/", api.UserProfileAPIView.as_view(), name="user_api"),
    path("api/user/create/", api.UserProfileCreateAPIView.as_view(), name="user_create_api"),
    path("api/user/update/", api.UserProfileUpdateAPIView.as_view(), name="user_update_api"),
    path("api/user/delete/", api.UserProfileDeleteAPIView.as_view(), name="user_delete_api"),
]
