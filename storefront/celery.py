# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storefront.settings")
app = Celery("storefront")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

if __name__ == "__main__":
    app.start()

app.conf.beat_schedule = {
    "check-new-users-daily": {
        "task": "users.celery_tasks.new_user.check_new_usersV2",
        # Example: run every day at 12:00 PM
        "schedule": crontab(minute=3, hour=8),
    },
}