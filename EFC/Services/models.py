from django.db import models
from Accounts.models import CustomerProfile

class Category(models.Model):
    category_name = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category_name


class SubCategory(models.Model):  # This is your "Service or sub_category"
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    description = models.TextField()
    cover_image = models.ImageField(upload_to='service_covers/', blank=True, null=True)
    section = models.CharField(max_length=50)  # most, premium, new, nearby
    steps = models.TextField()
    faqs = models.TextField()
    price = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Step(models.Model):
    service = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='service_steps')
    step_number = models.IntegerField()
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service.name} - Step {self.step_number}"


class ReviewRating(models.Model):
    # REVIEW_TYPE_CHOICES = (
    #     ('user_to_electrician', 'User to Electrician'),
    #     ('electrician_to_user', 'Electrician to User'),
    # )

    # review_type = models.CharField(max_length=30, choices=REVIEW_TYPE_CHOICES)
    user = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='reviews_given')
    service = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    electrician = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews_received')
    rating = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    after_service_photo = models.ImageField(upload_to='review_photos/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    flagged_reason = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user.username}"
