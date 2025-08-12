from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework import generics, permissions, status
from django.utils import timezone
import os
from django.conf import settings
from django.http import FileResponse, Http404
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf_report(file_path, report_type):
    c = canvas.Canvas(file_path, pagesize=letter)
    c.setFont("Helvetica", 14)
    c.drawString(100, 750, f"{report_type.capitalize()} Report")
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(100, 690, "This is a sample PDF report content.")
    c.showPage()
    c.save()

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


ALLOWED_REPORT_TYPES = [
    'booking',
    'earning',
    'complaint',
    'technician',
    'user',
    'wallet',
]

class ReportListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReportLogSerializer

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == 'admin':
            return ReportLog.objects.all().order_by('-created_date')
        return ReportLog.objects.filter(username=user).order_by('-created_date')

    def create(self, request, *args, **kwargs):
        user = request.user

        if getattr(user, 'role', None) != 'admin':
            return Response({"status": 403, "message": "Only admins can generate reports."}, status=403)

        report_type = request.data.get("type")
        if report_type not in ALLOWED_REPORT_TYPES:
            return Response({
                "status": 400,
                "message": f"Invalid report type. Allowed types: {', '.join(ALLOWED_REPORT_TYPES)}"
            }, status=400)

        file_format = request.data.get("format", "pdf")
        if file_format not in ["pdf", "csv"]:
            return Response({"status": 400, "message": "Invalid format. Allowed: pdf, csv"}, status=400)

        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        filename = f"{report_type}_{timestamp}.{file_format}"

        # Physical path where file will be saved
        reports_dir = os.path.join(settings.MEDIA_ROOT, "reports/")
        os.makedirs(reports_dir, exist_ok=True)
        file_path = os.path.join(reports_dir, filename)

        if file_format == "pdf":
            generate_pdf_report(file_path, report_type)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Dummy {report_type} report generated at {timestamp}")

        link = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, "reports/", filename))
        serializer = self.get_serializer(data={
            **request.data,
            "generated_by": user.id,
            "export_by": user.id,
            "link": link
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "status": 200,
            "message": "Report created successfully",
            "data": serializer.data
        })

class ReportDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            report = ReportLog.objects.get(id=pk)
        except ReportLog.DoesNotExist:
            return Response({"status": 404, "message": "Report not found"}, status=404)

        # Check permission
        if request.user != report.username and getattr(request.user, 'role', None) != 'admin':
            return Response({"status": 403, "message": "You are not allowed to access this report"}, status=403)

        if not report.link:
            return Response({"status": 400, "message": "Report link not available"}, status=400)

        # Build the local file path from stored link
        # If you store only relative path like 'reports/myfile.pdf'
        if report.link.startswith("http"):
            # If you stored a full URL, return it as normal
            return Response({
                "status": 200,
                "message": "Report link retrieved",
                "data": {
                    "id": report.id,
                    "type": report.type,
                    "format": report.format,
                    "link": report.link
                }
            })

        file_path = os.path.join(settings.MEDIA_ROOT, report.link)

        if not os.path.exists(file_path):
            raise Http404("File not found")

        # Send the file as download
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))