from django.core.management.base import BaseCommand

from tests.models import Test


class Command(BaseCommand):
    help = 'Archive Test. Mark as archived tests that were expired ("published_until") 7 days ago.'

    def handle(self, *args, **options):

        updated = Test.mark_archived()

        return 'Archived: {}'.format(updated)
