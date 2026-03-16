from django.urls import path

from .views import ApproveLeaveAPIView, LeaveRequestListCreateAPIView, RejectLeaveAPIView

urlpatterns = [
    path("requests/", LeaveRequestListCreateAPIView.as_view(), name="leave-list-create"),
    path("requests/<int:pk>/approve/", ApproveLeaveAPIView.as_view(), name="leave-approve"),
    path("requests/<int:pk>/reject/", RejectLeaveAPIView.as_view(), name="leave-reject"),
]
