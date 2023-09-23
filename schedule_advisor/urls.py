"""schedule_advisor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from .views import (
    search_view,
    home_view,
    class_schedule_change_view,
    schedule_view,
    advisor_view,
    advisee_change_view,
    class_schedule_visible_view,
    schedule_approval_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("search", search_view, name="search"),
    path("accounts/", include("allauth.urls")),
    path("schedule/", schedule_view, name="schedule"),
    path("schedule/update", class_schedule_change_view, name="update_schedule"),
    path("schedule/visible", class_schedule_visible_view, name="visible_schedule"),
    path("schedules", advisor_view, name="schedules"),
    path("schedules/update", advisee_change_view, name="update_advisees"),
    path("schedules/approve", schedule_approval_view, name="approve_schedule"),
]
