"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from rest_framework import routers
from fashflix import views
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()
# router.register(r'register_input_image', views.InputImageView, 'register_input_image')
# router.register(r'output_image', views.OutputImageView, 'output_image')

# router.register(r'setup', views.ML.setup, 'setup')
# router.register(r'get_recommendations', views.ML.get_recommendations, 'get_recommendations')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/setup", views.setup, name="setup"),
    # path('api/get_recommendations', views.ML.get_recommendations, name='get_recommendations'),
    path("api/get_recommendations", views.get_recommendations, name="get_recommendations"),
    # path('api/', include(router.urls)),
    path("api/login", views.login, name="login"),
    path("api/sign_up", views.sign_up, name="sign_up"),
    path("api/guest", views.guest_account, name="guest_account"),
    path("api/obtain_auth_token", obtain_auth_token, name="obtain_auth_token"),
    path("api/authenticate_token", views.authenticate_token, name="authenticate_token"),
]
