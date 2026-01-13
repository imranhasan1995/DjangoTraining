from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from django.contrib.auth.models import User

# Receiver function
@receiver(post_save, sender=User)
def user_saved(sender, instance, created, **kwargs):
    if created:
        print(f"New user created: {instance.username}")
    else:
        print(f"User updated: {instance.username}")


# Signal triggered when external data is fetched
external_data_fetched = Signal()
@receiver(external_data_fetched)
def handle_external_data(sender, url, response_data, **kwargs):
    print(f"Custom signal fired from {sender}")
    print(f"URL: {url}")
    print(f"Response length: {len(response_data) if response_data else 0}")