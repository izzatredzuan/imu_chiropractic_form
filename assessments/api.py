import logging
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
    AssessmentSection1And2DetailSerializer,
    AssessmentSection1And2CreateSerializer,
)

logger = logging.getLogger("assessments")


class AssessmentsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        role = profile.role

        if role == "student":
            queryset = Assessments.objects.filter(student=profile)

        elif role == "admin" or role == "clinician":
            queryset = Assessments.objects.all()

        else:
            queryset = Assessments.objects.none()

        queryset = queryset.select_related("student", "evaluator")

        serializer = AssessmentsListSerializer(queryset, many=True)
        return Response(serializer.data)


class AssessmentSection1And2APIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, assessment_id=None):
        """
        GET method to fetch section 1 data for editing or viewing.
        """
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

        # Admin can view all
        serializer = AssessmentSection1And2DetailSerializer(assessment)
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
        data = serializer.validated_data.copy()

        # --------------------------------
        # Extract controlled fields
        # --------------------------------
        evaluator = data.pop("evaluator", None)
        student_from_payload = data.pop("student", None)

        # --------------------------------
        # Role-based assignment
        # --------------------------------
        if profile.role == "student":
            student = profile
            if not evaluator:
                return Response(
                    {"evaluator": "Evaluator is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        elif profile.role == "admin" or profile.role == "clinician":
            student = student_from_payload
            if not student:
                return Response(
                    {"student": "Student is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not evaluator:
                return Response(
                    {"evaluator": "Evaluator is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"detail": "You are not allowed to create assessments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------
        # Create assessment
        # --------------------------------
        try:
            # Use serializer to create to ensure audit fields are set
            assessment = serializer.save(
                student=student,
                evaluator=evaluator,
                is_section_1_signed=False,
                is_section_2_signed=False,
                is_section_3_signed=False,
            )
            logger.info(
                f"CREATE - Assessment created successfully: "
                f"id={assessment.id}, patient name={assessment.patient_name}, student={student.member_id} - {student.official_name}, "
                f"evaluator={evaluator.member_id} - {evaluator.official_name},"
                f"created_by={request.user.username} - {request.user.profile.official_name})"
            )
            return Response(
                {
                    "id": assessment.id,
                    "message": "Assessment created successfully",
                },
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
            assessment,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # =========================
            # SECTION SIGN-OFF LOGIC
            # =========================

            # ---------- SAVE SECTION 1 ----------
            if action == "save_section_1":
                logger.info(
                    f"SAVE - Section 1 | "
                    f"assessment_id={assessment.id}, "
                    f"user={profile.official_name} ({profile.role}) | "
                    f"Resetting Section 1 & Section 2 sign-offs"
                )

                assessment.is_section_1_signed = False
                assessment.section_1_signed_by = None
                assessment.section_1_signed_at = None

                assessment.is_section_2_signed = False
                assessment.section_2_signed_by = None
                assessment.section_2_signed_at = None

            # ---------- SAVE SECTION 2 ----------
            elif action == "save_section_2":
                logger.info(
                    f"SAVE - Section 2 | "
                    f"assessment_id={assessment.id}, "
                    f"user={profile.official_name} ({profile.role}) | "
                    f"Resetting Section 2 sign-off"
                )

                assessment.is_section_2_signed = False
                assessment.section_2_signed_by = None
                assessment.section_2_signed_at = None

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
            raise
