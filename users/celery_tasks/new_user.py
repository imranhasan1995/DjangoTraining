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

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 5, 'countdown': 30}
)
def check_new_usersV2(self):
    """
    SUCCESS → result stored in DB
    FAILURE → exception + traceback stored in DB
    """
    interval_seconds = 30
    since_time = timezone.now() - timedelta(seconds=interval_seconds)

    # If this fails → exception stored automatically
    users = list(
        User.objects
        .filter(date_joined__gte=since_time)
        .values(
            'id', 'username', 'email',
            'first_name', 'last_name', 'date_joined'
        )
    )
    if len(users) == 0:
        raise Exception('No users added')
    # Returned data saved in DB
    return {
        "status": "success",
        "count": len(users),
        "users": users,
    }