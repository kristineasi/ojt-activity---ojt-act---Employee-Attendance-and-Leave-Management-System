from django.conf import settings
from django.db import models
from django.utils import timezone


class LeaveRequest(models.Model):
    class LeaveType(models.TextChoices):
        VACATION = "vacation", "Vacation"
        SICK = "sick", "Sick"
        EMERGENCY = "emergency", "Emergency"
        UNPAID = "unpaid", "Unpaid"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leave_requests",
    )
    manager_comment = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def total_days(self):
        return (self.end_date - self.start_date).days + 1

    def approve(self, manager, comment=""):
        self.status = self.Status.APPROVED
        self.approver = manager
        self.manager_comment = comment
        self.approved_at = timezone.now()
        self.save(update_fields=["status", "approver", "manager_comment", "approved_at"])

    def reject(self, manager, comment=""):
        self.status = self.Status.REJECTED
        self.approver = manager
        self.manager_comment = comment
        self.approved_at = timezone.now()
        self.save(update_fields=["status", "approver", "manager_comment", "approved_at"])

    def __str__(self):
        return f"{self.employee.username} {self.leave_type} ({self.status})"
