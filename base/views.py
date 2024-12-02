from django.forms import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token
from django.core.validators import validate_email
import json

from base.models import CustomUser

@require_http_methods(["GET"])
def login_page(request):
    """
    Render the login page
    """
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Pass CSRF token to the template
    return render(request, 'base/login.html', {'csrf_token': get_token(request)})

@csrf_protect
@require_http_methods(["POST"])
def login_user(request):
    """
    Handle user login via JSON request
    """
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
 
        email = data.get('email')
        password = data.get('password')
        print(email)
        print(password)

        # Validate input
        if not email or not password:
            return JsonResponse({
                'error': 'Email and password are required'
            }, status=400)

        # Authenticate user
        # user = authenticate(request, username=email, password=password)

        try:
            # Fetch the user by email
            user = CustomUser.objects.get(email=email)
            
            # Check if the user is active
            if not user.is_active:
                return JsonResponse({
                    'error': 'Account is not active'
                }, status=403)

            # Verify the password
            if user.check_password(password):
                # Successfully authenticated
                login(request, user)
                return JsonResponse({
                    'message': 'Login successful',
                    'user_id': str(user.id),
                    'email': user.email
                }, status=200)
            else:
                # Incorrect password
                return JsonResponse({
                    'error': 'Invalid email or password'
                }, status=401)

        except CustomUser.DoesNotExist:
            # User not found
            return JsonResponse({
                'error': 'Invalid email or password'
            }, status=401)

    except json.JSONDecodeError:
        # Invalid JSON
        return JsonResponse({
            'error': 'Invalid JSON format'
        }, status=400)

    except Exception as e:
        # Unexpected error
        return JsonResponse({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }, status=500)

@require_http_methods(["GET"])
def logout_user(request):
    """
    Handle user logout
    """
    logout(request)
    return redirect('')

@require_http_methods(["GET"])
def signup_page(request):
    """
    Render the signup page
    
    This view handles displaying the signup form to the user.
    It checks if the user is already authenticated and redirects 
    if necessary.

    Args:
        request (HttpRequest): The incoming HTTP request

    Returns:
        HttpResponse: Rendered signup page or redirect
    """
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')  # Adjust to your dashboard URL name
    
    # Render the signup template
    return render(request, 'base/signup.html',{'csrf_token': get_token(request)})


@csrf_protect
@require_POST
def signup_view(request):
    try:
        # Parse the JSON data from the request body
        data = json.loads(request.body)
        email = data.get('email')  # Changed from username
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        print("HEY")

        # Validate inputs
        errors = {}

        # Email validation
        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = 'Invalid email address'

        # Password validation
        if not password:
            errors['password'] = 'Password is required'
        elif len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters long'
        
        # Password confirmation
        if password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match'

        # Check for existing user
        if CustomUser.objects.filter(email=email).exists():
            errors['email'] = 'Email already in use'

        # If there are any errors, return them
        if errors:
            return JsonResponse({'errors': errors}, status=400)

        # Create the user
        try:
            user = CustomUser.objects.create_user(
                email=email, 
                password=password
            )
            
            # Optional: Automatically log in the user after signup
            login(request, user)

            return JsonResponse({
                'message': 'Signup successful',
                'user_id': str(user.id),
                'email': user.email
            }, status=201)

        except Exception as e:
            return JsonResponse({
                'error': 'Failed to create user',
                'details': str(e)
            }, status=500)

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON format'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }, status=500)

def home(request):
    return HttpResponse("hello")