from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django import forms
from django.views.decorators.csrf import csrf_exempt

from users.forms import UserForm

class UserCreateAPIView(APIView):
    @csrf_exempt
    def post(self, request):
        # Bind JSON data to ModelForm
        form = UserForm(request.data)

        if form.is_valid():
            user = form.save()  # creates the User
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        else:
            # Convert form.errors (ErrorDict) to normal dict
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
