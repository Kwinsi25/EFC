from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from .utils import send_email_notification, send_sms_notification
from Accounts.models import *
from rest_framework import generics, permissions
# Create your views here.

class SendNotificationView(APIView):
    def post(self, request):
        notifications_data = request.data
        if not isinstance(notifications_data, list):
            notifications_data = [notifications_data]  # Wrap in list if single

        created_notifications = []

        for notif_data in notifications_data:
            serializer = NotificationSerializer(data=notif_data, context={'request': request})
            if serializer.is_valid():
                notification = serializer.save(is_sent=True)

                # Send based on channel
                if notification.channel == 'email' and notification.user:
                    send_email_notification(notification.title, notification.message, notification.user.email)
                elif notification.channel == 'email' and notification.electrician:
                    send_email_notification(notification.title, notification.message, notification.electrician.email)
                elif notification.channel == 'sms' and notification.user:
                    send_sms_notification(notification.user.phone_number, notification.message)
                elif notification.channel == 'sms' and notification.electrician:
                    send_sms_notification(notification.electrician.phone_number, notification.message)

                created_notifications.append(notification)
            else:
                return Response({
                    "status": 400,
                    "message": "Invalid data",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": 201,
            "message": "Notifications sent successfully",
            "data": NotificationSerializer(created_notifications, many=True).data
        }, status=status.HTTP_201_CREATED)
    

# User complaint create/list (only their own)
class ComplaintListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ComplaintSerializer

    def get_queryset(self):
        return Complaint.objects.filter(user=self.request.user).order_by('-created_date')

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "status": response.status_code,
            "success": True,
            "message": "Complaint created successfully",
            "data": response.data,
            "errors": None
        }, status=response.status_code)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            "status": response.status_code,
            "success": True,
            "message": "Complaints fetched successfully",
            "data": response.data,
            "errors": None
        }, status=response.status_code)


# Admin complaint list
class ComplaintAdminListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ComplaintSerializer
    queryset = Complaint.objects.all().order_by('-created_date')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            "status": response.status_code,
            "success": True,
            "message": "All complaints fetched successfully",
            "data": response.data,
            "errors": None
        }, status=response.status_code)


# Admin update complaint status
class ComplaintUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Complaint.objects.all()
    serializer_class = ComplaintUpdateSerializer

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "status": response.status_code,
            "success": True,
            "message": "Complaint updated successfully",
            "data": response.data,
            "errors": None
        }, status=response.status_code)