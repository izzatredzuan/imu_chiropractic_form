from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Profile


# -----------------------------
# CREATE Serializer
# -----------------------------
class UserProfileCreateSerializer(serializers.ModelSerializer):
    member_id = serializers.CharField(required=False)
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES, default="student")
    phone = serializers.CharField(required=False, allow_blank=True)
    is_admin = serializers.BooleanField(default=False)
    official_name = serializers.CharField(required=True)
    # official_name = serializers.CharField(source="profile.official_name", required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "member_id",
            "official_name",
            "role",
            "phone",
            "is_admin",
        ]

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        # Pop profile fields
        member_id = validated_data.pop("member_id", None)
        official_name = validated_data.pop("official_name")
        role = validated_data.pop("role")
        phone = validated_data.pop("phone", "")
        is_admin = validated_data.pop("is_admin", False)

        # Create the user
        user = User.objects.create_user(**validated_data)

        # Auto-generate member_id if not provided
        if not member_id:
            member_id = f"{role[:3].upper()}{user.id:04d}"

        # Create or update Profile safely
        profile, created = Profile.objects.update_or_create(
            user=user,
            defaults={
                "member_id": member_id,
                "official_name": official_name,
                "role": role,
                "phone": phone,
                "is_admin": is_admin,
            },
        )

        return user


# -----------------------------
# UPDATE Serializer
# -----------------------------
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    member_id = serializers.CharField(required=False)
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES, required=False)
    phone = serializers.CharField(required=False, allow_blank=True)
    is_admin = serializers.BooleanField(required=False)
    official_name = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "member_id",
            "official_name",
            "role",
            "phone",
            "is_admin",
        ]

    # Validate password if provided
    def validate_password(self, value):
        if value:
            try:
                validate_password(value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.messages)
        return value

    # Update User and Profile
    def update(self, instance, validated_data):
        profile_data = {}
        for field in ["member_id", "official_name", "role", "phone", "is_admin"]:
            if field in validated_data:
                profile_data[field] = validated_data.pop(field)

        # Update User fields
        for attr, value in validated_data.items():
            if attr == "password":
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()

        # Update Profile
        profile = instance.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance


# -----------------------------
# READ Serializer
# -----------------------------
class UserProfileReadSerializer(serializers.ModelSerializer):
    member_id = serializers.CharField(source="profile.member_id")
    official_name = serializers.CharField(source="profile.official_name")
    role = serializers.CharField(source="profile.role")
    phone = serializers.CharField(source="profile.phone")
    is_admin = serializers.BooleanField(source="profile.is_admin")

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "member_id",
            "official_name",
            "role",
            "phone",
            "is_admin",
        ]
