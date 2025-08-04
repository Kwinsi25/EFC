from django.urls import path
from .views import *

urlpatterns = [
    path("login/", OTPLoginView.as_view(), name="otp-login"),
    path("device-info/", DeviceInfoView.as_view(), name="device-info"),
    path('address/add/', AddAddressView.as_view()),
    path('address/list/', ListAddressView.as_view()),
    path('address/<int:address_id>/', UpdateAddressView.as_view()),
    path('address/<int:address_id>/delete/', DeleteAddressView.as_view()),
    path("register/", CreateUserProfileView.as_view(), name="register-user"),
    path("profile/<int:user_id>/", UserDetailView.as_view(), name="user-detail"),

]
