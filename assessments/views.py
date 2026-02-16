from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import (
    render,
)
from django.views import View
from accounts.models import Profile
from .models import Assessments
from .utils import (
    clinician_is_readonly,
)


class AssessmentListView(View):
    template_name = "assessments/assessments.html"

    def get(self, request):
        return render(request, self.template_name)


class AssessmentSection1FormView(View):
    template_name = "assessments/section1_form.html"

    def get(self, request):
        profile = request.user.profile
        assessment_id = request.GET.get("id")
        context = {}
        assessment = None
        is_readonly = False

        # =========================
        # Edit mode
        # =========================
        if assessment_id:
            try:
                assessment = Assessments.objects.get(id=assessment_id)
            except Assessments.DoesNotExist:
                return HttpResponseNotFound("Assessment not found.")

            # Student permission
            if profile.role == "student" and assessment.student != profile:
                return HttpResponseForbidden("You cannot access this assessment.")

            # Clinician NOT assigned → read-only
            if clinician_is_readonly(profile, assessment):
                is_readonly = True

            context["assessment"] = assessment
            context["assessment_id"] = assessment_id

        # =========================
        # Field-level permissions
        # =========================
        context["student_readonly"] = profile.role == "student"
        context["is_readonly"] = is_readonly

        # =========================
        # Dropdown data
        # =========================
        context["students"] = Profile.objects.filter(role="student").order_by(
            "official_name"
        )
        context["clinicians"] = Profile.objects.filter(role="clinician").order_by(
            "official_name"
        )
        return render(request, self.template_name, context)


class AssessmentSection2FormView(View):
    template_name = "assessments/section2_form.html"

    def get(self, request):
        profile = request.user.profile
        assessment_id = request.GET.get("id")
        context = {}
        assessment = None
        is_readonly = False

        # =========================
        # Edit mode
        # =========================
        if assessment_id:
            try:
                assessment = Assessments.objects.get(id=assessment_id)
            except Assessments.DoesNotExist:
                return HttpResponseNotFound("Assessment not found.")

            # Student can only view their own
            if profile.role == "student" and assessment.student != profile:
                return HttpResponseForbidden("You cannot access this assessment.")

            context["assessment"] = assessment
            context["assessment_id"] = assessment_id

            if clinician_is_readonly(profile, assessment):
                is_readonly = True

        # =========================
        # Field-level permissions
        # =========================
        context["student_readonly"] = profile.role == "student"
        context["is_readonly"] = is_readonly

        # =========================
        # Dropdown data
        # =========================
        context["students"] = Profile.objects.filter(role="student").order_by(
            "official_name"
        )
        context["clinicians"] = Profile.objects.filter(role="clinician").order_by(
            "official_name"
        )

        return render(request, self.template_name, context)


class AssessmentTreatmentPlanFormView(View):
    template_name = "assessments/treatment_plan_form.html"

    def get(self, request):
        profile = request.user.profile
        assessment_id = request.GET.get("id")

        context = {}
        assessment = None
        is_readonly = False

        if assessment_id:
            try:
                assessment = Assessments.objects.get(id=assessment_id)
            except Assessments.DoesNotExist:
                return HttpResponseNotFound("Assessment not found.")

            # Student can only view their own
            if profile.role == "student" and assessment.student != profile:
                return HttpResponseForbidden("You cannot access this assessment.")

            # Clinician not assigned → readonly
            if clinician_is_readonly(profile, assessment):
                is_readonly = True

            context["assessment"] = assessment
            context["assessment_id"] = assessment_id

        # =========================
        # Field-level permissions
        # =========================
        context["student_readonly"] = profile.role == "student"
        context["is_readonly"] = is_readonly

        # =========================
        # Dropdown data
        # =========================
        context["students"] = Profile.objects.filter(role="student").order_by(
            "official_name"
        )
        context["clinicians"] = Profile.objects.filter(role="clinician").order_by(
            "official_name"
        )

        return render(request, self.template_name, context)
