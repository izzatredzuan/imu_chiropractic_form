from django.contrib import admin
from django.urls import include, path
from imu_chiropractic_form import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "",
        views.Home.as_view(),
        name="Home",
    ),
    path("", include("accounts.urls")),
    path("", include("students.urls")),
    path("", include("clinicians.urls")),
    path("", include("assessments.urls")),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]
