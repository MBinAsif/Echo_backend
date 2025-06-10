from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
import json
from accounts.models import User 
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.validators import validate_email
from django.core.mail import EmailMessage
from django.utils import timezone
import platform

@csrf_exempt
def send_contact_admin(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            your_email = data.get('yourEmail')
            admin_email = data.get('adminEmail')

            if your_email == admin_email:
                return JsonResponse({'contact message':'Sender and receiver emails cannot be the same'}, status=400)

            

            admin_emails = User.objects.filter(email__in=[your_email, admin_email]).values_list('email', flat=True)
            if your_email not in admin_emails or admin_email not in admin_emails:
                return JsonResponse({'contact message': 'One or both emails are not registered admins.'}, status=403)

            # Define content for both emails
            email_data = [
                {
                    "recipient": your_email,
                    "subject": "Your Request Has Been Sent",
                    "message": f"Your request for Paswword Reset has been successfully sent to {admin_email}. You Will be notify automatically once it's processed along with your updated password. Plase dont share this email with any one.",
                    "image_url": "https://yourdomain.com/static/emails/your_request.jpg",
                    "is_admin": False,
                    "action_url": "",
                    "button_text": "Review Request"
                },
                {
                    "recipient": admin_email,
                    "subject": "Password Change Request",
                    "message": f"{your_email} has requested you to change the password. Please review the request.",
                    "image_url": "https://yourdomain.com/static/emails/admin_request.jpg",
                    "is_admin": True,
                    "action_url": "https://yourdomain.com/admin/review-request",
                    "button_text": "Review Request"
                }
            ]

            # Send both emails using the template
            for email in email_data:
                html_content = render_to_string("ContactAdmin.html", email)
                plain_message = strip_tags(html_content)  # Strip HTML tags for text version

                email_message = EmailMessage(
                    subject=email["subject"],
                    body=html_content,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[email["recipient"]]
                )
                email_message.content_subtype = "html"  # Send HTML email
                email_message.send()

            return JsonResponse({'contact message': 'Emails sent successfully.'}, status=200)

        except Exception as e:
            return JsonResponse({'contact message': str(e)}, status=500)

def login_email(email):
    try:
        # Get current time
        login_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

        # Get device details
        device_name = platform.node()  # Gets the device name (if available)

        # Email content
        email_data = {
            "recipient": email,
            "subject": "Login Notification",
            "message": f"You have successfully logged into your account on {login_time}. With email {email}. "
                       f"Device Name: {device_name}. "
                       "If this was not you, please change your password immediately or contact admin now!",
            "image_url": "https://yourdomain.com/static/emails/login_notification.jpg",
            "is_admin": True,
            "action_url": "https://yourdomain.com/reset-password",
            "button_text": "Contact Admin",
        }

        try:
            html_content = render_to_string("ContactAdmin.html", email_data)
            plain_message = strip_tags(html_content)  # Convert HTML to plain text

            # Send email
            email_message = EmailMessage(
                subject=email_data["subject"],
                body=html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
            )
            email_message.content_subtype = "html"  # Set content type as HTML
            email_message.send()

        except Exception as e:
            pass

    finally:
        pass


def delete_admin(email):
    try:
        # Email data
        email_data = {
            "recipient": email,
            "subject": "Your Account was Deleted Sucessfully",
            "message": (
                f"You account was successfully deleted on your account email {email}. "
                f"If this was not you, please contact admin now! "
            ),
            "image_url": "https://yourdomain.com/static/emails/login_notification.jpg",
            "is_admin": True,
            "action_url": "https://yourdomain.com/reset-password",
            "button_text": "Contact Admin",
        }

        # Attempt to send the email
        try:
            html_content = render_to_string("ContactAdmin.html", email_data)
            plain_message = strip_tags(html_content)  # Convert HTML to plain text

            email_message = EmailMessage(
                subject=email_data["subject"],
                body=html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
            )
            email_message.content_subtype = "html"  # Set content type as HTML
            email_message.send()

        except Exception as e:
            pass

    finally:
        pass


def update_loggedin_email(name, email, email_password):
    try:
        # Get current time
        login_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

        # Get device details
        device_name = platform.node()  # Gets the device name (if available)

        # Email data
        email_data = {
            "recipient": email,
            "subject": "Your Account was Updated",
            "message": (
                f"You have successfully updated your account on {login_time}. "
                f"With email {email}. "
                f"Device Name: {device_name}. "
                f"If this was not you, please contact admin now! "
                f"\n\nYour new password is: {email_password} "
                f"\nUsername: {name} "
                f"\nEmail: {email}"
            ),
            "image_url": "https://yourdomain.com/static/emails/login_notification.jpg",
            "is_admin": True,
            "action_url": "https://yourdomain.com/reset-password",
            "button_text": "Contact Admin",
        }

        # Attempt to send the email
        try:
            html_content = render_to_string("ContactAdmin.html", email_data)
            plain_message = strip_tags(html_content)  # Convert HTML to plain text

            email_message = EmailMessage(
                subject=email_data["subject"],
                body=html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
            )
            email_message.content_subtype = "html"  # Set content type as HTML
            email_message.send()

        except Exception as e:
            pass

    finally:
        pass

def create_admin(name, email, email_password):
    try:
        created_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')


        # Email data
        email_data = {
            "recipient": email,
            "subject": "You Have Been Added As Admin",
            "message": (
                f"You have successfully added as Admin your account on {created_time}. "
                f"Email {name}, "
                f"Email {email}, "
                f"Password {email_password}"
                f"It is highly recomended to change your password after login by updating your account information"
            ),
            "image_url": "https://yourdomain.com/static/emails/login_notification.jpg",
            "is_admin": True,
            "action_url": "https://yourdomain.com/reset-password",
            "button_text": "Login Now",
        }

        # Attempt to send the email
        try:
            html_content = render_to_string("ContactAdmin.html", email_data)
            plain_message = strip_tags(html_content)  # Convert HTML to plain text

            email_message = EmailMessage(
                subject=email_data["subject"],
                body=html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
            )
            email_message.content_subtype = "html"  # Set content type as HTML
            email_message.send()

        except Exception as e:
            pass

    finally:
        pass


def delete_user(email):
    try:
        # Email data
        email_data = {
            "recipient": email,
            "subject": "Your Account Is Reset",
            "message": (
                f"You account was successfully Reset on your Request, for account email {email}. "
                f"Now Register your self to the application again"
            ),
            "image_url": "https://yourdomain.com/static/emails/login_notification.jpg",
            "is_admin": False,
        }

        # Attempt to send the email
        try:
            html_content = render_to_string("ContactAdmin.html", email_data)
            plain_message = strip_tags(html_content)  # Convert HTML to plain text

            email_message = EmailMessage(
                subject=email_data["subject"],
                body=html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
            )
            email_message.content_subtype = "html"  # Set content type as HTML
            email_message.send()

        except Exception as e:
            pass

    finally:
        pass

def update_OtherUser_email(name, email, email_password):
    try:
        # Get current time
        login_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')


        # Email data
        email_data = {
            "recipient": email,
            "subject": "Your Account was Updated",
            "message": (
                f"You have successfully updated your account on your request at {login_time}. "
                f"With email {email}. "
                f"\n\nYour new password is: {email_password} "
                f"\nUsername: {name} "
                f"\nEmail: {email}"
            ),
            "image_url": "https://yourdomain.com/static/emails/login_notification.jpg",
            "is_admin": False,
        }

        # Attempt to send the email
        try:
            html_content = render_to_string("ContactAdmin.html", email_data)
            plain_message = strip_tags(html_content)  # Convert HTML to plain text

            email_message = EmailMessage(
                subject=email_data["subject"],
                body=html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
            )
            email_message.content_subtype = "html"  # Set content type as HTML
            email_message.send()

        except Exception as e:
            pass

    finally:
        pass

def create_user(name, email, email_password):
    try:
        created_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')


        # Email data
        email_data = {
            "recipient": email,
            "subject": "Wellcome To the Family",
            "message": (
                f"You have successfully added as to Echotrail Family on {created_time}. "
                f"We are here to assist you through out your journey with us"
                f"Email {name}, "
                f"Email {email}, "
                f"Password {email_password}"
                f"Since your account was created by admin. It is highly recomended to change your password after login by updating your account information"
            ),
            "image_url": "https://yourdomain.com/static/emails/login_notification.jpg",
            "is_admin": False,
        }

        # Attempt to send the email
        try:
            html_content = render_to_string("ContactAdmin.html", email_data)
            plain_message = strip_tags(html_content)  # Convert HTML to plain text

            email_message = EmailMessage(
                subject=email_data["subject"],
                body=html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
            )
            email_message.content_subtype = "html"  # Set content type as HTML
            email_message.send()

        except Exception as e:
            pass

    finally:
        pass