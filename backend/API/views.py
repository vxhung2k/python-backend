import uuid

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Image, Product, Cart, Comment, Admin, Staff, Salary, Customer, OptionsProduct, DetailProduct, \
    Payment, PaymentTransaction
from .serializers import UserSerializer, LoginStatusSerializer, UserInfoSerializer, \
    UserUpdateSerializer, ProductSerializer, ProductDetailSerializer, ImageSerializer, ProductUpdateSerializer, \
    CartSerializer, CartCreateSerializer, CommentSerializer, SalarySerializer, AdminSerializer, \
    CustomerSerializer, StaffSerializer, ProductInfoSerializer, OptionsProductSerializer, UpdateSalaryStaffSerializer, \
    ListLikeSerializer, DetailProductGuarantee
from django.contrib.auth.hashers import make_password, check_password
from .utilities import password_check, checkUUID, SearchRangePrice, CheckLevelCustomer
from .authentication import create_access_token, create_refresh_token, decode_token
from django.shortcuts import get_object_or_404
from .pagination import Pagination
from .send_otp_email import *
from rest_framework.exceptions import AuthenticationFailed
from .permission import IsAdmin, IsStaff, IsCustomer
from datetime import datetime
from rest_framework.decorators import permission_classes
import pandas as pd
from django.db import transaction
from django.core.mail import send_mail


@api_view(['GET'])
def returnListProvinces(request):
    path = u'~/data_location/Provinces.xls'
    df = pd.read_excel(path)
    provinces = list(df.name.head(63))
    id_provinces = list(df.id.head(63))
    items = []
    index = 0
    while index < len(provinces):
        item = {}
        item.update({'id': id_provinces[index], 'name': provinces[index]})
        items.append(item)
        index += 1

    return Response({'payload': items, 'success': True}, status=200)


@api_view(['GET'])
def returnDistrictOfProvince(request):
    id_province = int(request.GET.get('province_id'))
    path1 = u'~/data_location/DistrictsAndWards.xls'
    path2 = u'~/data_location/Provinces.xls'
    df = pd.read_excel(path2)
    list_id_provinces = list(df.id.head(63))
    count = 0
    districts = []
    if id_province in list_id_provinces:
        df = pd.read_excel(path1)
        provinces_id = list(df.id_province)
        index_start = provinces_id.index(id_province)
        for i in provinces_id:
            if i > id_province:
                break
            count += 1
        list_district = list(df.district)
        list_id_district = list(df.id_district)
        list_id = list(sorted(set(list_id_district[index_start:count-1])))
        district = list(set(list_district[index_start: count-1]))
        district_convert = []
        index = 0
        for i in list_district[index_start:index_start + count]:
            if i in district and i not in district_convert:
                district_convert.append(i)
        while index < len(district_convert):
            item = {}
            item.update({'id': list_id[index], 'name': district_convert[index]})
            districts.append(item)
            index += 1
    else:
        districts.append({'message': 'province not exist!', 'success': False})
    return Response({'payload': districts, 'success': True}, status=200)


@api_view(['GET'])
def returnWardOfDistrict(request):
    id_district = int(request.GET.get('district_id'))
    path = u'~/data_location/DistrictsAndWards.xls'
    df = pd.read_excel(path)
    district_id = list(df.id_district)
    index_start = district_id.index(id_district)
    count = 0
    for i in district_id:
        if i > id_district:
            break
        count += 1
    list_ward = list(df.ward)
    list_id_ward = list(df.id_ward)
    list_id = list_id_ward[index_start: count]
    ward = list_ward[index_start:count]
    wards = []
    index = 0
    while index < len(ward):
        item = {}
        item.update({'id': list_id[index], 'name': ward[index]})
        wards.append(item)
        index += 1
    return Response({'payload': wards, 'success': True}, status=200)


# for DEV
@api_view(['GET'])
def GetAllUser(request):
    user = User.objects.all()
    return Response({'payload': UserInfoSerializer(user, many=True).data})


class Login(APIView):
    @classmethod
    def post(cls, request):
        data = JSONParser().parse(request)
        user = get_object_or_404(User, username=data['username'])
        if user and check_password(data['password'], user.password):
            access_token = create_access_token(str(user.user_id))
            refresh_token = create_refresh_token(str(user.user_id))
            response = Response()
            response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
            response.data = {
                'token': access_token
            }
            return response
        else:
            return Response({'errors_message': 'username or password in correct!Try again'}, status=404)


@api_view(['POST'])
@permission_classes([IsAdmin | IsCustomer | IsStaff])
def Logout(self):
    response = Response()
    response.delete_cookie(key='refresh_token')
    response.data = {
        'success': True,
        'message': 'Logout successful!'
    }
    return response


@api_view(['POST'])
@permission_classes([IsAdmin | IsStaff | IsCustomer])
def ChangePassword(request):
    data = JSONParser().parse(request)
    new_password = data['newPassword']
    password = data['password']
    otp = data['otp']
    user_info = get_object_or_404(User, username=data['username'])
    list_errors = {}
    if not check_password(password, user_info.password):
        list_errors.update({'password_error': 'password not valid!'})
    else:
        if password_check(new_password):
            update_data = {'password': make_password(new_password)}
            acc_update = LoginStatusSerializer(user_info, data=update_data, partial=True)
            if otp is not None and acc_update.is_valid():
                check_otp = user_info.otp
                if otp == check_otp:
                    acc_update.save()
                    return Response({'message': 'Change password success'}, status=200)
                raise ValueError('otp not valid')
            else:
                send_otp_email(user_info.email)
                return Response({'message': 'Please check otp send to your email'}, status=200)
        else:
            list_errors.update({'new_password_error': 'type new password not valid'})
    return Response({'message': list_errors}, status=404)


@api_view(['POST'])
@permission_classes([AllowAny])
def ResetPassword(request):
    email = request.data['email']
    otp = request.data['otp']
    password = request.data['password']
    user = get_object_or_404(User, email=email)
    if user and password_check(password):
        if otp is not None:
            user.password = make_password(password)
            user.save()
            return Response({'success': True}, status=200)
        else:
            send_otp_email(user.email)
            raise ValueError('Please check otp send to your email!')
    raise ValueError('User correct email not exist or type password not valid ')


@api_view(['GET'])
@csrf_exempt
@permission_classes([IsAdmin])
def getListUsers(request):
    users = User.objects.all()
    user_items = UserInfoSerializer(users, many=True)
    limit_page = int(request.GET.get('limit'))
    page = int(request.GET.get('page'))
    pagination = Pagination(user_items.data, page, limit_page)
    return Response({'message': 'get list user successfully!', 'payload': pagination}, status=200)


@api_view(['POST'])
# @permission_classes([IsAdmin])
def createAdmin(request):
    data = JSONParser().parse(request)
    password = data['password']
    email = User.objects.filter(email=data['email']).first()
    username = User.objects.filter(username=data['username']).first()
    phone_number = User.objects.filter(phoneNumber=data['phoneNumber'])
    list_errors = {}
    if not password_check(data['password']):
        list_errors.update({'password-errors': 'password not valid!'})
    if email:
        list_errors.update({'email-errors': 'email exist!'})
    if username:
        list_errors.update({'username-errors': 'username exist!'})
    if phone_number:
        list_errors.update({'phoneNumber-errors': 'phone number exist!'})
    if not phone_number and not email and not username and password_check(data['password']):
        data.pop('password')
        data.update({'password': make_password(password)})
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            admin = Admin.objects.create(user_id=serializer.data['user_id'])
            admin.save()
            return Response({'message': 'create success'}, status=200)
    return JsonResponse(list_errors)


@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAdmin])
def createStaff(request):
    data = JSONParser().parse(request)
    data_salary = {'basic_salary': data.pop('basic_salary')}
    password = data['password']
    email = User.objects.filter(email=data['email']).first()
    username = User.objects.filter(username=data['username']).first()
    phone_number = User.objects.filter(phoneNumber=data['phoneNumber'])
    list_errors = {}
    if not password_check(data['password']):
        list_errors.update({'password-errors': 'password not valid!'})
    if email:
        list_errors.update({'email-errors': 'email exist!'})
    if username:
        list_errors.update({'username-errors': 'username exist!'})
    if phone_number:
        list_errors.update({'phoneNumber-errors': 'phone number exist!'})
    if not phone_number and not email and not username and password_check(data['password']):
        data.pop('password')
        data.update({'password': make_password(password)})
        serializer = UserSerializer(data=data)
        serializer_salary = SalarySerializer(data=data_salary)
        if serializer.is_valid() and serializer_salary.is_valid():
            serializer.save()
            serializer_salary.save()
            admin = Staff.objects.create(user_id=serializer.data['user_id'], salary_id=serializer_salary.data['id'])
            admin.save()
            return Response({'message': 'create success'}, status=200)
        else:
            return Response({'message': 'Data not valid', 'payload': serializer_salary.errors}, status=404)
    return JsonResponse(list_errors)


@api_view(['POST'])
@permission_classes([IsStaff])
def createCustomer(request):
    data = JSONParser().parse(request)
    password = data['password']
    email = User.objects.filter(email=data['email']).first()
    username = User.objects.filter(username=data['username']).first()
    phone_number = User.objects.filter(phoneNumber=data['phoneNumber'])
    list_errors = {}
    if not password_check(data['password']):
        list_errors.update({'password-errors': 'password not valid!'})
    if email:
        list_errors.update({'email-errors': 'email exist!'})
    if username:
        list_errors.update({'username-errors': 'username exist!'})
    if phone_number:
        list_errors.update({'phoneNumber-errors': 'phone number exist!'})
    if not phone_number and not email and not username and password_check(data['password']):
        data.pop('password')
        data.update({'password': make_password(password)})
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            customer = Customer.objects.create(user_id=serializer.data['user_id'])
            cart = Cart.objects.create(customer_id=serializer.data['user_id'])
            customer.save()
            cart.save()
            return Response({'message': 'create success'}, status=200)


@api_view(['PUT'])
@permission_classes([IsStaff | IsCustomer | IsAdmin])
def UpdateBasicUserInfo(request):
    get_token = request.COOKIES.get('refresh_token')
    token = decode_token(get_token)
    customer_id = token['user_id']
    if request.data != {}:
        customer = get_object_or_404(Customer, user_id=customer_id)
    else:
        customer = get_object_or_404(Customer, user_id=request.data['customer_id'])
    return Response({'payload': CustomerSerializer(customer).data}, status=200)


@api_view(['PUT'])
@permission_classes([IsAdmin])
def UpdateSalaryStaff(request, **kwargs):
    staff_id = kwargs['staff_id']
    data = JSONParser().parse(request)
    staff = get_object_or_404(Staff, user_id=staff_id)
    salary = get_object_or_404(Salary, id=staff.salary_id)
    salary_serializer = UpdateSalaryStaffSerializer(salary, data=data, partial=True)
    if salary_serializer.is_valid():
        salary_serializer.save()
        return Response({'message': 'Update salary staff success', 'success': True}, status=200)
    else:
        return Response({'message': salary_serializer.errors}, status=404)


@api_view(['DELETE'])
@csrf_exempt
@permission_classes([IsAdmin])
def deleteUser(request):
    user_id = request.data['user_id']
    user_info = get_object_or_404(User, user_id=user_id)
    if user_info:
        user_info.delete()
        return JsonResponse({'message': 'Deleted successfully!'}, status=201)
    else:
        return JsonResponse({'message': 'User not exist!'}, status=402)


@api_view(['PUT'])
@permission_classes([IsStaff])
def UpdateCart(request):
    data = JSONParser().parse(request)
    product_id = data['product_id']
    customer_id = data['customer_id']
    Cart.objects.get(user_id=customer_id).product.add(product_id)
    product = Product.objects.get(product_id=product_id)

    data_product_quantity = {'product_quantity': product.product_quantity - 1}
    serializer = ProductUpdateSerializer(product, data=data_product_quantity, partial=True)
    customer = Customer.objects.get(user_id=customer_id)
    total_price = customer.total_money_bought + product.product_price
    data_customer = {'total_money_bought': total_price, 'level_customer': CheckLevelCustomer(total_price)}
    serializer_customer = CustomerSerializer(customer, data=data_customer, partial=True)
    if serializer.is_valid() and serializer_customer.is_valid():
        serializer.save()
        serializer_customer.save()
        return Response({'message': 'update successful!', 'success': True, 'payload': serializer.data}, status=201)
    else:
        return JsonResponse(serializer.errors, status=404)


@api_view(['GET'])
@permission_classes([IsStaff])
def CheckGuarantee(request):
    emei = request.GET.get('k')
    item = DetailProduct.objects.get(product_IMEI=emei)
    return Response({'payload': DetailProductGuarantee(item).data}, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def SearchUser(request):
    if 'q' in request.GET:
        search_text = request.GET.get('q')
        multi_search_text = Q(
            Q(fullName__icontains=search_text) | Q(address__icontains=search_text) | Q(
                phoneNumber__icontains=search_text))
        users = User.objects.filter(multi_search_text)
        if users:
            user_items = UserInfoSerializer(users, many=True)
            limit_page = int(request.GET.get('l'))
            page = int(request.GET.get('p'))
            pagination = Pagination(user_items.data, page, limit_page)
            return Response({'success': True, 'payload': pagination}, status=200)
        else:
            return Response({'message': 'not found'}, status=404)


@api_view(['GET'])
def GetProductDetail(request):
    product_id = request.GET.get('ID')
    product = get_object_or_404(Product, product_id=product_id)
    if checkUUID(product_id):
        product_info = ProductDetailSerializer(product)
        return Response({'message': 'get product success', 'payload': product_info.data}, status=200)
    else:
        return Response({'message': 'ID not valid!'}, status=404)


@api_view(['POST'])
@permission_classes([IsAdmin])
def createProduct(request):
    data = JSONParser().parse(request)
    start_date = datetime.today()
    list_option = data['options']
    list_image = data['image']
    get_token = request.COOKIES.get('refresh_token')
    if get_token:
        token = decode_token(get_token)
        exp = datetime.utcfromtimestamp(token['exp'])
        user_id = token['user_id']
        is_admin = Admin.objects.filter(user_id=user_id).first()
        if is_admin and start_date < exp:
            product = Product.objects.create(product_title=data['product_title'], product_name=data['product_name'],
                                             time_guarantee=data['time_guarantee'], manufacturer=data['manufacturer'],
                                             type_time_guarantee=data['type_time_guarantee'])
            product.save()
            if list_image is not None:
                for i in list_image:
                    image_serializer = Image.objects.create(imageID=i)
                    image_serializer.save()
                    image = ImageSerializer(image_serializer)
                    Product.objects.get(product_id=product.product_id).image.add(image.data['id'])
            if list_option is not None:
                for i in list_option:
                    option_serializer = OptionsProduct.objects.create(option=i['option'], price=i['price'])
                    option_serializer.save()
                    option = OptionsProductSerializer(option_serializer)
                    Product.objects.get(product_id=product.product_id).options.add(option.data['id'])
            get_product = get_object_or_404(Product, product_id=product.product_id)
            product_obj = ProductDetailSerializer(get_product)
            return Response({'payload': product_obj.data}, status=200)
        raise AuthenticationFailed('unAuthorization')
    raise AuthenticationFailed('unAuthorization,please login!')


@api_view(['POST'])
@permission_classes([IsCustomer])
def likeProduct(request):
    get_token = request.COOKIES.get('refresh_token')
    user_id = decode_token(get_token)['user_id']
    data = JSONParser().parse(request)
    product_id = data['product_id']
    product_obj = get_object_or_404(Product, product_id=product_id)
    if uuid.UUID(user_id) in ListLikeSerializer(product_obj).data['likes_person']:
        Product.objects.get(product_id=product_id).likes_person.remove(user_id)
        return Response({'message': 'Product is disLiked'}, status=200)
    else:
        Product.objects.get(product_id=product_id).likes_person.add(user_id)
        return Response({'message': 'Product is liked', 'user_info': user_id}, status=200)


@api_view(['DELETE'])
@permission_classes([IsAdmin])
def deleteProduct(request, **kwargs):
    product_id = kwargs['product_id']
    if checkUUID(str(product_id)):
        product_info = get_object_or_404(Product, product_id=product_id)
        if product_info:
            Product.objects.get(product_id=product_id).likes_person.all().delete()
            Product.objects.get(product_id=product_id).comments.all().delete()
            product_info.delete()
            return Response({'message': 'delete blog success', 'success': True}, status=200)
    else:
        return Response({'message': 'user_id not exist'}, status=404)


@api_view(['POST'])
@permission_classes([IsAdmin])
def RemoveImage(request):
    product_id = request.data['product_id']
    list_id = request.data['list_image_id']
    product = get_object_or_404(Product, product_id=product_id)
    if product:
        for i in list_id:
            Image.objects.get(id=i).delete()
            Product.objects.get(product_id=product_id).image.remove(i)
        return Response({'success': True}, status=200)


@api_view(['PUT'])
@permission_classes([IsAdmin])
def updateProduct(request):
    data = JSONParser().parse(request)
    product_id = request.GET.get('ID')
    option_id = data['opt_id']
    product = get_object_or_404(Product, product_id=product_id)
    if checkUUID(product_id):
        if option_id is not None and ProductDetailSerializer(product).data['options']:
            option = OptionsProduct.objects.get(id=option_id)
            quantity = data['quantity']
            data_option = {'quantity': option.quantity + quantity}
            option_serializer = OptionsProductSerializer(option, data=data_option, partial=True)
            if option_serializer.is_valid():
                option_serializer.save()
                return Response({'success': True}, status=200)
            else:
                return Response({'message': option_serializer.errors, 'success': False}, status=404)
        else:
            if data['image'] is not None:
                list_image = Image.objects.all()
                for i in data['image']:
                    if i not in list_image:
                        image = Image.objects.create(imageID=i)
                        image.save()
                        Product.objects.get(product_id=product_id).image.add(image.id)
            data.pop('image')
            data.pop('opt_id')
            product_info = ProductUpdateSerializer(product, data=data, partial=True)
            if product_info.is_valid():
                product_info.save()
                return Response({'message': 'update successful!', 'success': True}, status=200)
            else:
                return Response({'message': product_info.errors, 'success': False}, status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def SearchProduct(request):
    search = request.GET.get('key')
    multi_search_text = Q(Q(product_name__icontains=search) | Q(product_title__icontains=search))
    products = Product.objects.filter(multi_search_text)
    if products:
        products_info = ProductDetailSerializer(products, many=True)
        return Response({'success': True, 'payload': products_info.data}, status=200)
    else:
        return Response({'message': 'Not found!'}, status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def SortListProduct(request):
    # sort with datetime = createAt or-createAt
    # sort with price :(sort=2000000-30000000)
    # sort with like :(sort = like_count)
    # sort with product_price(sort = product_price)
    sort = request.GET.get('sort')
    price = request.GET.get('price')
    limit_page = int(request.GET.get('limit'))
    page = int(request.GET.get('page'))
    products = Product.objects.all()
    product_items = ProductInfoSerializer(products, many=True)
    if products:
        if sort and price:
            products_sort = products.order_by(sort)
            list_product = SearchRangePrice(products_sort, price, ProductInfoSerializer, OptionsProduct)
            if list_product:
                pagination = Pagination(list_product, page, limit_page)
                return Response({'success': True, 'payload': pagination}, status=200)
            else:
                return Response({'message': 'Data not found!'}, status=404)
        elif sort:
            products_sort = products.order_by(sort)
            product_items_sort = ProductInfoSerializer(products_sort, many=True)
            pagination = Pagination(product_items_sort.data, page, limit_page)
            return Response({'success': True, 'payload': pagination}, status=200)
        elif price:
            list_product = SearchRangePrice(products, price, ProductInfoSerializer, OptionsProduct)
            if list_product:
                pagination = Pagination(list_product, page, limit_page)
                return Response({'success': True, 'payload': pagination}, status=200)
            else:
                return Response({'message': 'Data not found!'}, status=404)
        else:
            pagination = Pagination(product_items.data, page, limit_page)
            return Response({'success': True, 'payload': pagination}, status=200)
    else:
        return Response({'message': 'List Product Empty!'}, status=404)


class CartOfCustomer(APIView):
    @classmethod
    def get(cls, request):
        get_token = request.COOKIES.get('refresh_token')
        if get_token and request.data != {}:
            customer_id = request.data['customer_id']
            token = decode_token(get_token)
            exp = datetime.utcfromtimestamp(token['exp'])
            staff_id = token['user_id']
            is_staff = Staff.objects.filter(user_id=staff_id).first()
            if is_staff and datetime.today() < exp:
                cart = get_object_or_404(Cart, customer_id=customer_id)
                return Response({'payload': CartSerializer(cart).data}, status=200)
        elif get_token:
            token = decode_token(get_token)
            exp = datetime.utcfromtimestamp(token['exp'])
            customer_id = token['user_id']
            is_customer = Customer.objects.filter(user_id=customer_id).first()
            if is_customer and datetime.today() < exp:
                cart = get_object_or_404(Cart, customer_id=customer_id)
                return Response({'payload': CartSerializer(cart).data}, status=200)
        raise AuthenticationFailed('unAuthorization, please login')

    # @classmethod
    # def put(cls, request):
    #     data = JSONParser().parse(request)
    #     item_id = request.GET.get('id')
    #     item = get_object_or_404(Cart, id=item_id)
    #     items_update = CartSerializer(item, data=data, partial=True)
    #     if items_update.is_valid():
    #         items_update.save()
    #         return Response({'success': True, 'payload': items_update.data}, status=200)
    #     else:
    #         return Response({'success': False}, status=404)

    @classmethod
    def post(cls, request):
        get_token = request.COOKIES.get('refresh_token')
        if get_token:
            customer_id = request.data['customer_id']
            product_id = request.data['product_id']
            token = decode_token(get_token)
            exp = datetime.utcfromtimestamp(token['exp'])
            staff_id = token['user_id']
            is_staff = Staff.objects.filter(user_id=staff_id).first()
            is_customer = Customer.objects.filter(user_id=customer_id).first()
            is_product = Product.objects.filter(product_id=product_id).first()
            list_errors = []
            if not is_customer:
                list_errors.append('customer not exist!')
            if not is_product:
                list_errors.append('product not exist')
            if not is_staff:
                list_errors.append('unAuthorization')
            if is_staff and datetime.today() < exp:
                Cart.objects.get(customer_id=customer_id).product.add(product_id)
                product_quantity_update = is_product.product_quantity - 1
                data = {'product_quantity': product_quantity_update}
                product = ProductSerializer(is_product, data=data, partial=True)
                if product.is_valid():
                    product.save()
                return Response({'success': True}, status=200)
            return Response({'errors': list_errors}, status=404)
        raise AuthenticationFailed('unAuthorization, please login')


@api_view(['POST'])
@permission_classes([IsCustomer])
def Comments(request, **kwargs):
    data = JSONParser().parse(request)
    parent_cmt_id = data['parent_id']
    product_id = kwargs['product_id']
    get_token = request.COOKIES.get('refresh_token')
    token = decode_token(get_token)
    user_id = token['user_id']
    if parent_cmt_id:
        cmt = Comment.objects.get(comment_id=parent_cmt_id)
        comment = Comment.objects.create(parent_id=parent_cmt_id, comment=data['comment'],
                                         user_id=user_id)
        comment.save()
        data = {'has_next_reply_cmt': True}
        cmt_obj = CommentSerializer(cmt, data=data, partial=True)
        if cmt_obj.is_valid():
            cmt_obj.save()
        return Response({'success': True}, status=200)
    else:
        comment = Comment.objects.create(comment=data['comment'], user_id=user_id)
        comment.save()
        comment_res = CommentSerializer(comment)
        Product.objects.get(product_id=product_id).comments.add(comment_res.data['comment_id'])
        return Response({'success': True}, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def GetMoreComments(request):
    data = JSONParser().parse(request)
    cmt = Comment.objects.filter(parent_id=data['parent_id'])
    list_cmt = []
    for i in cmt:
        if i.has_next_reply_cmt:
            more_cmt = Comment.objects.filter(parent_id=i.comment_id)
            data = {'comment_id': i.comment_id, 'comment': i.comment, 'user_id': i.user_id,
                    'reply_count': len(more_cmt)}
            list_cmt.append(data)
        else:
            data = {'comment_id': i.comment_id, 'comment': i.comment, 'user_id': i.user_id,
                    'reply_count': 0}
            list_cmt.append(data)
    return Response({'payload': list_cmt}, status=200)


@api_view(['GET'])
@permission_classes([IsAdmin | IsStaff | IsCustomer])
def getInformationByID(request):
    user_id = request.data['user_id']
    user = get_object_or_404(User, user_id=user_id)
    admin = Admin.objects.filter(user_id=user.user_id).first()
    staff = Staff.objects.filter(user_id=user.user_id).first()
    customer = Customer.objects.filter(user_id=user.user_id).first()
    if admin:
        return Response({'payload': AdminSerializer(admin).data}, status=200)
    elif staff:
        return Response({'payload': StaffSerializer(staff).data}, status=200)
    else:
        return Response({'payload': CustomerSerializer(customer).data}, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def FilterProduct(request):
    key_filter = request.GET.get('filter_by')
    page = int(request.GET.get('page'))
    limit = int(request.GET.get('limit'))
    products = Product.objects.filter(manufacturer=key_filter)
    if products:
        pagination = Pagination(ProductInfoSerializer(products, many=True).data, page, limit)
        return Response({'success': True, 'payload': pagination}, status=200)
    else:
        return Response({'detail': 'not found'}, status=404)


@api_view(['GET'])
@transaction.atomic()
def CreatePayment(request):
    try:
        product = Product.objects.get(product_id=request.data['product_id'])
        transaction_payment = PaymentTransaction.objects.create()
        email_body = f'Thank you for your payment of {product.product_price} for {product.name}!'
        transaction.commit(
            lambda: send_mail('Email confirmation', email_body, 'vxhung2k@gmail.com', [request.data['email']]))
    except Exception as e:
        transaction.set_rollback(True)
        raise e
