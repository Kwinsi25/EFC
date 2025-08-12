from django.urls import path
from .views import *

urlpatterns = [
    path('notifications/send/', SendNotificationView.as_view(), name='send-notification'),
    path('complaints/', ComplaintListCreateView.as_view(), name='complaint-list-create'),
    path('admin/complaints/', ComplaintAdminListView.as_view(), name='complaint-admin-list'),
    path('admin/complaints/<int:pk>/update/', ComplaintUpdateView.as_view(), name='complaint-update'),
]
