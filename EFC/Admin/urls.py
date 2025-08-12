from django.urls import path
from .views import *

urlpatterns = [
    path("all-system-logs/", AllSystemLogsView.as_view(), name="all-system-logs"),
    path('generate-report/', ReportListCreateView.as_view(), name='report-list-create'),
    path('<int:pk>/download/', ReportDownloadView.as_view(), name='report-download'),
]
