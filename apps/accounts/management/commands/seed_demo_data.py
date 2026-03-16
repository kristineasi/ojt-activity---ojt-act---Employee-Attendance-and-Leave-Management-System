from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.attendance.models import AttendanceRecord
from apps.leaves.models import LeaveRequest


class Command(BaseCommand):
    help = "Create one-click manager and employee accounts with clean attendance and leave records."

    def handle(self, *args, **options):
        user_model = get_user_model()

        user_model.objects.filter(username__in=["manager_demo", "employee_demo"]).delete()

        manager, _ = user_model.objects.update_or_create(
            username="@admin",
            defaults={
                "first_name": "System",
                "last_name": "Administrator",
                "email": "admin@example.com",
                "department": "Management",
                "role": user_model.Role.MANAGER,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        manager.set_password("Admin@123")
        manager.save()

        employees = [
            {
                "username": "jrobles",
                "password": "P@ssw0rd1",
                "first_name": "J",
                "last_name": "Robles",
                "email": "jrobles@example.com",
            },
            {
                "username": "aarceta",
                "password": "P@ssw0rd2",
                "first_name": "A",
                "last_name": "Arceta",
                "email": "aarceta@example.com",
            },
            {
                "username": "mlim",
                "password": "P@ssw0rd3",
                "first_name": "M",
                "last_name": "Lim",
                "email": "mlim@example.com",
            },
            {
                "username": "cvergara",
                "password": "P@ssw0rd4",
                "first_name": "C",
                "last_name": "Vergara",
                "email": "cvergara@example.com",
            },
        ]

        seeded_employees = []
        for employee_data in employees:
            password = employee_data.pop("password")
            employee, _ = user_model.objects.update_or_create(
                username=employee_data["username"],
                defaults={
                    **employee_data,
                    "department": "Operations",
                    "role": user_model.Role.EMPLOYEE,
                    "is_staff": False,
                    "is_superuser": False,
                },
            )
            employee.set_password(password)
            employee.save()
            seeded_employees.append((employee, password))

        seeded_users = [manager, *(employee for employee, _ in seeded_employees)]
        AttendanceRecord.objects.filter(employee__in=seeded_users).delete()
        LeaveRequest.objects.filter(employee__in=seeded_users).delete()

        self.stdout.write(self.style.SUCCESS("Accounts synced successfully. Attendance and leave records were cleared."))
        self.stdout.write("@admin / Admin@123 (manager)")
        for employee, password in seeded_employees:
            self.stdout.write(f"{employee.username} / {password} (employee)")
