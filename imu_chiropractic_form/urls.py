from django.conf import settings
from django.conf.urls.static import static
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
    path("accounts/", include("accounts.urls")),
    path("assessments/", include("assessments.urls")),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
