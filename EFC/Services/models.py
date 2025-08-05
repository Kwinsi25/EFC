from django.db import models
from Accounts.models import CustomerProfile
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    category_name = models.CharField(max_length=100,blank=False, null=False, unique=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category_name


class SubCategory(models.Model):  # This is your "Service or sub_category"
    name = models.CharField(max_length=100,blank=False, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    description = models.TextField(blank=False, null=False)
    cover_image = models.ImageField(upload_to='service_covers/', blank=True, null=True)
    image = models.ImageField(upload_to='subcategory_image/', blank=True, null=True)
    section = models.CharField(max_length=50,blank=False, null=False)  # most, premium, new, nearby
    steps = models.TextField(blank=False, null=False)
    faqs = models.TextField(blank=False, null=False)
    price = models.CharField(max_length=50,blank=False, null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Step(models.Model):
    service = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='service_steps')
    step_number = models.IntegerField( blank=False, null=False)
    title = models.CharField(max_length=100,blank=False, null=False)
    description = models.TextField(blank=False, null=False)
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
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    after_service_photo = models.ImageField(upload_to='review_photos/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    flagged_reason = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user.username}"
