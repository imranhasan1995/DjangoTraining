from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'List all users created in the last N hours'

    def add_arguments(self, parser):
        # Optional argument to specify hours
        parser.add_argument(
            '--hours',
            type=int,
            default=1,
            help='Number of hours to look back for newly created users'
        )

    def handle(self, *args, **options):
        hours = options['hours']
        now = timezone.now()
        cutoff_time = now - timedelta(hours=hours)

        User = get_user_model()
        new_users = User.objects.filter(date_joined__gte=cutoff_time)

        if new_users.exists():
            self.stdout.write(f"Users created in the last {hours} hour(s):")
            for user in new_users:
                self.stdout.write(f"- {user.username} ({user.email}) at {user.date_joined}")
        else:
            self.stdout.write(f"No users created in the last {hours} hour(s).")
