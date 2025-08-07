# Accounts/custom_auth.py

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from Accounts.models import CustomerProfile

class CustomerJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")

        if user_id is None:
            raise AuthenticationFailed("Token contained no recognizable user identification")

        try:
            user = CustomerProfile.objects.get(id=user_id)
            user.is_authenticated = True  # ✅ Add this line manually
            return user
        except CustomerProfile.DoesNotExist:
            raise AuthenticationFailed("User not found")
