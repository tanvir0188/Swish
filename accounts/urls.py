from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    path('register', views.RegisterView.as_view(), name='register'),
    path('otp', views.forget_password_otp, name='forget_password_otp'),
    path('otp-verificaiton', views.VerifyOTPView.as_view(), name='otp_verify'),
    path('change-password', views.ChangePasswordAPIView.as_view(), name='change_password'),

    path('pre-subscription', views.SubscribeView.as_view(), name='pre_subscription'),

    path('profile', views.ProfileAPIView.as_view(), name='profile'),

    path('logout', views.LogoutAPIView.as_view(), name='logout'),
]