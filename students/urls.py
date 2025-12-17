from django.urls import path

from students import views

urlpatterns = [
    path(
        "view_students/",
        views.DisplayStudent.as_view(),
        name="view_students",
    ),
]