from django.urls import path

from assessments import views

urlpatterns = [
    path(
        "view_assessments/",
        views.DisplayAssessment.as_view(),
        name="view_assessments",
    ),
]