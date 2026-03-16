from rest_framework import serializers

from .models import AttendanceRecord


class AttendanceRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.get_full_name", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            "id",
            "employee",
            "employee_name",
            "date",
            "time_in",
            "time_out",
            "worked_hours",
        ]
        read_only_fields = ["employee", "worked_hours", "time_out", "date"]
