from django.contrib import admin

from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "time_in", "time_out", "worked_hours")
    list_filter = ("date", "employee")
    search_fields = ("employee__username", "employee__first_name", "employee__last_name")
