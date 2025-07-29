from django.urls import path
from .views import (RegisterView, LoginView, EmailVerifyView, PasswordResetRequestView, PasswordResetConfirmView,
ResendVerificationEmailView, ResendPasswordResetEmailView)

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/email-verify/', EmailVerifyView.as_view(), name='email-verify'),
    path('api/password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('api/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('api/resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),
    path('api/resend-password-reset/', ResendPasswordResetEmailView.as_view(), name='resend-password-reset'),
]