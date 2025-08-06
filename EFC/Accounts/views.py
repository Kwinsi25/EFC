import random
from user_agents import parse
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Accounts.models import *
from Admin.models import SystemLog
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser

# #Login API
class OTPLoginView(APIView):
    """
    Login API using username, email, and mobile.

    If user details are correct:
      - An OTP is sent to the registered mobile number.
      - If OTP is provided and correct, login is successful.
      - Also detects device information (device type, OS, browser).
    """
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        mobile = request.data.get("mobile")
        otp = request.data.get("otp")

        #validate required fields
        if not (username and email and mobile):
            return Response({
                "status": 400,
                "message": "username, email, and mobile are required",
                "data": {}
            }, status=400)

        # Check if user exists#
        try:
            user = CustomerProfile.objects.get(username=username, email=email, mobile=mobile)
        except CustomerProfile.DoesNotExist:
            return Response({
                "status": 404,
                "message": "User not found",
                "data": {}
            }, status=404)

        #Device Detection
        user_agent_str = request.META.get("HTTP_USER_AGENT", "")
        user_agent = parse(user_agent_str)

        device_type = "PC"
        if user_agent.is_mobile:
            device_type = "Mobile"
        elif user_agent.is_tablet:
            device_type = "Tablet"
        elif user_agent.is_bot:
            device_type = "Bot"

        os_name = user_agent.os.family
        browser = user_agent.browser.family
        
        # Send OTP
        if not otp:
            generated_otp = str(random.randint(100000, 999999))
            cache.set(f"otp_{mobile}", generated_otp, timeout=300)  # valid 5 mins
            print(f"[DEBUG] OTP for {mobile}: {generated_otp}")
            return Response({
                "status": 200,
                "message": "OTP sent to your mobile",
                "data": {
                    "user_id": user.id,
                    "username": user.username,
                    "device_type": device_type,
                    "os": os_name,
                    "browser": browser
                }
            }, status=200)

        #Verify OTP
        cached_otp = cache.get(f"otp_{mobile}")
        if cached_otp == otp:
            cache.delete(f"otp_{mobile}")
            
            #Save login log into systemLog
            SystemLog.objects.create(
                type="login",
                performed_by=user,
                remark=f"Login from {device_type} using {browser} on {os_name}"
            )
            return Response({
                "status": 200,
                "message": "Login success",
                "data": {
                    "user_id": user.id,
                    "username": user.username,
                    "device_type": device_type,
                    "os": os_name,
                    "browser": browser
                }
            }, status=200)
        else:
            return Response({
                "status": 400,
                "message": "Invalid OTP",
                "data": {}
            }, status=400)

#device detection API(optional)
class DeviceInfoView(APIView):
    """
    API to detect device information from the User-Agent header.

    Can be used to test and view details like:
      - Device type (Mobile, Tablet, PC)
      - Operating system
      - Browser
    """
    def get(self, request):
        user_agent_str = request.META.get('HTTP_USER_AGENT', '')
        user_agent = parse(user_agent_str)

        device_type = "PC"
        if user_agent.is_mobile:
            device_type = "Mobile"
        elif user_agent.is_tablet:
            device_type = "Tablet"
        elif user_agent.is_bot:
            device_type = "Bot"

        device_info = {
            "device_type": device_type,
            "os": user_agent.os.family,
            "browser": user_agent.browser.family,
            "is_touch_capable": user_agent.is_touch_capable,
            "user_agent": user_agent_str
        }

        return Response({
            "status": 200,
            "message": "Device info detected",
            "data": device_info
        }, status=200)
        
# Add new address
class AddAddressView(APIView):
    """
    Add a new service address for a user.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')
        user = get_object_or_404(CustomerProfile, id=user_id)

        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data.get('is_default', False):
                Address.objects.filter(user=user).update(is_default=False)
            serializer.save(user=user)
            return Response({
                "status": 200,
                "message": "Address added successfully",
                "data": serializer.data
            }, status=200)

        return Response({
            "status": 400,
            "message": "Invalid data",
            "data": serializer.errors
        }, status=400)

# List addresses
class ListAddressView(APIView):
    """
    Get all saved addresses for a user.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({
                "status": 400,
                "message": "user_id is required in query parameters",
                "data": {}
            }, status=400)

        user = get_object_or_404(CustomerProfile, id=user_id)
        addresses = Address.objects.filter(user=user).order_by('-updated_date')
        serializer = AddressSerializer(addresses, many=True)
        
        return Response({
            "status": 200,
            "message": "Address list fetched successfully",
            "data": {
                "addresses": serializer.data
            }
        }, status=200)

        
# Update address
class UpdateAddressView(APIView):
    """
    Update a user's existing saved address.
    """
    permission_classes = [AllowAny]

    def patch(self, request, address_id):
        address = get_object_or_404(Address, id=address_id)
        user = address.user

        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            if serializer.validated_data.get('is_default', False):
                Address.objects.filter(user=user).exclude(id=address.id).update(is_default=False)
            serializer.save()
            return Response({
                "status": 200,
                "message": "Address updated successfully",
                "data": serializer.data
            }, status=200)
        
        return Response({
            "status": 400,
            "message": "Invalid data",
            "data": serializer.errors
        }, status=400)


# Delete address
class DeleteAddressView(APIView):
    """
    Delete a saved address by ID.
    """
    permission_classes = [AllowAny]

    def delete(self, request, address_id):
        address = get_object_or_404(Address, id=address_id)
        address.delete()
        return Response({
            "status": 200,
            "message": "Address deleted successfully",
            "data": {}
        }, status=200)


#User data saved
class CreateUserProfileView(APIView):
    """
    API to register/save a new user profile including image upload.

    - Accepts multipart/form-data.
    """

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = CustomerProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": 201,
                "message": "User created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": 400,
            "message": "Invalid data",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

#CRUD operations for CustomerProfile can be added here if needed
class UserDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, user_id):
        """
        Read/Retrieve user info by ID
        """
        user = get_object_or_404(CustomerProfile, id=user_id)
        serializer = CustomerProfileSerializer(user)
        return Response({
            "status": 200,
            "message": "User data fetched",
            "data": serializer.data
        })

    def patch(self, request, user_id):
        """
        Update user profile info
        """
        user = get_object_or_404(CustomerProfile, id=user_id)
        serializer = CustomerProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": 200,
                "message": "User profile updated",
                "data": serializer.data
            })
        return Response({
            "status": 400,
            "message": "Update failed",
            "errors": serializer.errors
        }, status=400)

    def delete(self, request, user_id):
        """
        Delete or deactivate user (soft delete recommended)
        """
        user = get_object_or_404(CustomerProfile, id=user_id)
        user.delete()  # Or set user.is_blocked = True and save()
        return Response({
            "status": 200,
            "message": "User deleted successfully"
        })

