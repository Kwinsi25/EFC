from django.urls import path
from .views import *

urlpatterns = [
    path("all-system-logs/", AllSystemLogsView.as_view(), name="all-system-logs"),
]
