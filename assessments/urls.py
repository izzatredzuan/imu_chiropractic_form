from django.urls import path

from assessments import views

urlpatterns = [
    path(
        "assessments/view_assessments/",
        views.DisplayAssessment.as_view(),
        name="view_assessments",
    ),
]