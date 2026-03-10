from django.urls import path

from assessments import views, api

urlpatterns = [
    path(
        "",
        views.AssessmentListView.as_view(),
        name="assessments_list",
    ),
    path(
        "assessments/create/",
        views.AssessmentSection1FormView.as_view(),
        name="assessment_create",
    ),
    path(
        "<int:assessment_id>/section-1/",
        views.AssessmentSection1FormView.as_view(),
        name="assessment_section1_form",
    ),
    path(
        "<int:assessment_id>/section-2/",
        views.AssessmentSection2FormView.as_view(),
        name="assessment_section2_form",
    ),
    path(
        "<int:assessment_id>/section-3/",
        views.AssessmentSection3FormView.as_view(),
        name="assessment_section3_form",
    ),
    path(
        "<int:assessment_id>/section-4/",
        views.AssessmentSection4FormView.as_view(),
        name="assessment_section4_form",
    ),
    path(
        "<int:assessment_id>/treatment-plan/",
        views.AssessmentTreatmentPlanFormView.as_view(),
        name="assessment_treatment_plan_form",
    ),
    # API endpoints
    path(
        "api/assessments/",
        api.AssessmentsListAPIView.as_view(),
        name="assessments_list_api",
    ),
    path(
        "api/assessments/section-1-and-2/",
        api.AssessmentSection1And2APIView.as_view(),
        name="assessment_section1_and_2_api",
    ),
    path(
        "api/assessments/section-3/",
        api.AssessmentSection3APIView.as_view(),
        name="assessment_section3_api",
    ),
    path(
        "api/assessments/section-4/",
        api.AssessmentSection4APIView.as_view(),
        name="assessment_section4_api",
    ),
    path(
        "api/assessments/treatment-plan/",
        api.AssessmentTreatmentPlanAPIView.as_view(),
        name="assessment_treatment_plan_api",
    ),
]
