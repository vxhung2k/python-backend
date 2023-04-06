from rest_framework import permissions

from .authentication import decode_token
import datetime
from .models import Admin, Staff, Customer


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        get_token = request.COOKIES.get('refresh_token')
        if get_token:
            token = decode_token(get_token)
            exp = datetime.datetime.utcfromtimestamp(token['exp'])
            admin_id = token['user_id']
            is_admin = Admin.objects.filter(user_id=admin_id).first()
            if is_admin and datetime.datetime.today() < exp:
                return True
            return False
        return False


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        get_token = request.COOKIES.get('refresh_token')
        if get_token:
            token = decode_token(get_token)
            exp = datetime.datetime.utcfromtimestamp(token['exp'])
            staff_id = token['user_id']
            is_staff = Staff.objects.filter(user_id=staff_id).first()
            if is_staff and datetime.datetime.today() < exp:
                return True
            return False
        return False


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        get_token = request.COOKIES.get('refresh_token')
        if get_token:
            token = decode_token(get_token)
            exp = datetime.datetime.utcfromtimestamp(token['exp'])
            customer_id = token['user_id']
            is_customer = Customer.objects.filter(user_id=customer_id).first()
            if is_customer and datetime.datetime.today() < exp:
                return True
            return False
        return False


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        get_token = request.COOKIES.get('refresh_token')
        if get_token:
            token = decode_token(get_token)
            exp = datetime.datetime.utcfromtimestamp(token['exp'])
            customer_id = token['user_id']
            is_customer = Customer.objects.filter(user_id=customer_id).first()
            if is_customer and datetime.datetime.today() < exp:
                return True
            return False
        return False
