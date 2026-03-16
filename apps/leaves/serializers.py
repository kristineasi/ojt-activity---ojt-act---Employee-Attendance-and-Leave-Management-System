from rest_framework import serializers

from .models import LeaveRequest


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.get_full_name", read_only=True)
    approver_name = serializers.CharField(source="approver.get_full_name", read_only=True)
    total_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee",
            "employee_name",
            "leave_type",
            "start_date",
            "end_date",
            "total_days",
            "reason",
            "status",
            "approver",
            "approver_name",
            "manager_comment",
            "approved_at",
            "created_at",
        ]
        read_only_fields = ["employee", "status", "approver", "approved_at", "created_at", "manager_comment"]

    def validate(self, attrs):
        if attrs["end_date"] < attrs["start_date"]:
            raise serializers.ValidationError("End date must not be earlier than start date.")
        return attrs


class LeaveDecisionSerializer(serializers.Serializer):
    manager_comment = serializers.CharField(required=False, allow_blank=True)
