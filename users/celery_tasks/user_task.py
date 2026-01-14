# app/tasks.py
import httpx
from celery import shared_task
import redis
import json
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

EXTERNAL_API_URL = "https://jsonplaceholder.typicode.com/users"

@shared_task
def fetch_and_store_users():
    try:
        response = httpx.get(EXTERNAL_API_URL, timeout=5)
        response.raise_for_status()
        users = response.json()

        # Save users to Redis as a JSON string
        r.set("processed_users", json.dumps(users))
        return {"status": "success", "count": len(users)}

    except Exception as e:
        return {"status": "failed", "error": str(e)}
