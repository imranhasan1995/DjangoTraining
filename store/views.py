from rest_framework import generics, mixins, viewsets
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from store.mixins.loggingmixin import LoggingMixin
from store.models import Address, Customer, Order, Product, Collections
from django.db.models import Avg
from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status

from store.serializers import AddressSerializer, CustomerSerializer, OrderSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
# Create your views here.


def insertCollections(request, title):
    collections = Collections.objects.create(title=title)
    return HttpResponse("Collection inserted successfully")


def insertProduct(request, title):
    # Create or get collection
    collection, _ = Collections.objects.get_or_create(
        title=request.GET.get('collection')
    )
    # Single insert
    product = Product.objects.create(
        title=title,
        description=request.GET.get('description'),
        unit_price=request.GET.get('price'),
        inventory=50,
        collection=collection
    )
    return HttpResponse("Product inserted successfully")


def getProducts(request):
    # Get all products
    products = Product.objects.all()
    # Get products with price > 100
    expensive_products = Product.objects.filter(unit_price__gt=100)

    # Chain filters
    recent_expensive_products = Product.objects.filter(
        unit_price__gt=100, last_update__year=2026)
    print(recent_expensive_products)

    # Get products that are NOT expensive
    affordable_products = Product.objects.exclude(unit_price__gt=1000)
    print(affordable_products)

    # Average price of products
    avg_price = Product.objects.aggregate(Avg('unit_price'))
    print(avg_price)
    return HttpResponse("Product list page")


def productDetail(request, title):
    products = Product.objects.get_or_create(title=title)
    url = reverse('product-detail', kwargs={'title': title})
    print(url)
    return HttpResponse("Product detail page")


def createCustomer(name):
    customer = Customer.objects.create(
        first_name=name,
        last_name='ext',
        email=name + 'test@gmail.com',
        phone='01943122344',
        membership='S'
    )
    return customer


def addCustomer(request):
    createCustomer(request.GET.get('name'))
    return HttpResponse("Customer added successfully")


def createOrder(request):
    # OUTER atomic block starts a database transaction
    with transaction.atomic():
        # Customer is created inside the transaction
        # This save is part of the outer transaction
        customer = createCustomer(request.GET.get('name'))

        try:
            # INNER atomic block creates a SAVEPOINT
            # Any error here can rollback only this inner block
            with transaction.atomic():
                # Create an order linked to the customer
                order = Order.objects.create(
                    customer=customer,
                    payment_status=Order.PAYMENT_STATUS_PENDING
                )

                # Force an exception to test rollback
                raise Exception('Failed')

        except Exception:
            # Exception is caught here
            # Django rolls back to the inner savepoint
            # Only the order creation is undone
            # Outer transaction (customer) is still active
            pass

    # Outer transaction is committed automatically here
    # Result:
    # ✅ Customer is saved
    # ❌ Order is rolled back due to inner savepoint
    return HttpResponse("Order added successfully")


@transaction.atomic
def createOrderWithAnnotation(request):
    # Entire function runs inside a single transaction
    customer = createCustomer(request.GET.get('name'))

    # Calls another atomic function
    # Note: Exception handling inside addOrder determines rollback
    addOrder(customer)

    # If no exception escapes, the whole transaction is committed
    # Result depends on addOrder behavior
    return HttpResponse("Order added successfully")


@transaction.atomic
def addOrder(customer):
    try:
        # Create order inside transaction
        order = Order.objects.create(
            customer=customer,
            payment_status=Order.PAYMENT_STATUS_PENDING
        )

        # Force an exception after saving order
        raise Exception('Failed')

    except Exception:
        # Catching exception prevents automatic rollback
        # We must manually mark transaction for rollback
        transaction.set_rollback(True)

    # At this point, if exception occurs, order will be rolled back
    # Customer will also be rolled back if part of same transaction


def getRecentCompletedOrders(request):
    # Filter customers with Silver or Gold membership (Query NOT executed yet)
    customers_qs = Customer.objects.filter(
        membership__in=[Customer.MEMBERSHIP_SILVER, Customer.MEMBERSHIP_GOLD])


    # Chaining Methods
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    recent_orders = Order.objects.filter(customer__in=customers_qs) \
                                 .filter(payment_status=Order.PAYMENT_STATUS_COMPLETE) \
                                 .filter(placed_at__gte=thirty_days_ago) \
                                 .order_by('-placed_at')
    print(list(recent_orders))
    # values() and values_list()
    orders_dict = recent_orders.values(
        'id', 'customer__first_name', 'customer__membership', 'placed_at')
    print(list(orders_dict))

    # As tuples
    orders_tuple = recent_orders.values_list(
        'id', 'customer__first_name', 'placed_at')
    print(list(orders_tuple))
    # Single field (order IDs)
    order_ids = recent_orders.values_list('id', flat=True)
    print(list(order_ids))
    # exists() and count()
    if recent_orders.exists():
        print(
            f"There are {recent_orders.count()} recent completed orders for Silver/Gold members.")
    else:
        print("No recent completed orders for Silver/Gold members.")

    # Return all results together
    return HttpResponse("Query successfull")


@api_view(['GET'])
def getCustomerDetails(request):
    customers = Customer.objects.all()  # get all customers
    serializer = CustomerSerializer(customers, many=True)
    return Response({
        "status": "success",
        "count": customers.count(),
        "data": serializer.data
    })

class CustomerGetAPIView(APIView):
    def get(self, request, customer_id=None):
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
                serializer = CustomerSerializer(customer)
                return Response(serializer.data)
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            customers = Customer.objects.all()
            serializer = CustomerSerializer(customers, many=True)
            return Response(serializer.data)
        
class CustomerListGetAPIView(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get(self, request):
        return self.list(request)

class CustomerCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Customer created successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
class CustomerUpdateAPIView(APIView):

    def put(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CustomerSerializer(
            customer,
            data=request.data,
            partial=True  # allows partial updates
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Customer updated successfully",
                    "data": serializer.data
                }
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# List all orders & Create new order
class OrderListCreateAPIView(LoggingMixin, 
                             mixins.ListModelMixin,
                             mixins.CreateModelMixin,
                             generics.GenericAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    # GET /orders/
    def get(self, request):
        return self.list(request)

    # POST /orders/
    def post(self, request):
        return self.create(request)

# Retrieve single order & Update existing order
class OrderRetrieveUpdateAPIView(LoggingMixin, 
                                 mixins.RetrieveModelMixin,
                                 mixins.UpdateModelMixin,
                                 generics.GenericAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    # GET /orders/<id>/
    def get(self, request, pk):
        return self.retrieve(request, pk=pk)

    # PUT /orders/<id>/
    def put(self, request, pk):
        return self.update(request, pk=pk)
    
class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    # JWT Authentication
    authentication_classes = [JWTAuthentication]

    # Public GET, authenticated for write actions
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]


class AsyncOrderView(APIView):
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
