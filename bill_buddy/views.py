from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .models import CustomUser
from .utils import send_verification_email, send_password_reset_email
from rest_framework_simplejwt.tokens import RefreshToken
from .response import custom_response

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        password = data.get('password')
        gender = data.get('gender', '')

        if not email or not first_name or not last_name or not password or not gender:
            return custom_response(
                success=False,
                message="Please provide email, first_name, last_name, password and gender",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if CustomUser.objects.filter(email=email).exists():
            return custom_response(
                success=False,
                message="User with this email already exists",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            is_active=False
        )

        send_verification_email(user, request)

        return custom_response(
            success=True,
            message="User registered successfully. Please check your email to verify your account.",
            status_code=status.HTTP_201_CREATED
        )


class EmailVerifyView(APIView):
    def get(self, request):
        token = request.query_params.get('token')
        from django.core.signing import TimestampSigner, SignatureExpired, BadSignature

        signer = TimestampSigner()
        try:
            email = signer.unsign(token, max_age=60*60*24)
        except (SignatureExpired, BadSignature):
            return custom_response(
                success=False,
                message="Invalid or expired token.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return custom_response(
                success=False,
                message="User not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        if user.is_active:
            return custom_response(success=True, message="Account already activated.")

        user.is_active = True
        user.save()

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
            message="Password reset request sent. Please check your email."
        )

from rest_framework import serializers
class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=6)


class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
        signer = TimestampSigner()

        try:
            email = signer.unsign(token, max_age=60*60*24)
        except (SignatureExpired, BadSignature):
            return custom_response(
                success=False,
                message="Invalid or expired token.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return custom_response(
                success=False,
                message="User not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        user.set_password(new_password)
        user.save()

        return custom_response(
            success=True,
            message="Password reset successful. You can now log in with the new password."
        )

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
            message="Verification email resent. Please check your inbox."
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
            message="Password reset email resent. Please check your inbox."
        )
