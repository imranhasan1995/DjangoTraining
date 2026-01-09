from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from store.models import Product, Collections
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
    products = Product.objects.all()
    return HttpResponse("Product list page")

def productDetail(request, title):
    products = Product.objects.get_or_create(title=title)
    url = reverse('product-detail', kwargs={'title':title})
    print(url)
    return HttpResponse("Product detail page")