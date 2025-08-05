from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'mobile', 'role']
    search_fields = ['username', 'email', 'mobile']
    list_filter = ['role']
    
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'address', 'city', 'state', 'pincode', 'is_default']
    search_fields = ['username__username', 'address', 'city']
    list_filter = ['is_default', 'city', 'state']