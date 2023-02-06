# -*- coding: utf-8 -*-
import datetime

from passport.backend.core.models.delete_tasks import PhoneBindingsHistoryDeleteTask
from passport.backend.core.test.consts import TEST_UID
from passport.backend.core.test.test_utils import PassportTestCase


TEST_TASK_ID = 1234
TEST_DATETIME = datetime.datetime(2020, 1, 1, 10, 30, 40)


class TestPhoneBindingsHistoryDeleteTask(PassportTestCase):
    def test_parse(self):
        task = PhoneBindingsHistoryDeleteTask().parse({
            'task_id': TEST_TASK_ID,
            'uid': TEST_UID,
            'deletion_started_at': TEST_DATETIME,
        })
        self.assertEqual(task.task_id, TEST_TASK_ID)
        self.assertEqual(task.uid, TEST_UID)
        self.assertEqual(task.deletion_started_at, TEST_DATETIME)
