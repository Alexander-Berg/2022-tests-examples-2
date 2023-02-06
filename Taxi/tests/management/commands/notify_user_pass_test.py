from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _, override

from compendium.models import Notification
from tests.models import TestLogs


class Command(BaseCommand):
    help = 'Search for not answered tests those will be finish soon'

    def handle(self, *args, **options):

        not_answered_tests = TestLogs.get_not_answered_tests()

        notifications_counter = 0
        for not_answered_test in not_answered_tests:

            test_title = not_answered_test.test.title
            if (
                    not_answered_test.user.lang == 'en'
                    and not_answered_test.test.title_en
            ):
                test_title = not_answered_test.test.title_en

            with override(not_answered_test.user.lang):
                message = _(
                    'I don’t want to put pressure, but the "{}" test has been '
                    'assigned to you, and you can go through it until {}. Have time?',
                ).format(test_title, not_answered_test.test.published_until)

            Notification(
                login=not_answered_test.user, text=message, type='test',
            ).save()

            notifications_counter += 1

        return 'Notified: {}'.format(notifications_counter)
