from rest_framework import serializers
from .models import *
from Accounts.models import *

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_date', 'updated_date', 'is_sent']

    # Custom validation to ensure recipient exists
    def validate(self, data):
        recipient_type = data.get('recipient_type')
        recipient_id = self.context['request'].data.get('recipient_id')

        if not recipient_id:
            raise serializers.ValidationError({"recipient_id": "Recipient ID is required."})

        try:
            recipient = CustomerProfile.objects.get(id=recipient_id)
        except CustomerProfile.DoesNotExist:
            raise serializers.ValidationError({"recipient_id": "Recipient not found."})

        if recipient_type == 'user':
            data['user'] = recipient
            data['electrician'] = None
        elif recipient_type == 'electrician':
            data['electrician'] = recipient
            data['user'] = None
        elif recipient_type == 'admin':
            data['user'] = None
            data['electrician'] = None

        return data


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = [
            'id', 'order', 'category', 'description', 'attachment',
            'status', 'is_resolved', 'resolved_by', 'created_date', 'updated_date'
        ]
        read_only_fields = ['status', 'is_resolved', 'resolved_by', 'created_date', 'updated_date']

    def create(self, validated_data):
        request = self.context['request']
        order = validated_data['order']

        # Ensure the order belongs to the logged-in user
        if order.user != request.user:
            raise serializers.ValidationError("You can only create complaints for your own orders.")

        validated_data['user'] = request.user
        return super().create(validated_data)


class ComplaintUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['status']

    def update(self, instance, validated_data):
        request = self.context['request']

        # Ensure only admin can update
        if getattr(request.user, 'role', None) != 'admin':
            raise serializers.ValidationError("Only admins can update complaints.")

        # If status is set to resolved, mark and set resolved_by
        if validated_data.get('status') == 'resolved':
            instance.is_resolved = True
            instance.resolved_by = request.user  # This is already a CustomerProfile

        return super().update(instance, validated_data)