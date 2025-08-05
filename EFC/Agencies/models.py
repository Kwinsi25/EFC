from django.db import models
from Accounts.models import CustomerProfile
from Booking.models import ServiceBook

class ServiceBroadcastRequest(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('accept', 'Accepted'),
        ('ignore', 'Ignored'),
        ('expire', 'Expired'),
    ]
    order = models.ForeignKey(ServiceBook, on_delete=models.CASCADE, related_name='broadcast_requests')
    electrician = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='received_broadcasts')
    distance_km = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Broadcast to {self.electrician} for Order #{self.order.id} - {self.status}"
