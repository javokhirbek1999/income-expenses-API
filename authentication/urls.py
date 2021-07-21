from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,)

from .views import RegisterView,VerifyEmail,LoginAPIView, RequestPasswordResetEmail, PasswordTokenCheckAPI,SetNewPasswordAPI, LogoutAPIView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('email_verify/', VerifyEmail.as_view(), name='email_verify'),
    path('token/refresh/', TokenRefreshView.as_view(),name='token-refresh'),
    path('request-reset-email/', RequestPasswordResetEmail.as_view(),name='request-reset-email'),
    path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(),name='password-reset-confirm'),
    path('password-rest-complete/',SetNewPasswordAPI.as_view(),name='password-reset-coomplete'),
]