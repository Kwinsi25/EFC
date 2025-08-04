from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category_name', 'created_date', 'updated_date']


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'

class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = '__all__'

class ServiceCardSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'price', 'short_description', 'average_rating', 'review_count']

    def get_average_rating(self, obj):
        reviews = ReviewRating.objects.filter(service=obj, is_approved=True)
        if reviews.exists():
            return round(sum([r.rating for r in reviews]) / reviews.count(), 1)
        return 0.0

    def get_review_count(self, obj):
        return ReviewRating.objects.filter(service=obj, is_approved=True).count()

    def get_short_description(self, obj):
        return obj.description[:100] + "..." if obj.description else ""


class ReviewRatingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = ReviewRating
        fields = ['username', 'rating', 'description', 'after_service_photo', 'created_date']