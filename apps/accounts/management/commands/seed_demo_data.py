from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.attendance.models import AttendanceRecord
from apps.leaves.models import LeaveRequest


class Command(BaseCommand):
    help = "Create one-click demo manager/employee data with attendance and leave records."

    def handle(self, *args, **options):
        user_model = get_user_model()

        manager, _ = user_model.objects.get_or_create(
            username="manager_demo",
            defaults={
                "first_name": "Mira",
                "last_name": "Manager",
                "email": "manager_demo@example.com",
                "department": "Operations",
                "role": user_model.Role.MANAGER,
                "is_staff": True,
            },
        )
        manager.role = user_model.Role.MANAGER
        manager.department = manager.department or "Operations"
        manager.email = manager.email or "manager_demo@example.com"
        manager.set_password("DemoPass123!")
        manager.save()

        employee, _ = user_model.objects.get_or_create(
            username="employee_demo",
            defaults={
                "first_name": "Eli",
                "last_name": "Employee",
                "email": "employee_demo@example.com",
                "department": "Operations",
                "role": user_model.Role.EMPLOYEE,
            },
        )
        employee.role = user_model.Role.EMPLOYEE
        employee.department = employee.department or "Operations"
        employee.email = employee.email or "employee_demo@example.com"
        employee.set_password("DemoPass123!")
        employee.save()

        today = timezone.localdate()
        yesterday = today - timedelta(days=1)

        AttendanceRecord.objects.update_or_create(
            employee=employee,
            date=yesterday,
            defaults={
                "time_in": timezone.make_aware(datetime.combine(yesterday, datetime.min.time().replace(hour=9))),
                "time_out": timezone.make_aware(datetime.combine(yesterday, datetime.min.time().replace(hour=17))),
                "worked_hours": Decimal("8.00"),
            },
        )

        AttendanceRecord.objects.update_or_create(
            employee=employee,
            date=today,
            defaults={
                "time_in": timezone.now() - timedelta(hours=2),
                "time_out": None,
                "worked_hours": Decimal("0.00"),
            },
        )

        LeaveRequest.objects.update_or_create(
            employee=employee,
            start_date=today + timedelta(days=2),
            end_date=today + timedelta(days=3),
            defaults={
                "leave_type": LeaveRequest.LeaveType.VACATION,
                "reason": "Family event",
                "status": LeaveRequest.Status.PENDING,
                "approver": None,
                "manager_comment": "",
                "approved_at": None,
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo data created or updated successfully."))
        self.stdout.write("manager_demo / DemoPass123! (manager)")
        self.stdout.write("employee_demo / DemoPass123! (employee)")
