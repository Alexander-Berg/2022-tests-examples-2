# coding: utf-8
from __future__ import unicode_literals, absolute_import, division, print_function

import unittest

from sandbox import sdk2
from sandbox.common.types import notification as ctn
from sandbox.projects.rasp.utils.email_notifications import (
    EmailNotificationMixin,
    SWITCHABLE_NOTIFICATIONS,
    RASP_GROUP,
    BUS_GROUP,
)


class TaskForTests(EmailNotificationMixin):
    class _Parameters(object):
        def __init__(self):
            self.enable_email_notifications = True
            self.notifications = []

    def __init__(self):
        self.Parameters = self._Parameters()


class TestEmailNotificationMixin(unittest.TestCase):
    def test_extend_default_notifications(self):
        task = TaskForTests()
        task.add_email_notifications()

        _check_notification_in_task(task, RASP_GROUP)

    def test_extend_notifications(self):
        task = TaskForTests()
        task.add_email_notifications(BUS_GROUP)

        _check_notification_in_task(task, BUS_GROUP)

    def test_keep_old_notifications(self):
        old_notification = sdk2.Notification([], ['email'], ctn.Transport.EMAIL)

        task = TaskForTests()
        task.Parameters.notifications.append(old_notification)
        task.add_email_notifications(BUS_GROUP)

        assert task.Parameters.notifications.count(old_notification) == 1
        _check_notification_in_task(task, BUS_GROUP)

    def test_composite_notifications(self):
        task = TaskForTests()
        task.add_email_notifications()
        task.add_email_notifications(BUS_GROUP)

        _check_notification_in_task(task, RASP_GROUP)
        _check_notification_in_task(task, BUS_GROUP)


def _check_notification_in_task(task, group_name):
    for notification in SWITCHABLE_NOTIFICATIONS[group_name]:
        assert task.Parameters.notifications.count(notification) == 1
