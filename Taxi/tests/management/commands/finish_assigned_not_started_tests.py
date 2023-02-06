from django.core.management.base import BaseCommand

from tests.models import TestLogs


class Command(BaseCommand):
    help = 'Set user result as 0 if the publication date is over.'

    def handle(self, *args, **options):

        tests = TestLogs.get_not_answered_and_expired()

        finished_tests_counter = 0
        for test in tests:
            test.user_result = 0

            test.save()

            finished_tests_counter += 1

        return 'Finished: {}'.format(finished_tests_counter)
