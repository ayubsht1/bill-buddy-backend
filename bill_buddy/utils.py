from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings

def send_verification_email(user, request):
    from django.core.signing import TimestampSigner

    signer = TimestampSigner()
    token = signer.sign(user.email)
    verify_url = request.build_absolute_uri(reverse('email-verify') + f'?token={token}')

    subject = 'Verify Your Email - Bill Buddy'
    message = f"""
    Hi {user.first_name},

    Please verify your email by clicking the link below:

    {verify_url}

    If you did not register, please ignore this email.

    Thanks,
    Bill Buddy Team
    """

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_password_reset_email(user, request):
    from django.core.signing import TimestampSigner

    signer = TimestampSigner()
    token = signer.sign(user.email)
    reset_url = request.build_absolute_uri(reverse('password-reset-confirm') + f'?token={token}')

    subject = 'Reset Your Password - Bill Buddy'
    message = f"""
    Hi {user.first_name},

    You requested a password reset. Click the link below to reset your password:

    {reset_url}

    If you didn't request this, please ignore this email.

    Thanks,
    Bill Buddy Team
    """

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


# from django.core.mail import send_mail
# from django.conf import settings

# def send_verification_email(user, request):
#     from django.core.signing import TimestampSigner

#     signer = TimestampSigner()
#     token = signer.sign(user.email)

#     FRONTEND_URL = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
#     verify_url = f"{FRONTEND_URL}/verify-email?token={token}"

#     subject = 'Verify Your Email - Bill Buddy'
#     message = f"""
#     Hi {user.first_name},

#     Please verify your email by clicking the link below:

#     {verify_url}

#     If you did not register, please ignore this email.

#     Thanks,
#     Bill Buddy Team
#     """

#     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


# def send_password_reset_email(user):
#     signer = TimestampSigner()
#     token = signer.sign(user.email)

#     # Send the user to the frontend URL instead of backend
#     FRONTEND_URL = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
#     reset_url = f"{FRONTEND_URL}/reset-password?token={token}"

#     subject = 'Reset Your Password - Bill Buddy'
#     message = f"""
#     Hi {user.first_name},

#     You requested a password reset. Click the link below to reset your password:

#     {reset_url}

#     If you didn't request this, please ignore this email.

#     Thanks,
#     Bill Buddy Team
#     """

#     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])