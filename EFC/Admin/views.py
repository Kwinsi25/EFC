from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SystemLog
from .serializers import SystemLogSerializer

class AllSystemLogsView(APIView):
    """
    Public API to fetch all system logs (admin-level view).

    - No authentication required.
    - Returns all system logs across all users.
    - Use for admin panel or testing.
    """

    def get(self, request):
        logs = SystemLog.objects.all().order_by('-created_date')
        serializer = SystemLogSerializer(logs, many=True)

        return Response({
            "status": 200,
            "message": "All system logs fetched successfully",
            "data": {
                "logs": serializer.data
            }
        }, status=200)
