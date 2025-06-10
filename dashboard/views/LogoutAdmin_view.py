from django.http import JsonResponse
from rest_framework.decorators import api_view
from accounts.models import User
from .utils.tokenvalidation import validate_token  # Import the validation function
from rest_framework.exceptions import AuthenticationFailed
import traceback

@api_view(["POST"])
def logout_admin(request):
    try:
        # Validate and decode token
        token = request.headers.get("Authorization")
        if not token:
            raise AuthenticationFailed("Authorization header is missing")

        refresh_token = token.split(" ")[1]  # Extract token after 'Bearer'
        payload = validate_token(refresh_token)  # Validate and extract payload
        admin_id = payload["user_id"]

        # Attempt to retrieve the admin user from the database
        try:
            admin_user = User.objects.get(id=admin_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "Admin not found"}, status=404)

        # Update admin status to inactive
        admin_user.status = "inactive"
        admin_user.save()

        return JsonResponse({"message": "Logout successful"})

    except AuthenticationFailed as e:
        return JsonResponse({"error": str(e)}, status=401)  # Handle authentication failure

    except Exception as e:
        # Log the error and send response with error details
        print("Error during logout:", traceback.format_exc())  # Logs error with traceback for better debugging
        return JsonResponse(
            {"error": "Internal Server Error", "details": str(e)}, status=500
        )
