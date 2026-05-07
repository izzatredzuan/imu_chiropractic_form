from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.views import View
from accounts.models import Profile
from .models import Assessments, Soaps, SoapModality, PatientReevaluation
from .utils import (
    clinician_is_readonly,
)


class AssessmentListView(View):
    template_name = "assessments/assessments.html"

    def get(self, request):
        profile = request.user.profile # Debugging line
        context = {
            "profile": profile
        }
        return render(request, self.template_name, context)


class BaseAssessmentFormView(View):
    template_name = None

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


class SoapFormView(View):
    template_name = "assessments/soap_form.html"

    def get_assessment(self, request, assessment_id):
        """
        Hook to get assessment. Can be overridden by child.
        """
        if assessment_id:
            assessment = get_object_or_404(Assessments, id=assessment_id)
        else:
            assessment = None
        return assessment
    
    def get(self, request, assessment_id=None, soap_id=None):
        profile = request.user.profile
        assessment = self.get_assessment(request, assessment_id)

        soap = None
        if soap_id:
            soap = get_object_or_404(Soaps, id=soap_id, assessment_id=assessment_id)

        is_readonly = False

        # =========================
        # Permission checks
        # =========================
        if soap:
            if assessment:
                # Student can only access their own
                if profile.role == "student" and soap.student != profile:
                    return HttpResponseForbidden("You cannot access this soap.")

                # Clinician not assigned → readonly
                is_readonly = clinician_is_readonly(profile, soap)
            else:
                # Optional hook for create logic
                is_readonly = self.get_create_readonly(profile)


        context = {
            "assessment": assessment,
            "assessment_id": assessment.id if assessment else None,
            "soap": soap,
            "student_readonly": profile.role == "student",
            "is_readonly": is_readonly,
            "students": Profile.objects.filter(role="student").order_by("official_name"),
            "clinicians": Profile.objects.filter(role="clinician").order_by("official_name"),
            "MODALITIES_CHOICES": SoapModality._meta.get_field("modality").choices,
        }

        return render(request, self.template_name, context)


class PatientReevaluationFormView(View):
    template_name = "assessments/patient_reevaluation_form.html"

    def get_assessment(self, request, assessment_id):
        """
        Hook to get assessment.
        Can be overridden by child.
        """
        if assessment_id:
            assessment = get_object_or_404(
                Assessments,
                id=assessment_id,
            )
        else:
            assessment = None

        return assessment

    def get(self, request, assessment_id=None, reevaluation_id=None):
        profile = request.user.profile
        assessment = self.get_assessment(
            request,
            assessment_id,
        )

        reevaluation = None

        if reevaluation_id:
            reevaluation = get_object_or_404(
                PatientReevaluation,
                id=reevaluation_id,
                assessment_id=assessment_id,
            )
        is_readonly = False

        # =========================
        # Permission checks
        # =========================
        if reevaluation:
            if assessment:
                # Student can only access their own
                if (
                    profile.role == "student"
                    and reevaluation.student != profile
                ):
                    return HttpResponseForbidden(
                        "You cannot access this reevaluation."
                    )

                # Clinician not assigned → readonly
                is_readonly = clinician_is_readonly(
                    profile,
                    reevaluation,
                )

            else:
                # Optional hook for create logic
                is_readonly = self.get_create_readonly(profile)

        context = {
            "assessment": assessment,
            "assessment_id": assessment.id if assessment else None,
            "reevaluation": reevaluation,
            "student_readonly": profile.role == "student",
            "is_readonly": is_readonly,
            "students": Profile.objects.filter(
                role="student"
            ).order_by("official_name"),
            "clinicians": Profile.objects.filter(
                role="clinician"
            ).order_by("official_name"),
        }

        return render(
            request,
            self.template_name,
            context,
        )