from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal


class User(AbstractUser):
    class Role(models.TextChoices):
        EMPLOYEE = "employee", "Employee"
        MANAGER = "manager", "Manager"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    department = models.CharField(max_length=120, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("100.00"))

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"
