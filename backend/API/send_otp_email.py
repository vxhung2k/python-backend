from django.core.mail import send_mail
import random
from django.conf import settings
from .models import User


def send_otp_email(email):
    subject = 'Your account verification email'
    otp = random.randint(100000, 999999)
    message = f'Your otp is : {otp}'
    email_from = settings.EMAIL_HOST
    send_mail(subject, message, email_from, [email])
    user = User.objects.get(email=email)
    user.otp = otp
    user.save()

