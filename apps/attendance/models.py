from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class AttendanceRecord(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField(default=timezone.localdate)
    time_in = models.DateTimeField(default=timezone.now)
    time_out = models.DateTimeField(null=True, blank=True)
    worked_hours = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        unique_together = ("employee", "date")
        ordering = ["-date", "-time_in"]

    def compute_worked_hours(self):
        if not self.time_out:
            return Decimal("0.00")
        elapsed = self.time_out - self.time_in
        hours = Decimal(str(elapsed.total_seconds() / 3600)).quantize(Decimal("0.01"))
        return max(hours, Decimal("0.00"))

    def close_shift(self):
        self.time_out = timezone.now()
        self.worked_hours = self.compute_worked_hours()
        self.save(update_fields=["time_out", "worked_hours"])

    def __str__(self):
        return f"{self.employee.username} - {self.date}"
