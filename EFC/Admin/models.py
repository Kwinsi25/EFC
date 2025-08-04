from django.db import models
from Accounts.models import CustomerProfile

class ReportLog(models.Model):
    is_scheduled = models.BooleanField(default=False)
    type = models.CharField(max_length=50)  # booking, earning, etc.
    generated_by = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, related_name='reports_generated')
    export_by = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, related_name='reports_exported')
    username = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, related_name='report_recipient')
    format = models.CharField(max_length=10)  # pdf, csv
    frequency = models.CharField(max_length=20, blank=True, null=True)  # daily, weekly, monthly (only for scheduled)
    link = models.URLField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.type} report for {self.username}"


class SystemLog(models.Model):
    type = models.CharField(max_length=50)  # login, wallet_update, manual_assign, etc.
    performed_by = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True)
    remark = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.type} by {self.performed_by}"
