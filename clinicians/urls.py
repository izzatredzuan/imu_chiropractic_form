from django.urls import path

from clinicians import views

urlpatterns = [
    path(
        "view_clinicians/",
        views.DisplayClinician.as_view(),
        name="view_clinicians",
    ),
]