from django.contrib import admin
from django.urls import path
from imu_chiropractic_form import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        "",
        views.Home.as_view(),
        name="Home",
    ),
]
