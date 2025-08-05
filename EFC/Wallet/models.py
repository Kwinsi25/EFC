from django.db import models
from Accounts.models import CustomerProfile
from Booking.models import ServiceBook

class WalletTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('received', 'Received'),
        ('withdraw', 'Withdraw'),
        ('deduct', 'Deduct'),
    ]

    WITHDRAW_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('complete', 'Complete'),
    ]

    user = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='wallet_transactions')
    is_platform = models.BooleanField(default=False)  # True = platform income/expense
    is_withdraw_request = models.BooleanField(default=False)
    withdraw_status = models.CharField(max_length=20,
        choices=WITHDRAW_STATUS_CHOICES,
        blank=True,
        null=True,
        default='pending')  # pending, approved, rejected
    approved_by_admin = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='wallet_approvals')
    approved_at = models.DateTimeField(blank=True, null=True)
    order = models.ForeignKey(ServiceBook, on_delete=models.SET_NULL, null=True, blank=True, related_name='wallet_transactions')
    amount = models.FloatField(default=0.0)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    source = models.CharField(max_length=50, blank=True, null=True)
    remarks = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    balance_after = models.FloatField(default=0)
    is_negative_triggered = models.BooleanField(default=False)
    admin_action_by = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='wallet_manual_actions')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.type} - ₹{self.amount}"


class EarningsSummary(models.Model):
    user = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='daily_earnings')
    total = models.FloatField(default=0)
    completed_job = models.IntegerField(default=0)
    created_date = models.DateTimeField()  # Date for which summary is recorded
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - ₹{self.total} on {self.created_date.date()}"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('UPI', 'UPI'),
        ('COD', 'Cash on Delivery'),
        ('Card', 'Card'),
        ('Netbanking', 'Netbanking'),
    ]

    RECEIVED_BY_CHOICES = [
        ('platform', 'Platform'),
        ('technician_qr', 'Technician QR'),
    ]

    order = models.ForeignKey(ServiceBook, on_delete=models.CASCADE, related_name='payments')
    amount = models.FloatField(default=0)
    upi = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='COD')
    received_by = models.CharField(max_length=50, choices=RECEIVED_BY_CHOICES, default='platform')
    bill_requested = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment ₹{self.amount} for Order #{self.order.id}"
