from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from fashflix import views
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/setup", views.setup, name="setup"),
    path("api/get_recommendations", views.get_recommendations, name="get_recommendations"),
    path("api/ratings", views.ratings, name="ratings"),
    path("api/guest", views.guest_account, name="guest_account"),
    path("api/authenticate_token", views.authenticate_token, name="authenticate_token"),
]
