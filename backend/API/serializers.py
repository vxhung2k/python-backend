from rest_framework import serializers
from .models import User, Image, Product, Cart, Comment, Customer, Staff, Admin, Salary, OptionsProduct, DetailProduct


class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        fields = ['id', 'basic_salary', 'bonus', 'allowance', 'overtime', 'total_salary']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'fullName', 'province', 'district', 'ward', 'street', 'houseNumber', 'phoneNumber', 'avatar',
                  'dateOfBirth', 'email', 'gender', 'username', 'password', 'gender']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_info', 'total_money_bought', 'level_customer', 'product']


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['staff_info', 'salary_detail']


class UpdateSalaryStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        fields = ['basic_salary', 'bonus', 'allowance', 'overtime']


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['admin_info']


class UserDTOSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'fullName', 'avatar']


class LoginStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['fullName', 'address', 'phoneNumber', 'avatar',
                  'dateOfBirth', 'email', 'gender', 'gender', 'updateAt']


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'fullName', 'address', 'phoneNumber', 'avatar',
                  'dateOfBirth', 'email', 'gender', 'gender']


class UserChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_id', 'product_IMEI', 'product_title', 'product_name', 'product_price', 'product_quantity',
                  'time_guarantee', 'startDate', 'endDate', 'image']


class ProductInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_id', 'product_title', 'product_name', 'product_quantity', 'basic_price',
                  'time_guarantee', 'image_url', 'comments', 'createAt', 'manufacturer', 'like_count']


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_id', 'product_title', 'product_name', 'options_detail', 'basic_price', 'product_quantity',
                  'time_guarantee', 'image_url', 'list_comments', 'createAt', 'manufacturer',
                  'list_likes_person', 'like_count']


class ListLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['likes_person']


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_title', 'product_name', 'time_guarantee', 'image', 'updateAt']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'imageID']


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['customer_basic_info', 'products']


class CartCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'customer_id', 'product_id', 'quantity']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['comment_id', 'comment', 'user_id', 'parent_id']


class UpdateProductCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['product']


class OptionsProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionsProduct
        fields = ['id', 'option', 'price', 'quantity']


class DetailProductGuarantee(serializers.ModelSerializer):
    class Meta:
        model = DetailProduct
        fields = ['product_IMEI', 'start_guarantee', 'end_guarantee']
