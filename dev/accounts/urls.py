# accounts/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [

	path('signup/', views.SignUp.as_view(), name='signup.html'),
	path('login/', auth_views.LoginView.as_view(template_name='registration/login.html')),
]
