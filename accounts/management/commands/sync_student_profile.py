import logging

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import Profile
from accounts.services import (
    generate_temp_password,
    get_imu_student_details,
    send_temp_password_email,
)

logger = logging.getLogger("userprofile")


# Sync all students
# python manage.py sync_student_profile

# Sync one student
# python manage.py sync_student_profile 00000051843


# Sync multiple students
# python manage.py sync_student_profile 00000051843 00000051844 00000051845
class Command(BaseCommand):
    help = "Sync IMU students into User and Profile models"

    def add_arguments(self, parser):
        parser.add_argument(
            "student_ids",
            nargs="*",
            type=str,
            help="One or more student IDs to sync.",
        )
        parser.add_argument(
            "--create-only",
            action="store_true",
            help="Create new users only. Existing users are skipped.",
        )
        parser.add_argument(
            "--update-only",
            action="store_true",
            help="Update existing users only. New users are skipped.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run the sync without saving changes.",
        )

    def handle(self, *args, **options):
        student_ids = options.get("student_ids") or []
        student_ids_set = set(student_ids)

        create_only = options["create_only"]
        update_only = options["update_only"]
        dry_run = options["dry_run"]

        if create_only and update_only:
            raise CommandError(
                "--create-only and --update-only cannot be used together."
            )

        logger.info(
            "Student sync started. Filter=%s",
            ", ".join(student_ids) if student_ids else "ALL",
        )

        students = get_imu_student_details(student_ids)

        created_count = 0
        updated_count = 0
        skipped_count = 0

        logger.info("Retrieved %s student records from IMU API.", len(students))

        gender_map = {
            "Male": "male",
            "Female": "female",
        }

        for student in students:
            member_id = student.get("EMPLID")

            if not member_id:
                skipped_count += 1
                logger.warning("Skipping record with missing EMPLID")
                continue

            if student_ids and member_id not in student_ids_set:
                continue

            try:
                with transaction.atomic():
                    profile = (
                        Profile.objects.filter(member_id=member_id)
                        .select_related("user")
                        .first()
                    )

                    # Existing user
                    if profile:
                        if create_only:
                            skipped_count += 1
                            logger.info(
                                "SKIPPED (already exists) - member_id=%s",
                                member_id,
                            )
                            continue

                        user = profile.user
                        created = False

                    # New user
                    else:
                        if update_only:
                            skipped_count += 1
                            logger.info(
                                "SKIPPED (user does not exist) - member_id=%s",
                                member_id,
                            )
                            continue

                        temp_password = generate_temp_password()

                        user = User.objects.create_user(
                            username=member_id,
                            email=student.get("STU_EMAIL_ADDR") or "",
                        )

                        user.set_password(temp_password)

                        if not dry_run:
                            user.save()
                            send_temp_password_email(
                                user, student["LONG_FULL_NAME"], temp_password
                            )

                        created = True

                    user.email = student.get("STU_EMAIL_ADDR") or ""

                    if not dry_run:
                        user.save()

                        profile, _ = Profile.objects.update_or_create(
                            user=user,
                            defaults={
                                "member_id": member_id,
                                "official_name": student.get("LONG_FULL_NAME", ""),
                                "role": "student",
                                "gender": gender_map.get(student.get("GENDER")),
                                "nricpsprt": student.get("NRICPSPRT"),
                                "phone": student.get("MOBILE"),
                                "emergency_contact": student.get("EMER_PHONE"),
                                "personal_email": student.get("EMAIL_ADDR"),
                                "address_1": student.get("ADDRESS1"),
                                "address_2": student.get("ADDRESS2"),
                                "address_3": student.get("ADDRESS3"),
                                "address_4": student.get("ADDRESS4"),
                                "postal_code": student.get("POSTAL"),
                                "city": student.get("CITY"),
                                "state": student.get("STATEDESCR"),
                                "country": student.get("COUNTRYDESCR"),
                                "location": student.get("CAMPUS"),
                                "cohort_code": student.get("INTAKE"),
                                "program_description": student.get("PROG_DESCR"),
                                "transcript_description": student.get("TRNSCR_DESCR"),
                                "advisor_name": student.get("ADVISOR_NAME"),
                                "advisor_email": student.get("ADVISOR_EMAIL"),
                            },
                        )

                    if created:
                        profile.first_time_password_change = True
                        profile.save(update_fields=["first_time_password_change"])
                        created_count += 1
                        logger.info(
                            "USER CREATED - username=%s member_id=%s role=student",
                            user.username,
                            member_id,
                        )
                    else:
                        updated_count += 1
                        logger.info(
                            "USER UPDATED - username=%s member_id=%s role=student",
                            user.username,
                            member_id,
                        )

            except Exception:
                skipped_count += 1
                logger.exception("Failed to sync student %s", member_id)

        logger.info(
            "Student sync completed. Created=%s Updated=%s Skipped=%s",
            created_count,
            updated_count,
            skipped_count,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created={created_count}, Updated={updated_count}, Skipped={skipped_count}"
            )
        )
