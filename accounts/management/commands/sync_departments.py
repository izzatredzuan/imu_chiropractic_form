import logging
from django.core.management.base import BaseCommand
from accounts.models import Department
from accounts.services import get_imu_employee_details

logger = logging.getLogger("userprofile")

class Command(BaseCommand):
    help = "Sync departments from IMU API"

    def handle(self, *args, **kwargs):
        employees = get_imu_employee_details()
        logger.info(f"Retrieved {len(employees)} employee records from IMU API.")
        created_count = 0

        for emp in employees:
            dept_code = emp.get("DEPT_CODE")
            dept_name = emp.get("DEPT")

            if not dept_code:
                continue

            department, created = Department.objects.get_or_create(
                department_code=dept_code, defaults={"department_name": dept_name}
            )

            if created:
                created_count += 1
                logger.info(
                    "DEPARTMENT CREATED - department_code=%s, department_name=%s",
                    department.department_code,
                    department.department_name,
                )
            else:
                logger.debug(
                    "Department already exists - department_code=%s",
                    department.department_code,
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Sync completed. {created_count} new departments created."
            )
        )
