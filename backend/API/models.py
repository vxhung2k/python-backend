import uuid

from django.core.validators import RegexValidator
from django.db import models
import pandas as pd

# Create your models here.
# config enum data for field
DataTypeUser = (
    ('customer', 'customer'),
    ('staff', 'staff'),
    ('admin', 'admin')
)
DataGender = (
    ('male', 'male'),
    ('female', 'female')
)
DataLevelCustomer = (
    ('bronze', 'bronze'),
    ('silver', 'silver'),
    ('gold', 'gold'),
    ('diamond', 'diamond')
)
DataTypeTimeGuarantee = (
    ('years', 'years'),
    ('months', 'months')
)
PaymentMethod = (
    ('cash', 'Cash'),
    ('credit', 'Credit')
)
PaymentStatus = (
    ('pending', 'Pending'),
    ('complete', 'Complete'),
    ('refunded', 'Refunded'),
    ('cancelled', 'Cancelled'),
    ('failed', 'Failed')
)
PaymentCurrency = (
    ('VND', 'VND'),
    ('USD', 'USD')
)
TransactionStatus = (
    ('success', 'success'),
    ('failed', 'failed'),
    ('waiting', 'waiting'),
    ('processing', 'processing')
)


class Image(models.Model):
    imageID = models.CharField(max_length=1000, null=True)


class Salary(models.Model):
    basic_salary = models.BigIntegerField(null=False)
    bonus = models.BigIntegerField(default=0)
    allowance = models.BigIntegerField(default=1500000)
    overtime = models.BigIntegerField(default=0)

    @property
    def total_salary(self):
        return self.basic_salary + self.bonus + self.allowance + self.overtime * (self.basic_salary / 27) * 3


class User(models.Model):
    user_id = models.UUIDField(primary_key=True, editable=True, auto_created=True, default=uuid.uuid4, blank=True)
    username = models.CharField(max_length=28, null=False, unique=True)
    otp = models.CharField(max_length=6, null=True)
    password = models.CharField(max_length=300, null=False)
    gender = models.CharField(choices=DataGender, default='male', max_length=6)
    fullName = models.CharField(max_length=128, null=True)
    province = models.IntegerField(blank=True)
    district = models.IntegerField(blank=True)
    ward = models.IntegerField(blank=True)
    street = models.CharField(max_length=500, blank=True)
    houseNumber = models.CharField(max_length=500, blank=True)
    phoneNumber = models.CharField(max_length=10)
    avatar = models.CharField(max_length=200, null=True)
    dateOfBirth = models.DateField(auto_now=False, auto_now_add=False, null=True)
    email = models.EmailField(null=True, unique=True)
    createAt = models.DateTimeField(auto_now_add=True)
    updateAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fullName

    @property
    def address(self):
        path1 = u'~/data_location/Provinces.xls'
        path2 = u'~/data_location/DistrictsAndWards.xls'
        df1 = pd.read_excel(path1)
        provinces_name = list(df1.name.head(63))
        provinces_id = list(df1.id.head(63))
        df2 = pd.read_excel(path2)
        districts_id = list(df2.id_district)
        districts_name = list(df2.district)
        wards_id = list(df2.id_ward)
        wards_name = list(df2.ward)
        index_province = provinces_id.index(self.province)
        index_district = districts_id.index(self.district)
        index_ward = wards_id.index(self.ward)
        return f'{self.houseNumber},{self.street},{wards_name[index_ward]},{districts_name[index_district]},' \
               f'{provinces_name[index_province]}'


class Comment(models.Model):
    comment_id = models.UUIDField(primary_key=True, editable=False, auto_created=True, default=uuid.uuid4)
    comment = models.CharField(max_length=1000, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_id = models.CharField(max_length=200, default=None, null=True, blank=True)
    has_next_reply_cmt = models.BooleanField(default=False)


class DetailProduct(models.Model):
    product_IMEI = models.CharField(max_length=24, null=False, unique=True)
    start_guarantee = models.DateField(auto_now_add=False, auto_created=False)
    end_guarantee = models.DateField(auto_now=False, auto_created=False)


class OptionsProduct(models.Model):
    option = models.CharField(max_length=200, null=False)
    price = models.BigIntegerField(null=False)
    detail = models.ManyToManyField(DetailProduct, default=None)
    quantity = models.IntegerField(default=0, null=False)


class Product(models.Model):
    product_id = models.UUIDField(primary_key=True, editable=True, auto_created=True, default=uuid.uuid4, blank=True)
    product_name = models.CharField(max_length=200, null=False)
    product_title = models.CharField(max_length=1000, null=False)
    time_guarantee = models.BigIntegerField(null=False)
    type_time_guarantee = models.CharField(choices=DataTypeTimeGuarantee, default='years', max_length=6)
    image = models.ManyToManyField(Image, blank=True, default=None)
    likes_person = models.ManyToManyField(User,
                                          related_name="%(app_label)s_%(class)s_likes_person", null=True, blank=True)
    comments = models.ManyToManyField(Comment, null=True, blank=True)
    manufacturer = models.CharField(max_length=100, default=None)
    createAt = models.DateTimeField(auto_now_add=True)
    updateAt = models.DateTimeField(auto_now=True)
    options = models.ManyToManyField(OptionsProduct, default=None, null=True, blank=True)

    def __str__(self):
        return self.product_name + self.product_title

    @property
    def basic_price(self):
        if self.options.all().count() > 0:
            for i in self.options.all():
                option = OptionsProduct.objects.get(id=i.id)
                break
            return option.price

    @property
    def options_detail(self):
        count = self.options.all().count()
        items = []
        if count > 0:
            for i in self.options.all():
                option = OptionsProduct.objects.get(id=i.id)
                item = {'opt_id': option.id, 'option': option.option, 'price': option.price,
                        'total_product_of_option': option.quantity}
                items.append(item)
        return items

    @property
    def product_quantity(self):
        product_count = 0
        for i in self.options.all():
            items = OptionsProduct.objects.get(id=i.id)
            product_count += items.quantity
        return product_count

    @property
    def like_count(self):
        return self.likes_person.all().count()

    @property
    def image_url(self):
        list_mage_count = self.image.all().count()
        images = []
        if list_mage_count > 0:
            for i in self.image.all():
                image = Image.objects.get(id=i.id)
                images.append({'id': image.id, 'url': image.imageID})
        return images

    @property
    def list_likes_person(self):
        likes_count = self.likes_person.all().count()
        persons = []
        if likes_count > 0:
            for i in self.likes_person.all():
                person = User.objects.get(user_id=i.user_id)
                person_info = {'user_id': person.user_id, 'fullName': person.fullName, 'avatar': person.avatar}
                persons.append(person_info)
        return persons

    @property
    def list_comments(self):
        list_cmt = []
        cmt_count = self.comments.all().count()
        if cmt_count > 0:
            for i in self.comments.all():
                cmt = Comment.objects.get(comment_id=i.comment_id)
                if cmt.has_next_reply_cmt:
                    more_cmt = Comment.objects.filter(parent_id=i)
                    data = {'comment_id': cmt.comment_id, 'comment': cmt.comment, 'user_id': cmt.user_id,
                            'reply_count': len(more_cmt)}
                    list_cmt.append(data)
                else:
                    data = {'comment_id': cmt.comment_id, 'comment': cmt.comment, 'user_id': cmt.user_id,
                            'reply_count': 0}
                    list_cmt.append(data)
        return list_cmt

    @property
    def product_detail_in_cart(self):
        product = []


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_money_bought = models.BigIntegerField(default=0)
    product = models.ManyToManyField(Product)
    level_customer = models.CharField(choices=DataLevelCustomer, default='bronze', max_length=20)

    @property
    def customer_info(self):
        customer = User.objects.get(user_id=self.user.user_id)
        customer_info = {'gender': customer.gender, 'fullName': customer.fullName, 'address': customer.address,
                         'phoneNumber': customer.phoneNumber, 'email': customer.email, 'avatar': customer.avatar,
                         'dateOfBirth': customer.dateOfBirth}
        return customer_info
    # @property
    # def list_product(self):


class Staff(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    salary = models.OneToOneField(Salary, on_delete=models.CASCADE)

    @property
    def staff_info(self):
        staff = User.objects.get(user_id=self.user.user_id)
        staff_info = {'gender': staff.gender, 'fullName': staff.fullName, 'address': staff.address,
                      'phoneNumber': staff.phoneNumber, 'email': staff.email, 'avatar': staff.avatar,
                      'dateOfBirth': staff.dateOfBirth}
        return staff_info

    @property
    def salary_detail(self):
        salary = Salary.objects.get(id=self.salary.id)
        salary_obj = {'basic_salary': salary.basic_salary, 'bonus': salary.bonus, 'allowance': salary.allowance,
                      'hours_overtime': salary.overtime, 'overtime': salary.overtime * 3 * (salary.basic_salary / 27),
                      'total': salary.total_salary}
        return salary_obj


class Admin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def admin_info(self):
        admin = User.objects.get(user_id=self.user.user_id)
        info = {'gender': admin.gender, 'fullName': admin.fullName, 'address': admin.address,
                'phoneNumber': admin.phoneNumber, 'email': admin.email, 'avatar': admin.avatar,
                'dateOfBirth': admin.dateOfBirth}
        return info


class Cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ManyToManyField(Product)

    @property
    def customer_basic_info(self):
        customer = User.objects.get(user_id=self.customer.user_id)
        info = {'customer_id': customer.user_id, 'fullName': customer.fullName}
        return info

    @property
    def products(self):
        product_count = self.product.all().count()
        items = []
        if product_count > 0:
            for i in self.product.all():
                product = Product.objects.get(product_id=i.product_id)
                product_info = {'product_name': product.product_name, 'product_IMEI': product.product_IMEI,
                                'product_price': product.product_price, 'startDate': product.startDate,
                                'endData': product.endDate, 'time_guarantee': product.time_guarantee,
                                'image': product.image_url}
                item = {'product': product_info}
                items.append(item)
        return items


class Payment(models.Model):
    payment_id = models.UUIDField(primary_key=True, editable=True, auto_created=True, default=uuid.uuid4, blank=True)
    product_id = models.ForeignKey(Product, on_delete=models.PROTECT)
    payment_status = models.CharField(choices=PaymentStatus, null=False, max_length=20)
    payment_method = models.CharField(choices=PaymentMethod, max_length=10, null=False)
    payment_amount = models.BigIntegerField(null=False)
    payment_currency = models.CharField(choices=PaymentCurrency, default='VND', max_length=5)
    payment_date = models.DateTimeField(auto_now_add=True)
    credit_card_number = models.CharField(max_length=19)
    bank_name = models.CharField(max_length=50)


class PaymentTransaction(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    transaction_id = models.UUIDField(default=uuid.uuid4, auto_created=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_status = models.CharField(choices=TransactionStatus, max_length=20, null=False)
    transaction_amount = models.BigIntegerField(null=False)

