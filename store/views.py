from django.http import HttpResponse
from django.shortcuts import render
from store.models import Product, Collections
# Create your views here.

def insertProduct(request):
    # Single insert
    collections = Collections.objects.create(title="Food")
    collections.save();
    product = Product.objects.create(
        title="Laptop",
        description="High-performance gaming laptop",
        unit_price=999.99,
        inventory=50,
        collection=collections
    )
    product.save()
    return HttpResponse("Product inserted successfully")