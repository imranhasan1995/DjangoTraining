from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from store.models import Product, Collections
from django.db.models import Avg
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
