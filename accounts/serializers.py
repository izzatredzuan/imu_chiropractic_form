from . import choices
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Profile

PROFILE_FIELDS = [
    "member_id",
    "official_name",
    "role",
    "is_admin",
    # Shared
    "nricpsprt",
    "gender",
    "phone",
    "emergency_contact",
    "personal_email",
    "address_1",
    "address_2",
    "address_3",
    "address_4",
    "postal_code",
    "city",
    "state",
    "country",
    "location",
    "position",
    # Student
    "cohort_code",
    "program_description",
    "transcript_description",
    "advisor_name",
    "advisor_email",
    # Clinician
    "department_code",
    "business_unit",
]


# -----------------------------
# CREATE Serializer
# -----------------------------
class UserProfileCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    # ONLY User fields here
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
        ]

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        request_data = self.initial_data  # full incoming payload

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
        )

        profile_data = {}

        # manually pull profile fields from request data
        for field in PROFILE_FIELDS:
            if field in request_data:
                profile_data[field] = request_data[field]

        Profile.objects.update_or_create(user=user, defaults=profile_data)

        return user


# -----------------------------
# UPDATE Serializer
# -----------------------------
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
        ]

    def validate_password(self, value):
        if value:
            try:
                validate_password(value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.messages)
        return value

    def update(self, instance, validated_data):
        request_data = self.initial_data

        # --------------------
        # Update User fields
        # --------------------
        if "username" in validated_data:
            instance.username = validated_data["username"]

        if "email" in validated_data:
            instance.email = validated_data["email"]

        if "password" in validated_data:
            instance.set_password(validated_data["password"])

        instance.save()

        # --------------------
        # Update Profile fields
        # --------------------
        profile = instance.profile

        for field in PROFILE_FIELDS:
            if field in request_data:
                setattr(profile, field, request_data[field])

        profile.save()

        return instance


# -----------------------------
# READ Serializer
# -----------------------------
class UserProfileReadSerializer(serializers.ModelSerializer):
    member_id = serializers.CharField(source="profile.member_id")
    official_name = serializers.CharField(source="profile.official_name")
    role = serializers.CharField(source="profile.role")
    is_admin = serializers.BooleanField(source="profile.is_admin")

    nricpsprt = serializers.CharField(source="profile.nricpsprt", allow_null=True)
    gender = serializers.CharField(source="profile.gender")
    phone = serializers.CharField(source="profile.phone", allow_null=True)
    emergency_contact = serializers.CharField(
        source="profile.emergency_contact", allow_null=True
    )
    personal_email = serializers.EmailField(
        source="profile.personal_email", allow_null=True
    )
    address_1 = serializers.CharField(source="profile.address_1", allow_null=True)
    address_2 = serializers.CharField(source="profile.address_2", allow_null=True)
    address_3 = serializers.CharField(source="profile.address_3", allow_null=True)
    address_4 = serializers.CharField(source="profile.address_4", allow_null=True)
    postal_code = serializers.CharField(source="profile.postal_code", allow_null=True)
    city = serializers.CharField(source="profile.city", allow_null=True)
    state = serializers.CharField(source="profile.state", allow_null=True)
    country = serializers.CharField(source="profile.country", allow_null=True)
    location = serializers.CharField(source="profile.location", allow_null=True)
    position = serializers.CharField(source="profile.position", allow_null=True)
    cohort_code = serializers.CharField(source="profile.cohort_code", allow_null=True)
    program_description = serializers.CharField(
        source="profile.program_description", allow_null=True
    )
    transcript_description = serializers.CharField(
        source="profile.transcript_description", allow_null=True
    )
    advisor_name = serializers.CharField(source="profile.advisor_name", allow_null=True)
    advisor_email = serializers.EmailField(
        source="profile.advisor_email", allow_null=True
    )
    department_code = serializers.CharField(
        source="profile.department_code", allow_null=True
    )
    business_unit = serializers.CharField(
        source="profile.business_unit", allow_null=True
    )

    class Meta:
        model = User

        fields = [
            "username",
            "email",
            "member_id",
            "official_name",
            "role",
            "is_admin",
            "nricpsprt",
            "gender",
            "phone",
            "emergency_contact",
            "personal_email",
            "address_1",
            "address_2",
            "address_3",
            "address_4",
            "postal_code",
            "city",
            "state",
            "country",
            "location",
            "position",
            "cohort_code",
            "program_description",
            "transcript_description",
            "advisor_name",
            "advisor_email",
            "department_code",
            "business_unit",
        ]
