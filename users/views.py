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
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from .celery_tasks import new_user
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import asyncio
from .playwright_tasks.playwright_task import run_login_playwright
import threading
from .celery_tasks.login_task import run_login_playwright_task

EXTERNAL_API_URL = "https://jsonplaceholder.typicode.com/users"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

logger = logging.getLogger('myapp')
class FetchUsersAPIView(APIView):
    def get(self, request):
        task = fetch_and_store_users.delay()  # push task to RabbitMQ
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
    
class GetProcessedUsersAPIView(APIView):
    permission_classes = [AllowAny]
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
        logger.debug('successfully fetched user list from remote API')
        return JsonResponse(data, status=status.HTTP_200_OK, safe=False)

    except httpx.RequestError as e:
        return JsonResponse({"error": f"Network error: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)
    except httpx.HTTPStatusError as e:
        return JsonResponse({"error": f"HTTP error {e.response.status_code}"}, status=e.response.status_code)
    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserCreateAPIView(APIView):
    permission_classes = [AllowAny]
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

class SceduleTask(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        interval, _ = IntervalSchedule.objects.get_or_create(
            every=30,
            period=IntervalSchedule.SECONDS,
        )

        PeriodicTask.objects.create(
            interval=interval,
            name="my-schedule",
            task="users.celery_tasks.new_user.check_new_users",
        )
        return Response("Task scheduled!", status=200)

class RemoveScheduledTask(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        task_name = "my-schedule"  # Name of the task you want to remove

        try:
            task = PeriodicTask.objects.get(name=task_name)
            task.delete()  # Deletes the scheduled task
            return Response(f"Task '{task_name}' removed!", status=200)
        except PeriodicTask.DoesNotExist:
            return Response(f"Task '{task_name}' does not exist.", status=404)


def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )
        if user:
            login(request, user)
            print('login successfull')
            return redirect("/dashboard/")
        return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")

def dashboard(request):
    return render(request, "dashboard.html")

@api_view(['POST'])
@permission_classes([AllowAny])
def start_login_playwright(request):
    """
    Trigger Playwright login asynchronously, return immediately.
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password required"}, status=400)

    # Run Playwright in background thread
    def background_task():
        import asyncio
        asyncio.run(run_login_playwright(username, password))

    threading.Thread(target=background_task).start()

    return Response({"message": "Playwright started"}, status=202)

@api_view(['POST'])
@permission_classes([AllowAny])
def start_login_celery(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password required"}, status=400)

    # Push task to Celery queue (non-blocking)
    run_login_playwright_task.delay(username, password)

    return Response({"message": "Playwright started"}, status=202)