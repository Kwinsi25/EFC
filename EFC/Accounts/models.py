from django.db import models

class CustomerProfile(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=12, unique=True)
    role = models.CharField(max_length=20)  # user, electrician, agency, admin
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    experience_year = models.IntegerField(blank=True, null=True)
    service_skill = models.TextField(blank=True, null=True)
    service_km = models.IntegerField(blank=True, null=True)
    document_type = models.CharField(max_length=20, blank=True, null=True)
    document_file = models.FileField(upload_to='documents/', blank=True, null=True)
    is_gov_verified = models.BooleanField(default=False)
    is_police_verified = models.BooleanField(default=False)
    is_admin_verified = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    wallet_balance = models.FloatField(default=0.0)
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class Address(models.Model):
    user = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50)  # e.g. Home, Office
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    is_default = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.label} - {self.user.username}"
