from django.urls import include, path
from . import views
from rest_framework.routers import DefaultRouter

#URL Configurations
router = DefaultRouter()
# customize the route path to 'store/address'
router.register(r'address', views.AddressViewSet, basename='address')
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
    path('customers/<int:customer_id>/', views.CustomerGetAPIView.as_view(), name='customer-detail'),
    path('orders/', views.OrderListCreateAPIView.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.OrderRetrieveUpdateAPIView.as_view(), name='order-detail'),
    path('', include(router.urls)),
    path('async/order/', views.AsyncOrderView)
]