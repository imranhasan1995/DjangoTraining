from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from store.models import Customer, Order, Product, Collections
from django.db.models import Avg
from django.db import transaction
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
