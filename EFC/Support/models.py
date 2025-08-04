from django.db import models
from Accounts.models import CustomerProfile
from Booking.models import ServiceBook

class Complaint(models.Model):
    order = models.ForeignKey(ServiceBook, on_delete=models.CASCADE, related_name='complaints')
    user = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='complaints')
    category = models.CharField(max_length=50)  # e.g., late, fraud, price, misbehavior
    description = models.TextField()
    attachment = models.ImageField(upload_to='complaints/', blank=True, null=True)
    status = models.CharField(max_length=20, default='open')  # open, in progress, resolved
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_complaints')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Complaint #{self.id} by {self.user.username}"


class Notification(models.Model):
    user = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    electrician = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='tech_notifications')
    recipient_type = models.CharField(max_length=20)  # admin, user, electrician
    title = models.CharField(max_length=100)
    message = models.TextField()
    type = models.CharField(max_length=30)  # booking, payment, profile, wallet, complaint, arrival, etc.
    channel = models.CharField(max_length=20)  # app, email, sms
    is_sent = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"To {self.recipient_type} - {self.title}"
