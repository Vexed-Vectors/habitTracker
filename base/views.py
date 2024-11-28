from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
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

def home(request):
    return HttpResponse("hello")