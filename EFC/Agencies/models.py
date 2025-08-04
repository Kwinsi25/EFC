from django.db import models
from Accounts.models import CustomerProfile
from Booking.models import ServiceBook

class ServiceBroadcastRequest(models.Model):
    order = models.ForeignKey(ServiceBook, on_delete=models.CASCADE, related_name='broadcast_requests')
    electrician = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='received_broadcasts')
    distance_km = models.FloatField()
    status = models.CharField(max_length=20)  # sent, accept, ignore, expire
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Broadcast to {self.electrician} for Order #{self.order.id} - {self.status}"
