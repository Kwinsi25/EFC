from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('register/verify-register-otp/', VerifyRegisterOTPAPIView.as_view(), name='verify-register-otp'),
    path("login/", LoginSendOTPView.as_view(), name="otp-login"),
    path("login/verify-login-otp/", LoginVerifyOTPView.as_view(), name="verify-login-otp"),
    path('admin/login/', AdminLoginView.as_view(), name='admin-login'),
    path("device-info/", DeviceInfoView.as_view(), name="device-info"),
    path('address/add/', AddAddressView.as_view()),
    path('address/list/', ListAddressView.as_view()),
    path('address/<int:address_id>/', UpdateAddressView.as_view()),
    path('address/<int:address_id>/delete/', DeleteAddressView.as_view()),
    path("register/", CreateUserProfileView.as_view(), name="register-user"),
    path("profile/<int:user_id>/", UserDetailView.as_view(), name="user-detail"),
    
]
