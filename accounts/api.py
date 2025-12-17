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
    # -----------------------------
    # GET User(s)
    # -----------------------------
    def get(self, request):
        member_ids = request.data.get("member_id")  # get list from JSON body

        if member_ids:
            profiles = Profile.objects.filter(member_id__in=member_ids)
            users = [profile.user for profile in profiles]
        else:
            users = User.objects.all()

        serializer = UserProfileReadSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


"""
    -----------------------------------
    CREATE User + Profile
    -----------------------------------

       Returns
       -------
       dict

       Examples
       --------
           {
       "username": "john",
       "email": "john@example.com",
       "password": "pass1234",
       "role": "student",
       "phone": "1234567890",
       "is_admin": false
       }

    """


class UserProfileCreateAPIView(APIView):
    # permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = UserProfileCreateSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            username = validated_data.get("username")
            email = validated_data.get("email")

            # Check if username or email exists
            if User.objects.filter(username=username).exists():
                return Response({"username": "Username already exists"}, status=400)
            if User.objects.filter(email=email).exists():
                return Response({"email": "Email already exists"}, status=400)

            try:
                with transaction.atomic():
                    user = serializer.save()  # User + Profile created

                    # Refresh the user queried to get the correct data
                    user.refresh_from_db()
                    user.profile.refresh_from_db()
            except Exception as e:
                logger.error(f"CREATE - Failed: {str(e)}")
                return Response({"error": str(e)}, status=400)

            profile = user.profile     
            logger.info(
                f"CREATE - User created: username={username}, member_id={profile.member_id}, "
                f"official_name={profile.official_name}, role={profile.role}"
            )

            response = UserProfileReadSerializer(user).data
            response["message"] = "User created successfully"
            return Response(response, status=status.HTTP_201_CREATED)

        logger.error(f"CREATE - Failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------
# EDIT / UPDATE User + Profile
# -----------------------------------
class UserProfileUpdateAPIView(APIView):
    # permission_classes = [permissions.IsAdminUser]

    def put(self, request):
        member_id = request.data.get("member_id")
        if not member_id:
            logger.error("UPDATE - member_id not provided")
            return Response({"error": "member_id is required"}, status=400)

        profile = get_object_or_404(Profile, member_id=member_id)
        user = profile.user

        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    serializer.save()
            except Exception as e:
                logger.error(f"UPDATE - Failed for member_id={member_id}: {str(e)}")
                return Response({"error": str(e)}, status=400)

            profile.refresh_from_db()
            logger.info(
                f"UPDATE - User updated: username={user.username}, member_id={profile.member_id}, "
                f"official_name={profile.official_name}, role={profile.role}"
            )

            response = UserProfileReadSerializer(user).data
            response["message"] = "User updated successfully"
            return Response(response, status=status.HTTP_200_OK)

        logger.error(f"UPDATE - Failed for member_id={member_id}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------
# DELETE User + Profile
# -----------------------------------
class UserProfileDeleteAPIView(APIView):
    # permission_classes = [permissions.IsAdminUser]

    def delete(self, request):
        member_ids = request.data.get("member_id")  # str or list

        if not member_ids:
            return Response({"error": "member_id is required"}, status=400)

        # Normalize input
        if isinstance(member_ids, str):
            member_ids = [member_ids.strip()]
        elif isinstance(member_ids, list):
            member_ids = [mid.strip() for mid in member_ids]
        else:
            return Response({"error": "member_id must be a string or list"}, status=400)

        # Get matching profiles
        profiles_to_delete = Profile.objects.filter(member_id__in=member_ids)

        if not profiles_to_delete.exists():
            return Response({"message": "No users found to delete."}, status=404)

        # Collect info for logging
        deleted_info = [
            {
                "username": profile.user.username,
                "member_id": profile.member_id,
                "official_name": profile.official_name,
            }
            for profile in profiles_to_delete
        ]

        # Delete all related users (cascades to Profile)
        User.objects.filter(profile__in=profiles_to_delete).delete()

        # Log deletion
        for info in deleted_info:
            logger.info(
                f"DELETE - User deleted successfully: username={info['username']}, "
                f"member_id={info['member_id']}, official_name={info['official_name']}"
            )

        return Response(
            {
                "deleted_count": len(deleted_info),
                "deleted": deleted_info,
                "message": f"{len(deleted_info)} user(s) deleted successfully.",
            },
            status=200,
        )
