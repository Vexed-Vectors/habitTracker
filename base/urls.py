from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),  # Home page of the base app
    path('dashboard/',views.home,name = 'dashboard'),
    path('api/login',views.login_user, name = 'login_api'),


    # path('signup/', views.signup_view, name='signup'),
    # path('about/', views.about, name='about'),  # About page
]