import datetime
import jwt
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


def create_access_token(user_id):
    return jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        'iat': datetime.datetime.utcnow()
    }, 'django-insecure-$$a@#ms1$x^sg)j0r@==034*r34ziu1iug%bhxf1z0^imc4f7-', algorithm='HS256')


def create_refresh_token(user_id):
    return jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow()
    }, 'django-insecure-$$a@#ms1$x^sg)j0r@==034*r34ziu1iug%bhxf1z0^imc4f7-', algorithm='HS256')


def decode_token(token):
    return jwt.decode(jwt=token, key='django-insecure-$$a@#ms1$x^sg)j0r@==034*r34ziu1iug%bhxf1z0^imc4f7-',
                      algorithms='HS256')


def create_jwt_pair_for_user(user: User):
    refresh = RefreshToken.for_user(user)

    tokens = {"access": str(refresh.access_token), "refresh": str(refresh)}

    return tokens


def permission(user_id):
    user = User.objects.get(user_id=user_id)
    permission_admin = ['create_user', 'delete_user', 'update_user', 'get_user', 'create_product', 'delete_product',
                        'update_product', 'get_product']
    permission_staff = ['create_user', 'delete_user', 'update_user', 'get_user', 'update_product', 'get_product']
    permission_customer = ['update_user', 'get_product']
    if user.userType == 'admin':
        return permission_admin
    elif user.userType == 'staff':
        return permission_staff
    else:
        return permission_customer
