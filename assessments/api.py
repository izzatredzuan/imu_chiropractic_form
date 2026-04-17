import logging
import base64
import uuid
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from accounts.models import Profile
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Assessments, SoapModality, Soaps
from .serializers import (
    AssessmentsListSerializer,
    AssessmentSection1And2CreateSerializer,
    AssessmentSection3Serializer,
    AssessmentSection4Serializer,
    AssessmentTreatmentPlanSerializer,
    SoapSerializer,
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
            f"VIEW - Section 1 | assessment_id={assessment.id}, "
            f"user={profile.official_name} ({profile.role})"
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
                logger.info(
                    f"SAVE - Section 1 | "
                    f"assessment_id={assessment.id}, "
                    f"user={profile.official_name} ({profile.role}) | "
                    f"Reset section 1 sign-offs"
                )

            # ---------- SAVE SECTION 2 ----------
            elif action == "save_section_2":
                assessment.is_section_2_signed = False
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
                    "Section 1 sign-offs have been reset."
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


class AssessmentSection3APIView(APIView):
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

        if profile.role == "student" and assessment.student != profile:
            return Response(
                {"detail": "You cannot view this section"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AssessmentSection3Serializer(assessment)
        logger.info(
            f"VIEW - Section 3 | assessment_id={assessment.id}, "
            f"user={profile.official_name} ({profile.role})"
        )

        return Response(serializer.data)

    # =========================
    # PUT
    # =========================
    def put(self, request):
        profile = request.user.profile
        assessment_id = request.data.get("assessment_id")
        action = request.data.get("action", "save_section_3")

        if not assessment_id:
            return Response(
                {"assessment_id": "Assessment ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assessment = get_object_or_404(Assessments, id=assessment_id)

        if profile.role == "student" and assessment.student != profile:
            return Response(
                {"detail": "You cannot edit this section"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AssessmentSection3Serializer(
            assessment,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        # =========================
        # ROM DRAWING HANDLING
        # =========================
        rom_drawing_data = request.data.get("rom_drawing_data")

        try:
            if rom_drawing_data:
                format, imgstr = rom_drawing_data.split(";base64,")
                ext = format.split("/")[-1]

                # delete old file
                if assessment.rom_drawing:
                    assessment.rom_drawing.delete(save=False)

                    logger.info(
                        f"ROM_DRAWING_DELETED - assessment_id={assessment.id}, "
                        f"user={profile.official_name} ({profile.role})"
                    )

                rom_file = ContentFile(
                    base64.b64decode(imgstr),
                    name=f"rom_drawing_{assessment.id}_{uuid.uuid4().hex}.{ext}",
                )

                serializer.save(rom_drawing=rom_file)

                logger.info(
                    f"ROM_DRAWING_UPDATED - assessment_id={assessment.id}, "
                    f"user={profile.official_name} ({profile.role})"
                )
            else:
                serializer.save()

        except Exception as e:
            logger.error(
                f"ROM_DRAWING_ERROR - assessment_id={assessment.id}, "
                f"user={profile.official_name} ({profile.role}), "
                f"error={str(e)}",
                exc_info=True,
            )

            return Response(
                {"rom_drawing_data": f"Invalid image data: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # refresh instance after save
        assessment.refresh_from_db()

        # =========================
        # ACTION LOGIC (SIGN-OFF)
        # =========================
        print(action)
        try:
            if action == "save_section_3":
                print("trying to save_section_3")
                assessment.is_section_3_signed = False

                logger.info(
                    f"SAVE_SECTION_3 - assessment_id={assessment.id}, "
                    f"user={profile.official_name} ({profile.role})"
                )

            elif action == "sign_off_section_3":
                print("trying to sign_off_section_3")
                if profile.role not in ["clinician", "admin"]:
                    logger.warning(
                        f"SIGN_OFF_DENIED - Section 3 | "
                        f"assessment_id={assessment.id}, user={profile.official_name} ({profile.role})"
                    )
                    return Response(
                        {"detail": "Not allowed to sign off"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                assessment.is_section_3_signed = True
                assessment.section_3_signed_by = profile
                assessment.section_3_signed_at = timezone.now()

                logger.info(
                    f"SIGN_OFF_SECTION_3 - assessment_id={assessment.id}, "
                    f"student={assessment.student.official_name}, "
                    f"signed_by={profile.official_name} ({profile.role})"
                )

            assessment.save()

            # =========================
            # RESPONSE
            # =========================
            message = "Section 3 updated successfully"

            if action == "sign_off_section_3":
                message = "Section 3 signed off successfully"

            logger.info(
                f"UPDATE_SUCCESS - Section 3 | assessment_id={assessment.id}, "
                f"action={action}, user={profile.official_name} ({profile.role})"
            )

            return Response(
                {"message": message},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(
                f"UPDATE_FAILED - Section 3 | assessment_id={assessment.id}, "
                f"user={profile.official_name}, error={str(e)}",
                exc_info=True,
            )

            return Response(
                {"detail": "Failed to update Section 3", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AssessmentSection4APIView(APIView):
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

        if profile.role == "student" and assessment.student != profile:
            return Response(
                {"detail": "You cannot view this section"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AssessmentSection4Serializer(assessment)
        logger.info(
            f"VIEW - Section 4 | assessment_id={assessment.id}, "
            f"user={profile.official_name} ({profile.role})"
        )

        return Response(serializer.data)

    # =========================
    # PUT
    # =========================
    def put(self, request):

        profile = request.user.profile
        assessment_id = request.data.get("assessment_id")
        action = request.data.get("action", "save_section_4")

        if not assessment_id:
            return Response(
                {"assessment_id": "Assessment ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assessment = get_object_or_404(Assessments, id=assessment_id)

        if profile.role == "student" and assessment.student != profile:
            return Response(
                {"detail": "You cannot edit this section"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AssessmentSection4Serializer(
            assessment,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # =========================
        # ACTION LOGIC
        # =========================
        if action == "save_section_4":
            assessment.is_section_4_signed = False

        elif action == "sign_off_section_4":
            if profile.role not in ["clinician", "admin"]:
                logger.warning(
                    f"SIGN_OFF_DENIED - Section 4 | "
                    f"assessment_id={assessment.id}, user={profile.official_name} ({profile.role})"
                )
                return Response(
                    {"detail": "Not allowed to sign off"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            assessment.is_section_4_signed = True
            assessment.section_4_signed_by = profile
            assessment.section_4_signed_at = timezone.now()

        assessment.save()
        logger.info(
            f"UPDATE - Section 4 | assessment_id={assessment.id}, "
            f"student={assessment.student.official_name}, "
            f"updated_by={profile.official_name} ({profile.role}), "
            f"action={action}"
        )

        return Response(
            {"message": "Section 4 updated successfully"},
            status=status.HTTP_200_OK,
        )


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


class SoapAPIView(APIView):
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

        # permission
        if profile.role == "student" and assessment.student != profile:
            return Response(
                {"detail": "You cannot view SOAPs for this assessment"},
                status=status.HTTP_403_FORBIDDEN,
            )

        soaps = Soaps.objects.filter(assessment=assessment).prefetch_related(
            "soap_modalities"
        )

        serializer = SoapSerializer(soaps, many=True)

        logger.info(
            f"VIEW - SOAP | "
            f"assessment_id={assessment.id}, "
            f"user={profile.official_name} ({profile.role}), "
            f"count={soaps.count()}"
        )
        return Response(serializer.data)

    # =========================
    # POST
    # =========================
    def post(self, request):
        profile = request.user.profile
        action = request.data.get("action", "save")

        serializer = SoapSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        assessment = validated_data["assessment"]

        # -----------------------------
        # Permission check
        # -----------------------------
        if profile.role == "student":
            if assessment.student != profile:
                return Response(
                    {"detail": "You cannot create SOAP for this assessment"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            # auto assign student
            validated_data["student"] = profile

        elif profile.role in ["admin", "clinician"]:
            if not validated_data.get("student"):
                return Response(
                    {"student": "This field is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        modalities = request.data.get("soap_modalities", [])

        try:
            # -------------------------------
            # Create SOAP
            # -------------------------------
            soap = serializer.save(
                student=validated_data.get("student"),
                evaluator=validated_data.get("evaluator"),
                created_by=profile,
                updated_by=profile,
            )

            # -------------------------------
            # Create Modalities
            # -------------------------------
            for modality in modalities:
                SoapModality.objects.create(soap=soap, **modality)

            # ---------- CREATE LOG ----------
            logger.info(
                f"CREATE - SOAP | "
                f"soap_id={soap.id}, "
                f"student={soap.student.official_name if soap.student else None}, "
                f"evaluator={soap.evaluator.official_name if soap.evaluator else None}, "
                f"assessment_id={soap.assessment.id}, "
                f"created_by={soap.created_by.official_name}, "
                f"created_at={soap.created_at}"
            )

            # -------------------------------
            # SIGN OFF
            # -------------------------------
            if action == "sign_off":
                if profile.role not in ["clinician", "admin"]:
                    return Response(
                        {"detail": "Not allowed to sign SOAP"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                soap.is_soap_signed = True
                soap.soap_signed_by = profile
                soap.soap_signed_at = timezone.now()
                soap.save()

                logger.info(
                    f"SIGN_OFF - SOAP | "
                    f"soap_id={soap.id}, "
                    f"student={soap.student.official_name if soap.student else None}, "
                    f"assessment_id={soap.assessment.id}, "
                    f"signed_by={profile.official_name}, "
                    f"signed_at={soap.soap_signed_at}"
                )

            return Response(
                {"id": soap.id, "message": "S.O.A.P. created successfully"},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(
                f"CREATE_FAILED - SOAP | assessment_id={assessment.id}, "
                f"user={profile.official_name}, error={str(e)}",
                exc_info=True,
            )
            return Response(
                {"detail": "Failed to create SOAP", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # =========================
    # PUT
    # =========================
    def put(self, request):
        profile = request.user.profile
        soap_id = request.data.get("soap_id")
        action = request.data.get("action", "save")

        if not soap_id:
            return Response(
                {"soap_id": "SOAP ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        soap = get_object_or_404(Soaps, id=soap_id)

        # -----------------------------
        # Permission check
        # -----------------------------
        if profile.role == "student" and soap.assessment.student != profile:
            return Response(
                {"detail": "You cannot edit this SOAP"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SoapSerializer(
            soap,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        # -----------------------------
        # Prevent student tampering
        # -----------------------------
        if profile.role == "student":
            validated_data["student"] = profile

        elif profile.role in ["admin", "clinician"]:
            # Optional: enforce student presence if updating it
            if "student" in validated_data and not validated_data.get("student"):
                return Response(
                    {"student": "This field cannot be null"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            # -----------------------------
            # Save SOAP
            # -----------------------------
            soap = serializer.save(
                student=validated_data.get("student", soap.student),
                evaluator=validated_data.get("evaluator", soap.evaluator),
                updated_by=profile,
            )

            logger.info(
                f"UPDATE - SOAP | "
                f"soap_id={soap.id}, "
                f"student={soap.student.official_name if soap.student else None}, "
                f"evaluator={soap.evaluator.official_name if soap.evaluator else None}, "
                f"assessment_id={soap.assessment.id}, "
                f"updated_by={profile.official_name}, "
                f"updated_at={soap.updated_at}"
            )

            # -----------------------------
            # Update Modalities
            # -----------------------------
            modalities = request.data.get("soap_modalities", None)

            if modalities is not None:
                soap.soap_modalities.all().delete()

                for modality in modalities:
                    SoapModality.objects.create(soap=soap, **modality)

            # =========================
            # ACTION LOGIC
            # =========================

            # ---------- SAVE ----------
            if action == "save":
                soap.is_soap_signed = False
                soap.soap_signed_by = None
                soap.soap_signed_at = None

                logger.info(
                    f"SAVE - SOAP | "
                    f"soap_id={soap.id}, "
                    f"student={soap.student.official_name if soap.student else None}, "
                    f"evaluator={soap.evaluator.official_name if soap.evaluator else None}, "
                    f"assessment_id={soap.assessment.id}, "
                    f"updated_by={profile.official_name}, "
                    f"updated_at={soap.updated_at} | "
                    f"Sign-off reset"
                )

            # ---------- SIGN OFF ----------
            elif action == "sign_off":
                if profile.role not in ["clinician", "admin"]:
                    logger.warning(
                        f"SIGN_OFF_DENIED - SOAP | "
                        f"soap_id={soap.id}, "
                        f"user={profile.official_name} ({profile.role})"
                    )
                    return Response(
                        {"detail": "Not allowed to sign SOAP"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                soap.is_soap_signed = True
                soap.soap_signed_by = profile
                soap.soap_signed_at = timezone.now()

                logger.info(
                    f"SIGN_OFF - SOAP | "
                    f"soap_id={soap.id}, "
                    f"student={soap.student.official_name if soap.student else None}, "
                    f"evaluator={soap.evaluator.official_name if soap.evaluator else None}, "
                    f"assessment_id={soap.assessment.id}, "
                    f"signed_by={profile.official_name}, "
                    f"signed_at={soap.soap_signed_at}"
                )
            soap.save()

            # =========================
            # RESPONSE MESSAGE
            # =========================
            message = "SOAP updated successfully"

            if action == "sign_off":
                message = "SOAP signed off successfully"

            elif action == "save":
                message = "SOAP updated successfully. Sign-off has been reset."

            logger.info(
                f"RESPONSE - SOAP | "
                f"soap_id={soap.id}, "
                f"action={action}, "
                f"message='{message}'"
            )
            return Response(
                {"message": message},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(
                f"UPDATE_FAILED - SOAP | soap_id={soap.id}, "
                f"user={profile.official_name}, error={str(e)}",
                exc_info=True,
            )
            return Response(
                {"detail": "Failed to update SOAP", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )