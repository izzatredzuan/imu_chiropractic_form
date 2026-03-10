from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import (
    get_object_or_404,
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


class BaseAssessmentFormView(View):
    template_name = None  # child must define this

    def get_assessment(self, request, assessment_id):
        """
        Hook to get assessment. Can be overridden by child.
        """
        if assessment_id:
            assessment = get_object_or_404(Assessments, id=assessment_id)
        else:
            assessment = None
        return assessment

    def get(self, request, assessment_id=None):
        profile = request.user.profile
        assessment = self.get_assessment(request, assessment_id)

        is_readonly = False

        # =========================
        # Permission checks
        # =========================
        if assessment:
            # Student can only access their own
            if profile.role == "student" and assessment.student != profile:
                return HttpResponseForbidden("You cannot access this assessment.")

            # Clinician not assigned → readonly
            is_readonly = clinician_is_readonly(profile, assessment)
        else:
            # Optional hook for create logic
            is_readonly = self.get_create_readonly(profile)

        # =========================
        # Context
        # =========================
        context = {
            "assessment": assessment,
            "assessment_id": assessment.id if assessment else None,
            "student_readonly": profile.role == "student",
            "is_readonly": is_readonly,
            "students": Profile.objects.filter(role="student").order_by(
                "official_name"
            ),
            "clinicians": Profile.objects.filter(role="clinician").order_by(
                "official_name"
            ),
        }

        return render(request, self.template_name, context)

    def get_create_readonly(self, profile):
        """
        Hook to decide readonly when creating a new assessment.
        Default: True (cannot create)
        Child classes can override.
        """
        return True


class AssessmentSection1FormView(BaseAssessmentFormView):
    template_name = "assessments/section1_form.html"

    def get_create_readonly(self, profile):
        """
        Allow students to create a new Section 1 assessment for themselves.
        """
        return False


class AssessmentSection2FormView(BaseAssessmentFormView):
    template_name = "assessments/section2_form.html"


class AssessmentSection3FormView(BaseAssessmentFormView):
    template_name = "assessments/section3_form.html"


class AssessmentSection4FormView(BaseAssessmentFormView):
    template_name = "assessments/section4_form.html"


class AssessmentTreatmentPlanFormView(BaseAssessmentFormView):
    template_name = "assessments/treatment_plan_form.html"
