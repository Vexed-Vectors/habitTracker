from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page of the base app
    # path('about/', views.about, name='about'),  # About page
]