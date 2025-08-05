from rest_framework import serializers
from .models import *
from Booking.models import ServiceBook


class CategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id', 'category_name', 'image', 'image_url', 'created_date', 'updated_date']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url
        return None

class SubCategorySerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = [
            'id', 'name', 'category', 'description', 'cover_image', 'image',
            'section', 'steps', 'faqs', 'price', 'created_date', 'updated_date',
            'cover_image_url', 'image_url'
        ]

    def get_cover_image_url(self, obj):
        request = self.context.get('request')
        if obj.cover_image and request:
            return request.build_absolute_uri(obj.cover_image.url)
        elif obj.cover_image:
            return obj.cover_image.url
        return None

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url
        return None
    
class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = '__all__'

class ServiceCardSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'price', 'short_description', 'image_url', 'average_rating', 'review_count']

    def get_average_rating(self, obj):
        reviews = ReviewRating.objects.filter(service=obj, is_approved=True)
        if reviews.exists():
            return round(sum([r.rating for r in reviews]) / reviews.count(), 1)
        return 0.0

    def get_review_count(self, obj):
        return ReviewRating.objects.filter(service=obj, is_approved=True).count()

    def get_short_description(self, obj):
        return obj.description[:100] + "..." if obj.description else ""

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class ReviewRatingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = ReviewRating
        fields = ['username', 'rating', 'description', 'after_service_photo', 'created_date']

class AfterServicePhotoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewRating
        fields = ['after_service_photo']


class SubmitReviewRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewRating
        fields = ['service', 'electrician', 'rating', 'description', 'after_service_photo']



