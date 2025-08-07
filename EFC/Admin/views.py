from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SystemLog
from .serializers import SystemLogSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
class AllSystemLogsView(APIView):
    permission_classes = [IsAuthenticated]  # Require login

    def get(self, request):
        user = request.user

        # Check if logged-in user is admin
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({
                "status": 403,
                "message": "Access denied. Admins only.",
                "data": {}
            }, status=status.HTTP_403_FORBIDDEN)

        logs = SystemLog.objects.all().order_by('-created_date')
        serializer = SystemLogSerializer(logs, many=True)

        return Response({
            "status": 200,
            "message": "All system logs fetched successfully",
            "data": {
                "logs": serializer.data
            }
        }, status=200)
