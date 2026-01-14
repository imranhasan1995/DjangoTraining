import json
from django.http import JsonResponse
from django.shortcuts import render
import logging

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django import forms
from django.views.decorators.csrf import csrf_exempt
import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed, retry_if_exception_type, AsyncRetrying
from users.signals import external_data_fetched
from users.serializers import UserSerializer
import requests
from .celery_tasks.user_task import fetch_and_store_users
import redis
import os
from rest_framework.permissions import AllowAny

EXTERNAL_API_URL = "https://jsonplaceholder.typicode.com/users"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)


class FetchUsersAPIView(APIView):
    def get(self, request):
        task = fetch_and_store_users.delay()  # push task to RabbitMQ
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
    
class GetProcessedUsersAPIView(APIView):
    def get(self, request):
        users_json = r.get("processed_users")
        if not users_json:
            return Response({"message": "No data found"}, status=404)
        users = json.loads(users_json)
        return Response(users, status=200)

async def getexternaldata(request):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(EXTERNAL_API_URL)
            response.raise_for_status()
            data = json.loads(response.text)  # use response.text to avoid blocking

        # Dispatch the custom signal
        external_data_fetched.send(
            sender=getexternaldata,
            url=EXTERNAL_API_URL,
            response_data=data
        )
        return JsonResponse(data, status=status.HTTP_200_OK, safe=False)

    except httpx.RequestError as e:
        return JsonResponse({"error": f"Network error: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)
    except httpx.HTTPStatusError as e:
        return JsonResponse({"error": f"HTTP error {e.response.status_code}"}, status=e.response.status_code)
    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserCreateAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


'''
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
'''