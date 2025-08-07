from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from Accounts.models import CustomerProfile

def get_authenticated_admin(request):
    """
    Verifies JWT token and ensures user is an admin (CustomerProfile).
    """
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith("Bearer "):
        raise AuthenticationFailed("Missing or malformed token")

    token = auth_header.split(" ")[1]
    jwt_authenticator = JWTAuthentication()

    try:
        validated_token = jwt_authenticator.get_validated_token(token)
        user = jwt_authenticator.get_user(validated_token)

        if not isinstance(user, CustomerProfile):
            raise AuthenticationFailed("Invalid user type")

        if user.role != "admin":
            raise AuthenticationFailed("You are not authorized as admin")

        return user
    except Exception:
        raise AuthenticationFailed("Unauthorized or invalid token")
