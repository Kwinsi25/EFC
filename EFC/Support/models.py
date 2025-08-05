from django.db import models
from Accounts.models import CustomerProfile
from Booking.models import ServiceBook

class Complaint(models.Model):
    COMPLAINT_STATUS_CHOICES = [
    ('open', 'Open'),
    ('in_progress', 'In Progress'),
    ('resolved', 'Resolved'),
]

    order = models.ForeignKey(ServiceBook, on_delete=models.CASCADE, related_name='complaints')
    user = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='complaints')
    category = models.CharField(max_length=100, blank=False, null=False)  # e.g., late, fraud, price, misbehavior
    description = models.TextField(blank=False, null=False)
    attachment = models.ImageField(upload_to='complaints/', blank=True, null=True)
    status = models.CharField(max_length=20, default='open', choices=COMPLAINT_STATUS_CHOICES,blank=False, null=False)  # open, in progress, resolved
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_complaints')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Complaint #{self.id} by {self.user.username}"


class Notification(models.Model):
    RECIPIENT_TYPE_CHOICES = [
    ('admin', 'Admin'),
    ('user', 'User'),
    ('electrician', 'Electrician'),
    ]
    NOTIFICATION_CHANNEL_CHOICES = [
    ('app', 'App'),
    ('email', 'Email'),
    ('sms', 'SMS'),
    ]
    NOTIFICATION_TYPE_CHOICES = [
    ('booking', 'Booking'),
    ('payment', 'Payment'),
    ('profile', 'Profile'),
    ('wallet', 'Wallet'),
    ('complaint', 'Complaint'),
    ('arrival', 'Arrival'),
    ]

    user = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    electrician = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='tech_notifications')
    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_TYPE_CHOICES,blank=False, null=False, default='user')  # admin, user, electrician
    title = models.CharField(max_length=100, blank=False, null=False)
    message = models.TextField(blank=False, null=False)
    type = models.CharField(max_length=50,choices=NOTIFICATION_TYPE_CHOICES ,blank=False, null=False)# booking, payment, profile, wallet, complaint, arrival, etc.
    channel = models.CharField(max_length=20, blank=False, choices=NOTIFICATION_CHANNEL_CHOICES,null=False, default='app')  # app, email, sms
    is_sent = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"To {self.recipient_type} - {self.title}"
