"""
URL configuration for demopro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from .views import (
    login, register, home,
    edit_user, delete_user,
    loan_prediction_view,   
    dashboard, history,
    users_list,             
)

from demoapp import views

urlpatterns = [
    path('',views.login,name='login'),
    path('register/',views.register,name='register'),
    path('home/',views.home,name='home'),
    path('logout/',views.logout,name='logout'),
    path('edit-user/<int:id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:id>/', views.delete_user, name='delete_user'),
    path("loan-prediction/", loan_prediction_view, name="loan_prediction"),
    path("users/", users_list, name="users_list"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('history/', views.history, name='history'),

]
