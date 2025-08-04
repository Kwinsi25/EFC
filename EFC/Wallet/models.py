from django.db import models
from Accounts.models import CustomerProfile
from Booking.models import ServiceBook

class WalletTransaction(models.Model):
    user = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='wallet_transactions')
    is_platform = models.BooleanField(default=False)  # True = platform income/expense
    is_withdraw_request = models.BooleanField(default=False)
    withdraw_status = models.CharField(max_length=20, blank=True, null=True)  # pending, approved, rejected
    approved_by_admin = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='wallet_approvals')
    approved_at = models.DateTimeField(blank=True, null=True)
    order = models.ForeignKey(ServiceBook, on_delete=models.SET_NULL, null=True, blank=True, related_name='wallet_transactions')
    amount = models.FloatField()
    type = models.CharField(max_length=20)  # received, withdraw, deduct
    source = models.CharField(max_length=100)  # job, QR, penalty, manual, etc.
    remarks = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20)  # pending, complete
    balance_after = models.FloatField()
    is_negative_triggered = models.BooleanField(default=False)
    admin_action_by = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='wallet_manual_actions')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.type} - ₹{self.amount}"


class EarningsSummary(models.Model):
    user = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='daily_earnings')
    total = models.FloatField()
    completed_job = models.IntegerField()
    created_date = models.DateTimeField()  # Date for which summary is recorded
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - ₹{self.total} on {self.created_date.date()}"


class Payment(models.Model):
    order = models.ForeignKey(ServiceBook, on_delete=models.CASCADE, related_name='payments')
    amount = models.FloatField()
    upi = models.CharField(max_length=100)
    status = models.CharField(max_length=20)  # pending, paid, failed
    method = models.CharField(max_length=30)  # UPI, COD, Card, Netbanking
    received_by = models.CharField(max_length=50)  # platform or technician QR
    bill_requested = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment ₹{self.amount} for Order #{self.order.id}"
