from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the labeled local development demo account."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("The demo account is available only in development.")
        user, created = get_user_model().objects.get_or_create(username="medresearch-demo")
        if created:
            user.set_password("LocalResearchDemo!26")
            user.save(update_fields=["password"])
        self.stdout.write("Local demo username: medresearch-demo")
