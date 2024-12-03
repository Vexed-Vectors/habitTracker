from django.urls import path

from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),  # Home page of the base app
    path('dashboard/',views.home,name = 'dashboard'),
    path('api/login',views.login_user, name = 'login_api'),

    path('signup/', views.signup_page, name = 'signup_page'),
    path('signup/api/', views.signup_view, name='signup'),


]