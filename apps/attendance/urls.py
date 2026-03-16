from django.urls import path

from .views import AttendanceSummaryAPIView, MyAttendanceAPIView, SalarySummaryAPIView, TimeInAPIView, TimeOutAPIView

urlpatterns = [
    path("time-in/", TimeInAPIView.as_view(), name="time-in"),
    path("time-out/", TimeOutAPIView.as_view(), name="time-out"),
    path("my-records/", MyAttendanceAPIView.as_view(), name="my-attendance-records"),
    path("summary/", AttendanceSummaryAPIView.as_view(), name="attendance-summary"),
    path("salary-summary/", SalarySummaryAPIView.as_view(), name="salary-summary"),
]
