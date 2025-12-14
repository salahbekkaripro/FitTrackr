import os

from django.conf import settings
from django.core.management import BaseCommand, CommandError, call_command


class Command(BaseCommand):
    help = "Flush database data then reload the official demo fixture."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-flush",
            action="store_true",
            help="Skip flushing the database and only load the fixture.",
        )

    def handle(self, *args, **options):
        fixture_path = os.path.join(settings.BASE_DIR, "fixtures", "demo_data.json")
        if not os.path.exists(fixture_path):
            raise CommandError(f"Fixture not found at {fixture_path}")

        if not options["no_flush"]:
            self.stdout.write("Flushing database before loading demo data...")
            call_command("flush", interactive=False)

        self.stdout.write("Loading demo fixture...")
        call_command("loaddata", fixture_path)
        self.stdout.write(self.style.SUCCESS("Demo data loaded successfully."))
