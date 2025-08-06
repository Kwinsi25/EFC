from rest_framework import serializers
from Accounts.models import CustomerProfile
from Accounts.models import Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id',
            'label',
            'address',
            'city',
            'state',
            'pincode',
            'is_default',
            'created_date',
            'updated_date'
        ]


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = [
            'id', 'username', 'email', 'mobile', 'role',
            'experience_year', 'service_skill', 'service_km',
            'document_type', 'document_file',
            'is_gov_verified', 'is_police_verified', 'is_admin_verified',
            'is_verified', 'wallet_balance', 'is_blocked', 'blocked_reason',
            'profile_image', 'created_date', 'updated_date'
        ]


