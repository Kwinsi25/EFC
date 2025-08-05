from rest_framework import serializers
from .models import *
from Services.models import *

class ServiceCartSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = ServiceCart
        fields = [
            'id', 'service', 'service_name', 'qty', 'num_of_tech',
            'price', 'total_price', 'status'
        ]


class CartSerializer(serializers.ModelSerializer):
    services = ServiceCartSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'services', 'created_date', 'updated_date']
    
class BookingListSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name')
    image = serializers.SerializerMethodField()

    class Meta:
        model = ServiceBook
        fields = ['id', 'service_name', 'status', 'technician_required', 'created_date', 'image']

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.service.cover_image and request:
            return request.build_absolute_uri(obj.service.cover_image.url)
        return None
    
class OrderHistorySerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    category_name = serializers.CharField(source='service.category.category_name', read_only=True)
    technician_name = serializers.CharField(source='assigned_technician.username', read_only=True)

    class Meta:
        model = ServiceBook
        fields = [
            'id', 'status', 'scheduled_date_time', 'service_name',
            'category_name', 'technician_name', 'comment',
            'is_bill_generated', 'pdf_url'
        ]
