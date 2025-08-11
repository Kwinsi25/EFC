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
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import RefreshToken
import re
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Temporary OTP store (for demo only, in production use DB or cache)
OTP_STORE = {}
class RegisterAPIView(APIView):
    """
    Step 1: Accept user details, validate, generate OTP, and store temporarily.
    """
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            mobile_key = serializer.validated_data['country_code'] + serializer.validated_data['mobile']

            # Generate OTP
            otp = str(random.randint(100000, 999999))
            OTP_STORE[mobile_key] = {
                "otp": otp,
                "data": serializer.validated_data,
                "expires_at": datetime.now() + timedelta(minutes=5)
            }

            return Response({
                "status": 200,
                "message": "OTP sent successfully",
                "otp": otp  # ⚠️ Remove in production
            })

        return Response({
            "status": 400,
            "message": "Invalid data",
            "errors": serializer.errors
        }, status=400)

class VerifyRegisterOTPAPIView(APIView):
    """
    Step 2: Verify OTP and create the user.
    """
    def post(self, request):
        country_code = request.data.get('country_code')
        mobile = request.data.get('mobile')
        otp_provided = request.data.get('otp')

        if not country_code or not mobile or not otp_provided:
            return Response({"status": 400, "message": "country_code, mobile, and otp are required"}, status=400)

        mobile_key = country_code + mobile
        otp_data = OTP_STORE.get(mobile_key)

        if not otp_data:
            return Response({"status": 400, "message": "OTP not found or expired"}, status=400)

        if datetime.now() > otp_data["expires_at"]:
            OTP_STORE.pop(mobile_key, None)
            return Response({"status": 400, "message": "OTP expired"}, status=400)

        if otp_provided != otp_data["otp"]:
            return Response({"status": 400, "message": "Invalid OTP"}, status=400)

        # Create user
        user = CustomerProfile.objects.create(**otp_data["data"])
        OTP_STORE.pop(mobile_key, None)  # cleanup

        return Response({
            "status": 201,
            "message": "User registered successfully",
            "data": RegisterSerializer(user).data
        }, status=201)

#Login API
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Store pending logins temporarily
LOGIN_OTP_STORE = {}

class LoginSendOTPView(APIView):
    """Step 1: Send OTP to user."""
    def post(self, request):
        country_code = request.data.get("country_code")
        mobile = request.data.get("mobile")

        # Validate country code
        if not country_code or not country_code.startswith("+") or not country_code[1:].isdigit():
            return Response({"status": 400, "message": "Invalid or missing country code"}, status=400)

        # Validate mobile
        if not mobile or not re.fullmatch(r"\d{10}", mobile):
            return Response({"status": 400, "message": "Invalid or missing mobile number (must be 10 digits)"}, status=400)

        # Check if user exists
        try:
            user = CustomerProfile.objects.get(country_code=country_code, mobile=mobile)
        except CustomerProfile.DoesNotExist:
            return Response({"status": 404, "message": "User not found"}, status=404)

        # Generate OTP
        generated_otp = str(random.randint(100000, 999999))
        mobile_key = f"{country_code}{mobile}"

        LOGIN_OTP_STORE[mobile_key] = {
            "otp": generated_otp,
            "user_id": user.id
        }

        print(f"[DEBUG] OTP for {mobile_key}: {generated_otp}")

        return Response({
            "status": 200,
            "message": "OTP sent to your mobile",
            "otp": generated_otp
        }, status=200)

class LoginVerifyOTPView(APIView):
    """Step 2: Verify OTP and login."""
    def post(self, request):
        otp = request.data.get("otp")
        if not otp:
            return Response({"status": 400, "message": "OTP is required"}, status=400)

        # Find matching OTP in store
        found_key = None
        for key, data in LOGIN_OTP_STORE.items():
            if data["otp"] == otp:
                found_key = key
                break

        if not found_key:
            return Response({"status": 400, "message": "Invalid OTP"}, status=400)

        # Get user and remove OTP from store
        user_id = LOGIN_OTP_STORE.pop(found_key)["user_id"]
        user = CustomerProfile.objects.get(id=user_id)

        # Device Detection
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

        # Save login log
        SystemLog.objects.create(
            type="login",
            performed_by=user,
            remark=f"Login from {device_type} using {browser} on {os_name}"
        )

        # Generate JWT token
        tokens = get_tokens_for_user(user)

        return Response({
            "status": 200,
            "message": "Login success",
            "data": {
                "user_id": user.id,
                "country_code": user.country_code,
                "mobile": user.mobile,
                "access_token": tokens['access'],
                "refresh_token": tokens['refresh'],
                "device_type": device_type,
                "os": os_name,
                "browser": browser
            }
        }, status=200)


#admin login view
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class AdminLoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        print(f"[DEBUG] Admin login attempt with email: {email}")
        if not email or not password:
            return Response({"status": 400, "message": "Email and password are required"}, status=400)

        # Django default User model uses username as login by default, so find user by email first
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"status": 401, "message": "Invalid credentials"}, status=401)

        # Authenticate user by username and password (username is user.username)
        user = authenticate(username=user.username, password=password)
        if user is None:
            return Response({"status": 401, "message": "Invalid credentials"}, status=401)

        # Check if user is admin (staff or superuser)
        if not (user.is_staff or user.is_superuser):
            return Response({"status": 403, "message": "You are not authorized as admin"}, status=403)

        # Generate JWT tokens - use your existing method, assuming get_tokens_for_user(user) exists
        tokens = get_tokens_for_user(user)

        return Response({
            "status": 200,
            "message": "Admin login success",
            "data": {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "access_token": tokens['access'],
                "refresh_token": tokens['refresh'],
            }
        }, status=200)


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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user  #will now be CustomerProfile instance due to custom auth

        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            # Set existing default address to False
            if serializer.validated_data.get('is_default', False):
                Address.objects.filter(user=user).update(is_default=False)

            serializer.save(user=user)
            return Response({
                "status": 200,
                "message": "Address added successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": 400,
            "message": "Invalid data",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
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
    permission_classes = [IsAuthenticated]

    def patch(self, request, address_id):
        address = get_object_or_404(Address, id=address_id)

        # nsure the logged-in user owns this address
        if address.user != request.user:
            return Response({
                "status": 403,
                "message": "You do not have permission to edit this address.",
                "data": {}
            }, status=403)

        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            if serializer.validated_data.get('is_default', False):
                Address.objects.filter(user=request.user).exclude(id=address.id).update(is_default=False)

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

