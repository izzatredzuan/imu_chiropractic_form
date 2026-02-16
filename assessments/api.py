import logging
import base64
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from accounts.models import Profile
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Assessments
from .serializers import (
    AssessmentsListSerializer,
    AssessmentSection1And2CreateSerializer,
    AssessmentTreatmentPlanSerializer,
)

logger = logging.getLogger("assessments")


class AssessmentsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        role = profile.role

        scope = request.GET.get("scope", "all")  # all | assigned
        if role == "student":
            queryset = Assessments.objects.filter(student=profile)

        elif role == "admin":
            queryset = Assessments.objects.all()

        elif role == "clinician":
            if scope == "assigned":
                queryset = Assessments.objects.filter(evaluator=profile)
            else:
                queryset = Assessments.objects.all()

        else:
            queryset = Assessments.objects.none()

        queryset = queryset.select_related("student", "evaluator").order_by(
            "-updated_at"
        )

        serializer = AssessmentsListSerializer(queryset, many=True)
        return Response(serializer.data)


class AssessmentSection1And2APIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, assessment_id=None):
        profile = request.user.profile
        if not assessment_id:
            return Response(
                {"assessment_id": "Assessment ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assessment = get_object_or_404(Assessments, id=assessment_id)

        # -----------------------------
        # Permission rules
        # -----------------------------
        if profile.role == "student" and assessment.student != profile:
            return Response(
                {"detail": "You cannot view this assessment"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AssessmentSection1And2CreateSerializer(assessment)
        logger.info(
            f"VIEW - Assessment {assessment.id} accessed by {profile.official_name} ({profile.role})"
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        POST method to create a new assessment (section 1).
        """
        profile = request.user.profile
        if profile.role not in ["student", "admin", "clinician"]:
            return Response(
                {"detail": "You are not allowed to create assessments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        logger.info(
            f"CREATE - Attempt by user={request.user.username} - {profile.official_name}, role={profile.role}, "
            f"patient name={request.data.get('patient_name', 'N/A')}"
        )

        serializer = AssessmentSection1And2CreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        signature_data = request.data.get("signature_data")
        if signature_data:
            try:
                format, imgstr = signature_data.split(";base64,")
                ext = format.split("/")[-1]
                signature_file = ContentFile(
                    base64.b64decode(imgstr), name=f"signature.{ext}"
                )
                serializer.validated_data["initial_patient_consent_signature"] = (
                    signature_file
                )
            except Exception as e:
                logger.error(f"SIGNATURE_ERROR - Invalid signature data: {str(e)}")
                return Response(
                    {"signature_data": f"Invalid image data: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # --------------------------------
        # Create assessment
        # --------------------------------
        try:
            assessment = serializer.save()
            logger.info(
                f"CREATE - Assessment created successfully: "
                f"id={assessment.id}, "
                f"patient name={assessment.patient_name}, "
                f"student={assessment.student.member_id} - {assessment.student.official_name}, "
                f"evaluator={assessment.evaluator.member_id} - {assessment.evaluator.official_name}, "
                f"created_by={request.user.username} - {request.user.profile.official_name}"
            )

            if signature_data:
                logger.info(
                    f"SIGNATURE_SAVED - Initial patient consent signature saved for assessment {assessment.id}"
                )

            return Response(
                {"id": assessment.id, "message": "Assessment created successfully"},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            logger.error(
                f"CREATE - Failed to create assessment: patient name={assessment.patient_name}"
                f"created_by={request.user.username} - {request.user.profile.official_name}, "
                f"error={str(e)}"
            )
            return Response(
                {"detail": "Failed to create assessment", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request):
        profile = request.user.profile
        assessment_id = request.data.get("assessment_id")
        action = request.data.get("action", "save")

        if not assessment_id:
            return Response(
                {"assessment_id": "Assessment ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assessment = get_object_or_404(Assessments, id=assessment_id)

        # -------------------------
        # Permission check
        # -------------------------
        if profile.role == "student" and assessment.student != profile:
            return Response(
                {"detail": "You cannot edit this assessment"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AssessmentSection1And2CreateSerializer(
            assessment, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        signature_data = request.data.get("signature_data")
        try:
            if signature_data:
                format, imgstr = signature_data.split(";base64,")
                ext = format.split("/")[-1]
                signature_file = ContentFile(
                    base64.b64decode(imgstr), name=f"signature.{ext}"
                )
                serializer.save(initial_patient_consent_signature=signature_file)
                logger.info(
                    f"SIGNATURE_UPDATED - Signature updated for assessment {assessment.id} by {profile.official_name}"
                )
            else:
                serializer.save()
        except Exception as e:
            logger.error(
                f"SIGNATURE_SAVE_FAILED - Assessment {assessment.id} | Error: {str(e)}",
                exc_info=True,
            )
            return Response(
                {"detail": "Failed to save signature", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ===== Section sign-off logic =====
        # ---------- SAVE SECTION 1 ----------
        try:
            if action == "save_section_1":
                assessment.is_section_1_signed = False
                assessment.section_1_signed_by = None
                assessment.section_1_signed_at = None
                assessment.is_section_2_signed = False
                assessment.section_2_signed_by = None
                assessment.section_2_signed_at = None
                logger.info(
                    f"SAVE - Section 1 | "
                    f"assessment_id={assessment.id}, "
                    f"user={profile.official_name} ({profile.role}) | "
                    f"Reset section 1 & 2 sign-offs"
                )

            # ---------- SAVE SECTION 2 ----------
            elif action == "save_section_2":
                assessment.is_section_2_signed = False
                assessment.section_2_signed_by = None
                assessment.section_2_signed_at = None
                logger.info(
                    f"SAVE - Section 2 | "
                    f"assessment_id={assessment.id}, "
                    f"user={profile.official_name} ({profile.role}) | "
                    f"Resetting Section 2 sign-off"
                )

            # ---------- SIGN OFF SECTION 1 ----------
            elif action == "sign_off_section_1":
                if profile.role not in ["clinician", "admin"]:
                    logger.warning(
                        f"SIGN_OFF_DENIED - Section 1 | "
                        f"assessment_id={assessment.id}, "
                        f"user={profile.official_name} ({profile.role})"
                    )
                    return Response(
                        {"detail": "Not allowed to sign off Section 1"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                assessment.is_section_1_signed = True
                assessment.section_1_signed_by = profile
                assessment.section_1_signed_at = timezone.now()
                logger.info(
                    f"SIGN_OFF - Section 1 | "
                    f"assessment_id={assessment.id}, "
                    f"student={assessment.student.official_name}, "
                    f"signed_by={profile.official_name} ({profile.role})"
                )

            # ---------- SIGN OFF SECTION 2 ----------
            elif action == "sign_off_section_2":
                if profile.role not in ["clinician", "admin"]:
                    logger.warning(
                        f"SIGN_OFF_DENIED - Section 2 | "
                        f"assessment_id={assessment.id}, "
                        f"user={profile.official_name} ({profile.role})"
                    )
                    return Response(
                        {"detail": "Not allowed to sign off Section 2"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                if not assessment.is_section_1_signed:
                    logger.warning(
                        f"SIGN_OFF_BLOCKED - Section 2 | "
                        f"assessment_id={assessment.id}, "
                        f"user={profile.official_name} | "
                        f"reason=Section 1 not signed"
                    )
                    return Response(
                        {"detail": "Section 1 must be signed before Section 2"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                assessment.is_section_2_signed = True
                assessment.section_2_signed_by = profile
                assessment.section_2_signed_at = timezone.now()
                logger.info(
                    f"SIGN_OFF - Section 2 | "
                    f"assessment_id={assessment.id}, "
                    f"student={assessment.student.official_name}, "
                    f"signed_by={profile.official_name} ({profile.role})"
                )

            assessment.save()
            logger.info(
                f"UPDATE - Section 1 | "
                f"assessment_id={assessment.id}, "
                f"student={assessment.student.official_name}, "
                f"updated_by={profile.official_name} ({profile.role}), "
                f"action={action}"
            )

            # =========================
            # RESPONSE MESSAGEs
            # =========================
            message = "Assessment updated successfully"

            if action == "sign_off_section_1":
                message = "Section 1 signed off successfully"

            elif action == "sign_off_section_2":
                message = "Section 2 signed off successfully"

            elif action == "save_section_1":
                message = (
                    "Section 1 updated successfully. "
                    "Section 1 and Section 2 sign-offs have been reset."
                )

            elif action == "save_section_2":
                message = (
                    "Section 2 updated successfully. "
                    "Section 2 sign-off has been reset."
                )

            logger.info(
                f"RESPONSE - Assessment | "
                f"assessment_id={assessment.id}, "
                f"action={action}, "
                f"message='{message}'"
            )
            return Response(
                {"message": message},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(
                f"UPDATE_FAILED - Section 1 | "
                f"assessment_id={assessment_id}, "
                f"user={profile.official_name}, "
                f"error={str(e)}",
                exc_info=True,
            )
            return Response(
                {"detail": "Failed to update assessment", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# api.py


class AssessmentTreatmentPlanAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # =========================
    # GET
    # =========================
    def get(self, request):
        profile = request.user.profile
        assessment_id = request.query_params.get("assessment_id")

        if not assessment_id:
            return Response(
                {"assessment_id": "Assessment ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assessment = get_object_or_404(Assessments, id=assessment_id)

        # Permission check
        if profile.role == "student" and assessment.student != profile:
            return Response(
                {"detail": "You cannot view this treatment plan"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AssessmentTreatmentPlanSerializer(assessment)

        logger.info(
            f"VIEW - Treatment Plan | "
            f"assessment_id={assessment.id}, "
            f"user={profile.official_name} ({profile.role})"
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    # =========================
    # PUT
    # =========================
    def put(self, request):
        profile = request.user.profile
        assessment_id = request.data.get("assessment_id")
        action = request.data.get("action", "save_treatment_plan")

        if not assessment_id:
            return Response(
                {"assessment_id": "Assessment ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assessment = get_object_or_404(Assessments, id=assessment_id)

        # Permission check
        if profile.role == "student" and assessment.student != profile:
            return Response(
                {"detail": "You cannot edit this treatment plan"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AssessmentTreatmentPlanSerializer(
            assessment,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()

            # =========================
            # ACTION LOGIC
            # =========================

            # ---------- SAVE ----------
            if action == "save_treatment_plan":
                assessment.is_treatment_plan_signed = False
                assessment.treatment_plan_signed_by = None
                assessment.treatment_plan_signed_at = None

                logger.info(
                    f"SAVE - Treatment Plan | "
                    f"assessment_id={assessment.id}, "
                    f"user={profile.official_name} ({profile.role}) | "
                    f"Sign-off reset"
                )

            # ---------- SIGN OFF ----------
            elif action == "sign_off_treatment_plan":

                if profile.role not in ["clinician", "admin"]:
                    logger.warning(
                        f"SIGN_OFF_DENIED - Treatment Plan | "
                        f"assessment_id={assessment.id}, "
                        f"user={profile.official_name} ({profile.role})"
                    )
                    return Response(
                        {"detail": "Not allowed to sign off Treatment Plan"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                assessment.is_treatment_plan_signed = True
                assessment.treatment_plan_signed_by = profile
                assessment.treatment_plan_signed_at = timezone.now()

                logger.info(
                    f"SIGN_OFF - Treatment Plan | "
                    f"assessment_id={assessment.id}, "
                    f"signed_by={profile.official_name} ({profile.role})"
                )

            assessment.save()

            # =========================
            # RESPONSE MESSAGE
            # =========================
            message = "Treatment Plan updated successfully"

            if action == "save_treatment_plan":
                message = (
                    "Treatment Plan updated successfully. " "Sign-off has been reset."
                )

            elif action == "sign_off_treatment_plan":
                message = "Treatment Plan signed off successfully"

            logger.info(
                f"RESPONSE - Treatment Plan | "
                f"assessment_id={assessment.id}, "
                f"action={action}, "
                f"message='{message}'"
            )

            return Response(
                {"message": message},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(
                f"UPDATE_FAILED - Treatment Plan | "
                f"assessment_id={assessment_id}, "
                f"user={profile.official_name}, "
                f"error={str(e)}",
                exc_info=True,
            )

            return Response(
                {"detail": "Failed to update treatment plan", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
