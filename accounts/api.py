import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Profile

# from .serializers import UserProfileSerializer
from .serializers import (
    UserProfileCreateSerializer,
    UserProfileUpdateSerializer,
    UserProfileReadSerializer,
)

logger = logging.getLogger("userprofile")


class UserProfileAPIView(APIView):
    def get(self, request):
        member_ids = request.query_params.getlist("member_id")

        if member_ids:
            profiles = Profile.objects.filter(member_id__in=member_ids)
            users = [p.user for p in profiles]
        else:
            users = User.objects.all()

        serializer = UserProfileReadSerializer(users, many=True)
        return Response(serializer.data, status=200)
    

class UserProfileCreateAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = UserProfileCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        validated_data = serializer.validated_data

        username = validated_data.get("username")
        email = validated_data.get("email")

        if User.objects.filter(username=username).exists():
            return Response({"username": "Username already exists"}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({"email": "Email already exists"}, status=400)

        try:
            with transaction.atomic():
                user = serializer.save()

                user.refresh_from_db()
                user.profile.refresh_from_db()

            logger.info(
                f"CREATE SUCCESS - username={user.username}, "
                f"member_id={user.profile.member_id}, "
                f"official_name={user.profile.official_name}, "
                f"role={user.profile.role}"
            )

        except Exception as e:
            logger.error(f"CREATE failed: {str(e)}")
            return Response({"error": str(e)}, status=400)

        response = UserProfileReadSerializer(user).data
        response["message"] = "User created successfully"

        return Response(response, status=201)
    

# -----------------------------------
# EDIT / UPDATE User + Profile
# -----------------------------------
class UserProfileUpdateAPIView(APIView):
    # permission_classes = [permissions.IsAdminUser]

    def put(self, request):
        member_id = request.data.get("member_id")

        if not member_id:
            return Response(
                {"error": "member_id is required"},
                status=400
            )

        profile = get_object_or_404(Profile, member_id=member_id)
        user = profile.user

        serializer = UserProfileUpdateSerializer(
            user,
            data=request.data,
            partial=True
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        try:
            with transaction.atomic():
                serializer.save()

        except Exception as e:
            logger.error(f"UPDATE failed: {str(e)}")
            return Response({"error": str(e)}, status=400)

        user.refresh_from_db()
        profile.refresh_from_db()

        logger.info(
            f"UPDATE SUCCESS - username={user.username}, "
            f"member_id={profile.member_id}, "
            f"official_name={profile.official_name}, "
            f"role={profile.role}"
        )

        response = UserProfileReadSerializer(user).data
        response["message"] = "User updated successfully"

        return Response(response, status=200)


# -----------------------------------
# DELETE User + Profile
# -----------------------------------
class UserProfileDeleteAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request):
        member_ids = request.data.get("member_id")

        if not member_ids:
            return Response(
                {"error": "member_id is required"},
                status=400
            )

        if isinstance(member_ids, str):
            member_ids = [member_ids.strip()]
        elif isinstance(member_ids, list):
            member_ids = [m.strip() for m in member_ids]
        else:
            return Response(
                {"error": "member_id must be string or list"},
                status=400
            )

        profiles = Profile.objects.filter(member_id__in=member_ids)

        if not profiles.exists():
            return Response(
                {"message": "No users found to delete"},
                status=404
            )

        deleted_info = [
            {
                "username": p.user.username,
                "member_id": p.member_id,
                "official_name": p.official_name,
            }
            for p in profiles
        ]

        User.objects.filter(profile__in=profiles).delete()

        for info in deleted_info:
            logger.info(
                f"DELETE user: username={info['username']}, "
                f"member_id={info['member_id']}"
            )

        return Response(
            {
                "deleted_count": len(deleted_info),
                "deleted": deleted_info,
                "message": "Users deleted successfully"
            },
            status=200
        )