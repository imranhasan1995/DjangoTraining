from django.urls import path
from . import views

#URL Configurations
urlpatterns = [
    path('insertproduct/<str:title>/', views.insertProduct),
    path('insertcollection/<str:title>/', views.insertCollections),
    path('products/', views.getProducts),
    path('productdetails/<str:title>/', views.productDetail, name='product-detail'),
    path('addcustomer/', views.addCustomer),
    path('addorder/', views.createOrder),
    path('addorderv2/', views.createOrderWithAnnotation),
    path('getrecentorders/', views.getRecentCompletedOrders),
    path('getallcustomer/', views.getCustomerDetails),
    path('customers/create/', views.CustomerCreateAPIView.as_view(), name='customer-create'),
    path('customers/update/<int:pk>/', views.CustomerUpdateAPIView.as_view(), name='customer-update'),
]