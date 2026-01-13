from rest_framework import serializers
from django.utils import timezone
from accounts.models import Profile
from .models import Assessments


class AssessmentsListSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    clinician = serializers.CharField(source="evaluator", read_only=True)
    updated_by = serializers.CharField(
        source="updated_by.official_name", read_only=True
    )
    created_by = serializers.CharField(
        source="created_by.official_name", read_only=True
    )

    class Meta:
        model = Assessments
        fields = [
            "id",
            "patient_name",
            "student",
            "clinician",
            "is_section_1_signed",
            "is_section_2_signed",
            "is_section_3_signed",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        ]


# serializers.py
class AssessmentSection1And2DetailSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    evaluator = serializers.StringRelatedField()

    class Meta:
        model = Assessments
        fields = [
            "id",
            # Assignment
            "student",
            "evaluator",
            # Section 1 – Initial Assessment
            "patient_name",
            "gender",
            "date_of_birth",
            "pulse",
            "respiratory",
            "systolic_bp",
            "diastolic_bp",
            "summary",
            "special_direction",
            # Presenting Complaint
            "chief_complaint",
            "history_of_condition",
            "pain",
            "aggravating_factors",
            "relieving_factors",
            "associated_symptoms",
            "health_hx_review",
            "past_illnesses",
            "family_hx",
            "psycho_social_hx",
            "occupational",
            "diet",
            "system_review",
            "is_section_1_signed",
            "is_section_2_signed",
            "created_at",
            "updated_at",
        ]


class AssessmentSection1And2CreateSerializer(serializers.ModelSerializer):
    evaluator = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.filter(role="clinician"), required=True
    )

    student = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.filter(role="student"),
        required=False,  # optional for student users
    )

    class Meta:
        model = Assessments
        fields = [
            "student",
            "evaluator",
            # Section 1 – Initial Assessment
            "patient_name",
            "gender",
            "date_of_birth",
            "pulse",
            "respiratory",
            "systolic_bp",
            "diastolic_bp",
            "summary",
            "special_direction",
            # Section 2 – Presenting Complaint
            "chief_complaint",
            "history_of_condition",
            "pain",
            "aggravating_factors",
            "relieving_factors",
            "associated_symptoms",
            "health_hx_review",
            "past_illnesses",
            "family_hx",
            "psycho_social_hx",
            "occupational",
            "diet",
            "system_review",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        user_profile = request.user.profile

        # If user is a student, override student field
        if user_profile.role == "student":
            validated_data["student"] = user_profile

        # If user is admin, must select student manually
        elif user_profile.role == "admin":
            student = validated_data.get("student")
            if not student:
                raise serializers.ValidationError(
                    {"student": "This field is required for admins."}
                )
            
        # -----------------------------
        # Audit fields (CREATE)
        # -----------------------------
        validated_data["created_by"] = user_profile
        validated_data["updated_by"] = user_profile

        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context["request"]
        user_profile = request.user.profile

        # -----------------------------
        # Audit field (UPDATE)
        # -----------------------------
        instance.updated_by = user_profile

        return super().update(instance, validated_data)