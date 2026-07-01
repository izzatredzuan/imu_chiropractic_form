import requests
from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings

def generate_temp_password(length=12):
    return get_random_string(
        length=length,
        allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789@#$"
    )

def send_temp_password_email(user, full_name, temp_password):
    send_mail(
        subject="IMU Chiropractic Application Account Registration – Temporary Login Credentials",
        message=f"""
        Dear {full_name},

        Your IMU account has been successfully created.

        You may now log in using the following credentials:

        Username: {user.username}
        Temporary Password: {temp_password}

        For security reasons, you are strongly advised to change your password immediately after your first login.

        If you encounter any issues accessing your account or require further assistance, please contact the IMU IT Support team.

        Thank you.

        Kind regards,

        IMU IT Services
        International Medical University
        """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            # recipient_list=["izzatredzuan@imu.edu.my"],
            fail_silently=False,
        )


def send_reset_password_email(user, reset_link):
    send_mail(
            subject="IMU Chiropractic Application Account Password Reset",
            message=f"""
            Dear {user.profile.official_name},

            We received a request to reset the password for your IMU account.

            Please click the link below to set a new password:

            {reset_link}

            If you did not request this password reset, you may safely ignore this email.

            Kind regards,

            IMU IT Services
            International Medical University
            """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
    
# API Configuration
# HEADERS = {
#     "x-functions-key": "mF5mDk4S3fPFC_60ETADBUUafITYSZS3fQA8xobV4HgxAzFuTbBW6Q=="
# }

# BASE_URL = "https://imuapi.azurewebsites.net/api/SqlToREST/IMU"

HEADERS = {
    "x-functions-key": settings.AZURE_FUNCTION_KEY
}

BASE_URL = settings.AZURE_BASE_URL

def get_imu_employee_details(employee_id=None):
    if employee_id:
        url = f"{BASE_URL}/EmployeeInfoById"
        params = {"EMPLID": employee_id}
    else:
        url = f"{BASE_URL}/EmployeeInfo"
        params = None

    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()

    return response.json()


def get_imu_student_details(student_id=None):
    if student_id:
        url = f"{BASE_URL}/StudentProgramInfoById"
        params = {"EMPLID": student_id}
    else:
        url = f"{BASE_URL}/StudentProgramInfo"
        params = None

    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()
