from django.db import models
from Accounts.models import CustomerProfile
from Services.models import *  

class Cart(models.Model):
    user = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='carts')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"


class ServiceCart(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed')

    ]
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='services')
    service = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    num_of_tech = models.IntegerField(default=1)
    qty = models.IntegerField(default=1)
    price = models.FloatField(default=0.0)
    total_price = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES ,default='pending')  # pending, complete
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service.name} x {self.qty}"


class ServiceBook(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assign', 'Assigned'),
        ('arriving', 'Arriving'),
        ('complete', 'Complete'),
        ('cancel', 'Cancel')

    ]
    ACTION_CHOICE = [
        ('approve', 'Approve'),
        ('reject', 'Reject')
    ]
    user = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES , default='assign')  # assigned, arriving, complete, cancel
    technician_required = models.IntegerField(default=1)
    assigned_technician = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_jobs')
    is_agency_booking = models.BooleanField(default=False)
    assigned_agency = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='agency_bookings')
    is_manual_assignment = models.BooleanField(default=False)
    assigned_by_admin = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_assigned_jobs')
    manual_assignment_reason = models.TextField(blank=True, null=True)
    manual_assignment_date = models.DateTimeField(blank=True, null=True)

    is_scheduled = models.BooleanField(default=False)
    scheduled_date_time = models.DateTimeField(blank=True, null=True)

    accept_at = models.DateTimeField(blank=True, null=True)
    arrived_at = models.DateTimeField(blank=True, null=True)

    quatation_amt = models.FloatField(default=0.0)
    otp_required = models.BooleanField(default=True)
    service_start_otp = models.CharField(max_length=6, blank=True, null=True)
    otp_generated_at = models.DateTimeField(blank=True, null=True)
    otp_verified_at = models.DateTimeField(blank=True, null=True)
    otp_verified_by = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='otp_verified_jobs')

    action = models.CharField(max_length=20, choices=ACTION_CHOICE, default='Approve')  # start, reject
    job_started_at = models.DateTimeField(blank=True, null=True)
    photo = models.ImageField(upload_to='job_photos/', blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)
    is_bill_generated = models.BooleanField(default=False)
    pdf_url = models.CharField(max_length=255, blank=True, null=True)
    is_repeated = models.BooleanField(default=False)
    triggered = models.BooleanField(default=False)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking #{self.id} by {self.user.username}"
