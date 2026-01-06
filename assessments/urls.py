from django.urls import path

from assessments import views, api

urlpatterns = [
    path(
        "",
        views.AssessmentListView.as_view(),
        name="assessments_list",
    ),
    path(
        "section-1/form/",
        views.AssessmentSection1FormView.as_view(),
        name="assessment_section1_form",
    ),
    path(
        "section-2/form/",
        views.AssessmentSection2FormView.as_view(),
        name="assessment_section2_form",
    ),
    path(
        "api/assessments/",
        api.AssessmentsListAPIView.as_view(),
        name="assessments_list_api",
    ),
    # For creating Section 1, might need to change the name later if used for update as well
    path(
        "api/assessments/section-1/",
        api.AssessmentSection1APIView.as_view(),
        name="assessment_section1_api",
    ),
]
