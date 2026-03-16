from django.contrib import admin

from .models import LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("employee", "leave_type", "start_date", "end_date", "status", "approver")
    list_filter = ("status", "leave_type", "start_date")
    search_fields = ("employee__username", "employee__first_name", "employee__last_name")
