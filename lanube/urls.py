"""
URL configuration for lanube project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.views import views
from core.views import ChangePassword
from core.views.CustomLoginView import CustomLoginView  

urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('comingsoon/', views.coming_soon, name='coming-soon'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('sonar/', include('django_sonar.urls')),
    path('password/cambiar',ChangePassword.change_password,name="cambiar_password"),
    path('password/resetear', ChangePassword.reset_password, name='resetear_password'),
    path("get-security-question/", ChangePassword.get_security_question, name="get-security-question"),
]

handler404 = 'core.views.views.error_404_view'
