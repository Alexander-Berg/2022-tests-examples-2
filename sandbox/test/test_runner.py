import logging
import unittest

from sandbox.projects.mobile_apps.teamcity_sandbox_runner.runner import prepare_failed_message


logger = logging.getLogger("test_runner")


class TestPrepareFailedMessage(unittest.TestCase):
    def test_tasks_and_messages(self):
        message = prepare_failed_message(
            failed_task_ids=[1, 999, 42],
            failed_messages=['Message body\nFor the first case', 'Message body for the second case']
        )

        self.assertEqual(
            message,
            'Message body\n'
            'For the first case\n'
            'Message body for the second case\n'
            'Error in tasks [<a href="https://sandbox.yandex-team.ru/task/1/view">1</a>, '
            '<a href="https://sandbox.yandex-team.ru/task/999/view">999</a>, '
            '<a href="https://sandbox.yandex-team.ru/task/42/view">42</a>].'
        )

    def test_tasks_only(self):
        message = prepare_failed_message(
            failed_task_ids=[5006],
            failed_messages=[]
        )

        self.assertEqual(
            message,
            '\nError in tasks [<a href="https://sandbox.yandex-team.ru/task/5006/view">5006</a>].'
        )

    def test_messages_only(self):
        message = prepare_failed_message(
            failed_task_ids=[],
            failed_messages=['Message body\nThe only one']
        )

        self.assertEqual(
            message,
            'Message body\n'
            'The only one'
        )

    def test_empty_lists(self):
        message = prepare_failed_message(
            failed_task_ids=[],
            failed_messages=[]
        )

        self.assertEqual(message, '')
