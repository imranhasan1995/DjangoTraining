from django.shortcuts import render
# Create your views here.
# request -> responce
# request handler

from django.http import HttpResponse
from store.models import Product

def say_hello(request):
    x = 1
    y = x
    z = x + 1
    return render(request, "hello.html", {"name":"Imran"})
