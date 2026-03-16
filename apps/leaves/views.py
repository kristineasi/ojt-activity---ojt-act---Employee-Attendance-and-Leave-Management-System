from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsManager

from .models import LeaveRequest
from .serializers import LeaveDecisionSerializer, LeaveRequestSerializer


class LeaveRequestListCreateAPIView(APIView):
    def get(self, request):
        queryset = LeaveRequest.objects.all() if request.user.role == "manager" else LeaveRequest.objects.filter(employee=request.user)
        serializer = LeaveRequestSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LeaveRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        leave_request = serializer.save(employee=request.user)
        return Response(LeaveRequestSerializer(leave_request).data, status=status.HTTP_201_CREATED)


class ApproveLeaveAPIView(APIView):
    permission_classes = [IsManager]

    def patch(self, request, pk):
        leave_request = LeaveRequest.objects.filter(pk=pk).first()
        if not leave_request:
            return Response({"detail": "Leave request not found."}, status=status.HTTP_404_NOT_FOUND)
        if leave_request.status != LeaveRequest.Status.PENDING:
            return Response({"detail": "Only pending requests can be approved."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LeaveDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        leave_request.approve(request.user, serializer.validated_data.get("manager_comment", ""))
        return Response(LeaveRequestSerializer(leave_request).data)


class RejectLeaveAPIView(APIView):
    permission_classes = [IsManager]

    def patch(self, request, pk):
        leave_request = LeaveRequest.objects.filter(pk=pk).first()
        if not leave_request:
            return Response({"detail": "Leave request not found."}, status=status.HTTP_404_NOT_FOUND)
        if leave_request.status != LeaveRequest.Status.PENDING:
            return Response({"detail": "Only pending requests can be rejected."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LeaveDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        leave_request.reject(request.user, serializer.validated_data.get("manager_comment", ""))
        return Response(LeaveRequestSerializer(leave_request).data)
