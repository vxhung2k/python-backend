# import graphene
# from graphene_django import DjangoObjectType
# from .models import User, Product, Customer, Admin, Staff, Salary, OptionsProduct, DetailProduct, Comment
#
#
# class UserType(DjangoObjectType):
#     class Meta:
#         model = User
#         fields = ('user_id', 'username', 'fullName', 'phoneNumber', 'gender', 'address', 'avatar', 'dateOfBirth',
#                   'email')
#
#
# class AdminType(DjangoObjectType):
#     class Meta:
#         model = Admin
#         fields = '__all__'
#
#
# class Query(graphene.ObjectType):
#     user_id = graphene.Field(Admin, user_id=graphene.UUID(required=True))
#     user = graphene.List(UserType)
#
#     @classmethod
#     def GetInfo(cls, root, user_id):
#         try:
#             return User.objects.get(user_id=user_id)
#         except User.DoseNotExist:
#             return {'message': 'data not found'}
#
#
# schema = graphene.Schema(query=Query)
