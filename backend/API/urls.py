from django.urls import path
from graphene_django.views import GraphQLView

from .views import Login, Logout, createStaff, createAdmin, deleteUser, createCustomer, createProduct, likeProduct, \
    GetProductDetail, UpdateCart, updateProduct, SearchProduct, Comments, GetMoreComments, \
    SortListProduct, GetAllUser, ChangePassword, CartOfCustomer, FilterProduct, \
    ResetPassword, deleteProduct, getInformationByID, UpdateSalaryStaff, SearchUser, RemoveImage, CheckGuarantee, \
    returnListProvinces, returnDistrictOfProvince, returnWardOfDistrict

urlpatterns = [
    path('login', Login.as_view(), name='login'),
    path('logout', Logout, name='logout'),
    path('create_admin', createAdmin, name='create admin'),
    path('staff', createStaff, name='create staff'),
    path('user_info', getInformationByID, name='get staff info'),
    path('staff/<uuid:staff_id>', UpdateSalaryStaff, name='update salary for staff'),
    path('customer', createCustomer, name='create customer'),
    path('users/', GetAllUser, name='get user for dev'),
    path('change_password', ChangePassword, name='change password'),
    path('update', UpdateCart, name='update Cart'),
    path('delete', deleteUser, name='deleted user'),
    path('search/', SearchUser, name='search with key'),
    path('product/', GetProductDetail, name='get product detail'),
    path('list_product/', SortListProduct, name='get list product'),
    path('create_product', createProduct, name='create product '),
    path('like_product', likeProduct, name='like or unlike product'),
    path('search_product/', SearchProduct, name='search product'),
    path('product/<uuid:product_id>', deleteProduct, name='delete product'),
    path('update_product/', updateProduct, name='update product'),
    path('remove_image', RemoveImage, name='remove image'),
    path('cart/', CartOfCustomer.as_view(), name='cart of customer'),
    path('comment/<uuid:product_id>', Comments, name='comment product'),
    path('more_comment', GetMoreComments, name='get more cmt'),
    path('products/', FilterProduct, name='filter product'),
    path('reset_password', ResetPassword, name='reset password'),
    path('check/', CheckGuarantee, name='check time guarantee'),
    path('province', returnListProvinces, name='get list province'),
    path('district', returnDistrictOfProvince, name='return list district of province'),
    path('ward', returnWardOfDistrict, name='return list ward of district')
    # path("graphql", GraphQLView.as_view(graphiql=True,schema=schema)),
    # path('oauth/', include('social_django.urls', namespace='social')),  # <-- here

]
