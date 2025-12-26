from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Assessments
from .serializers import (
    AssessmentsListSerializer,
    AssessmentSection1DetailSerializer,
    AssessmentSection1CreateSerializer,
)


class AssessmentsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        role = profile.role

        if role == "student":
            queryset = Assessments.objects.filter(student=profile)

        elif role == "clinician":
            queryset = Assessments.objects.filter(evaluator=profile)

        elif role == "admin":
            queryset = Assessments.objects.all()

        else:
            queryset = Assessments.objects.none()

        queryset = queryset.select_related("student", "evaluator")

        serializer = AssessmentsListSerializer(queryset, many=True)
        return Response(serializer.data)


class AssessmentSection1APIView(APIView):
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

        if profile.role == "clinician" and assessment.evaluator != profile:
            return Response(
                {"detail": "You are not assigned to this assessment"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Admin can view all
        serializer = AssessmentSection1DetailSerializer(assessment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        POST method to create a new assessment (section 1).
        """
        profile = request.user.profile

        if profile.role not in ["student", "admin"]:
            return Response(
                {"detail": "You are not allowed to create assessments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AssessmentSection1CreateSerializer(
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

        elif profile.role == "admin":
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
        assessment = Assessments.objects.create(
            student=student,
            evaluator=evaluator,
            **data,
            # Student sign-off on creation
            is_student_signed=True,
            student_signed_by=student,
            student_signed_at=timezone.now(),
            # Clinician sign-offs reset
            is_section_1_signed=False,
            is_section_2_signed=False,
            is_section_3_signed=False,
        )

        return Response(
            {
                "id": assessment.id,
                "message": "Assessment created successfully",
            },
            status=status.HTTP_201_CREATED,
        )

    def put(self, request):
        """
        PUT method to update section 1.
        Resets all sign-offs (student and clinician).
        """
        profile = request.user.profile
        assessment_id = request.data.get("assessment_id")

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

        if profile.role not in ["student", "admin"]:
            return Response(
                {"detail": "Only student or admin can edit Section 1"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AssessmentSection1CreateSerializer(
            assessment,
            data=request.data,
            partial=False,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # -------------------------
        # Reset all sign-offs
        # -------------------------
        assessment.is_student_signed = False
        assessment.student_signed_by = None
        assessment.student_signed_at = None

        assessment.is_section_1_signed = False
        assessment.section_1_signed_by = None
        assessment.section_1_signed_at = None

        assessment.is_section_2_signed = False
        assessment.section_2_signed_by = None
        assessment.section_2_signed_at = None

        assessment.is_section_3_signed = False
        assessment.section_3_signed_by = None
        assessment.section_3_signed_at = None

        assessment.updated_at = timezone.now()
        assessment.save()

        return Response(
            {"message": "Section 1 updated. All sign-offs reset."},
            status=status.HTTP_200_OK,
        )
