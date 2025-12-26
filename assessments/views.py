from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import (
    render,
)
from django.views import View
from accounts.models import Profile
from assessments.models import Assessments


class AssessmentListView(View):
    template_name = "assessments/assessments.html"

    def get(self, request):
        return render(request, self.template_name)


class AssessmentSection1FormView(View):
    template_name = "assessments/section1_form.html"

    def get(self, request):
        profile = request.user.profile

        # Only student & admin allowed
        # if profile.role not in ["student", "admin"]:
        #     return HttpResponseForbidden("You are not allowed to access this page.")

        # Check for assessment ID for edit mode
        assessment_id = request.GET.get("id")
        context = {}

        if assessment_id:
            try:
                assessment = Assessments.objects.get(id=assessment_id)
            except Assessments.DoesNotExist:
                return HttpResponseNotFound("Assessment not found.")

            # Permission check for student
            if profile.role == "student" and assessment.student != profile:
                return HttpResponseForbidden("You cannot edit this assessment.")

            context["assessment_id"] = assessment_id
            context["assessment"] = assessment

        # Set read-only for clinicians
        is_readonly = request.user.profile.role == "clinician"
        context["is_readonly"] = is_readonly

        # For admin, show all students and clinicians
        if profile.role == "admin":
            context["students"] = Profile.objects.filter(role="student").order_by(
                "official_name"
            )
            context["clinicians"] = Profile.objects.filter(role="clinician").order_by(
                "official_name"
            )

        # For student, only show clinicians
        if profile.role == "student":
            context["clinicians"] = Profile.objects.filter(role="clinician").order_by(
                "official_name"
            )

        return render(request, self.template_name, context)
