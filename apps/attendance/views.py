from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from .models import AttendanceRecord
from .serializers import AttendanceRecordSerializer

User = get_user_model()
STANDARD_HOURS_PER_DAY = Decimal("8.00")
OVERTIME_MULTIPLIER = Decimal("1.25")


def parse_month_year(request):
    try:
        month = int(request.query_params.get("month", timezone.localdate().month))
        year = int(request.query_params.get("year", timezone.localdate().year))
    except (TypeError, ValueError):
        return None, None, Response({"detail": "Month and year must be valid integers."}, status=status.HTTP_400_BAD_REQUEST)

    if month < 1 or month > 12:
        return None, None, Response({"detail": "Month must be between 1 and 12."}, status=status.HTTP_400_BAD_REQUEST)

    if year < 1900 or year > 9999:
        return None, None, Response({"detail": "Year is out of supported range."}, status=status.HTTP_400_BAD_REQUEST)

    return month, year, None


def summarize_payroll(records, hourly_rate):
    regular_hours = Decimal("0.00")
    overtime_hours = Decimal("0.00")

    for record in records:
        hours = record.worked_hours or Decimal("0.00")
        regular_hours += min(hours, STANDARD_HOURS_PER_DAY)
        overtime_hours += max(hours - STANDARD_HOURS_PER_DAY, Decimal("0.00"))

    regular_hours = regular_hours.quantize(Decimal("0.01"))
    overtime_hours = overtime_hours.quantize(Decimal("0.01"))
    regular_pay = (regular_hours * hourly_rate).quantize(Decimal("0.01"))
    overtime_pay = (overtime_hours * hourly_rate * OVERTIME_MULTIPLIER).quantize(Decimal("0.01"))
    total_pay = (regular_pay + overtime_pay).quantize(Decimal("0.01"))

    return {
        "regular_hours": regular_hours,
        "overtime_hours": overtime_hours,
        "hourly_rate": hourly_rate,
        "regular_pay": regular_pay,
        "overtime_pay": overtime_pay,
        "total_pay": total_pay,
    }


class TimeInAPIView(APIView):
    def post(self, request):
        today = timezone.localdate()
        record, created = AttendanceRecord.objects.get_or_create(
            employee=request.user,
            date=today,
            defaults={"time_in": timezone.now()},
        )
        if not created and record.time_out is None:
            return Response({"detail": "You already timed in today."}, status=status.HTTP_400_BAD_REQUEST)
        if not created and record.time_out is not None:
            return Response({"detail": "Shift already completed for today."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(AttendanceRecordSerializer(record).data, status=status.HTTP_201_CREATED)


class TimeOutAPIView(APIView):
    def post(self, request):
        today = timezone.localdate()
        record = AttendanceRecord.objects.filter(employee=request.user, date=today).first()
        if not record:
            return Response({"detail": "No active shift found for today."}, status=status.HTTP_400_BAD_REQUEST)
        if record.time_out:
            return Response({"detail": "You already timed out today."}, status=status.HTTP_400_BAD_REQUEST)

        record.close_shift()
        return Response(AttendanceRecordSerializer(record).data)


class MyAttendanceAPIView(APIView):
    def get(self, request):
        queryset = AttendanceRecord.objects.all() if request.user.role == "manager" else AttendanceRecord.objects.filter(employee=request.user)
        serializer = AttendanceRecordSerializer(queryset, many=True)
        return Response(serializer.data)


class AttendanceSummaryAPIView(APIView):
    def get(self, request):
        month, year, error_response = parse_month_year(request)
        if error_response:
            return error_response

        records = AttendanceRecord.objects.filter(date__month=month, date__year=year)
        if request.user.role != "manager":
            records = records.filter(employee=request.user)

        total_hours = records.aggregate(total=Sum("worked_hours"))["total"] or Decimal("0.00")
        return Response(
            {
                "month": month,
                "year": year,
                "days_logged": records.count(),
                "total_hours": total_hours,
            }
        )


class SalarySummaryAPIView(APIView):
    def get(self, request):
        month, year, error_response = parse_month_year(request)
        if error_response:
            return error_response

        records = AttendanceRecord.objects.filter(date__month=month, date__year=year)

        if request.user.role == "manager":
            employees = User.objects.filter(role=User.Role.EMPLOYEE).order_by("first_name", "last_name", "username")
            employee_items = []
            totals = {
                "regular_hours": Decimal("0.00"),
                "overtime_hours": Decimal("0.00"),
                "regular_pay": Decimal("0.00"),
                "overtime_pay": Decimal("0.00"),
                "total_pay": Decimal("0.00"),
            }

            for employee in employees:
                employee_records = list(records.filter(employee=employee))
                summary = summarize_payroll(employee_records, employee.hourly_rate)
                for key in totals:
                    totals[key] = (totals[key] + summary[key]).quantize(Decimal("0.01"))

                employee_items.append(
                    {
                        "employee_id": employee.id,
                        "employee_name": employee.get_full_name() or employee.username,
                        "username": employee.username,
                        "records_count": len(employee_records),
                        **summary,
                    }
                )

            return Response(
                {
                    "month": month,
                    "year": year,
                    "overtime_multiplier": OVERTIME_MULTIPLIER,
                    "employees": employee_items,
                    "totals": totals,
                }
            )

        employee_records = list(records.filter(employee=request.user))
        summary = summarize_payroll(employee_records, request.user.hourly_rate)
        return Response(
            {
                "month": month,
                "year": year,
                "overtime_multiplier": OVERTIME_MULTIPLIER,
                "employee": {
                    "employee_id": request.user.id,
                    "employee_name": request.user.get_full_name() or request.user.username,
                    "username": request.user.username,
                    "records_count": len(employee_records),
                    **summary,
                },
            }
        )
