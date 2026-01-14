# app/tasks.py
from celery import shared_task
from django.contrib.auth.models import User
import redis
import json
from django.utils import timezone
from datetime import timedelta

# Redis client
redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0)
NEW_USERS_KEY = "processed_users"

@shared_task
def check_new_users():
    # Define interval: last 30 seconds
    interval_seconds = 30
    since_time = timezone.now() - timedelta(seconds=interval_seconds)

    # Fetch users created in the last 30 seconds
    new_users_qs = User.objects.filter(date_joined__gte=since_time)
    # Serialize to JSON
    new_users_list = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_joined": user.date_joined.isoformat()
        }
        for user in new_users_qs
    ]
    print('New User Count:', len(new_users_list))
    # Save the list to Redis (overwrites previous)
    redis_client.set(NEW_USERS_KEY, json.dumps(new_users_list))
