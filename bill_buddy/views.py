from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .models import CustomUser,PasswordResetToken, EmailVerificationToken
from .utils import send_verification_email, send_password_reset_email
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.permissions import IsAuthenticated
from .response import custom_response
from .serializers import RegisterSerializer, PasswordResetConfirmSerializer
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return custom_response(
                success=False,
                message="Validation failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()
        send_verification_email(user, request)

        return custom_response(
            success=True,
            message="User registered successfully, Please check your email to verify your account the link will expire in 10 minutes.",
            status_code=status.HTTP_201_CREATED
        )


class EmailVerifyView(APIView):
    def get(self, request):
        token = request.query_params.get('token')
        signer = TimestampSigner()

        try:
            verification_token = EmailVerificationToken.objects.get(token=token)
        except EmailVerificationToken.DoesNotExist:
            return custom_response(
                success=False,
                message="Invalid token.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if verification_token.used:
            return custom_response(success=False, message="Token already used.")

        if verification_token.is_expired():
            return custom_response(success=False, message="Token expired.")

        try:
            email = signer.unsign(token, max_age=60 * 10)
        except (SignatureExpired, BadSignature):
            return custom_response(
                success=False,
                message="Invalid or expired token.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user = verification_token.user

        if user.email != email:
            return custom_response(success=False, message="Token does not match user.")

        if user.is_active:
            return custom_response(success=True, message="Account already activated.")

        user.is_active = True
        user.save()

        verification_token.used = True
        verification_token.save()

        return custom_response(success=True, message="Email verified successfully. You can now log in.")


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return custom_response(
                success=False,
                message="Email and password required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, email=email, password=password)

        if user is None:
            return custom_response(
                success=False,
                message="Invalid credentials",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return custom_response(
                success=False,
                message="Account not activated. Please verify your email.",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return custom_response(
            success=True,
            message="Login successful",
            data={
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "gender": user.gender,
                }
            }
        )


class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return custom_response(
                success=False,
                message="Email is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return custom_response(
                success=False,
                message="User with this email does not exist",
                status_code=status.HTTP_404_NOT_FOUND
            )

        send_password_reset_email(user, request)
        return custom_response(
            success=True,
            message="Password reset request sent. Please check your email the link will expire in 10 minutes."
        )

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            reset_token = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return custom_response(success=False, message="Invalid token", status_code=400)

        if reset_token.used:
            return custom_response(success=False, message="Token already used", status_code=400)

        if reset_token.is_expired():
            return custom_response(success=False, message="Token expired", status_code=400)

        user = reset_token.user
        user.set_password(new_password)
        user.save()

        reset_token.used = True
        reset_token.save()

        return custom_response(success=True, message="Password reset successful")

class ResendVerificationEmailView(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return custom_response(
                success=False,
                message="Email is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return custom_response(
                success=False,
                message="User with this email does not exist",
                status_code=status.HTTP_404_NOT_FOUND
            )

        if user.is_active:
            return custom_response(
                success=False,
                message="Account is already verified.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        send_verification_email(user, request)
        return custom_response(
            success=True,
            message="Verification email resent. Please check your inbox the link will expire in 10 minutes."
        )


class ResendPasswordResetEmailView(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return custom_response(
                success=False,
                message="Email is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return custom_response(
                success=False,
                message="User with this email does not exist",
                status_code=status.HTTP_404_NOT_FOUND
            )

        send_password_reset_email(user, request)
        return custom_response(
            success=True,
            message="Password reset email resent. Please check your inbox the link will expire in 10 minutes."
        )

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return custom_response(
                success=False,
                message="Refresh token is required.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return custom_response(
                success=True,
                message="Logout successful."
            )

        except TokenError:
            return custom_response(
                success=False,
                message="Invalid or expired refresh token.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
