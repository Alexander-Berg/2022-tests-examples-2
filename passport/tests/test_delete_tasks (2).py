import datetime

from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import phone_bindings_history_delete_tasks_table as pbt
from passport.backend.core.differ import diff
from passport.backend.core.models.delete_tasks import PhoneBindingsHistoryDeleteTask
from passport.backend.core.serializers.delete_tasks import PhoneBindingsHistoryDeleteTaskSerializer
from passport.backend.core.test.consts import TEST_UID
from passport.backend.core.test.test_utils import PassportTestCase


TEST_DATETIME = datetime.datetime(2020, 1, 1, 10, 40, 30)


class TestPhoneBindingsHistoryDeleteTaskSerializer(PassportTestCase):
    def setUp(self):
        self.db = FakeDB()
        self.db.start()
        self.serializer = PhoneBindingsHistoryDeleteTaskSerializer()

    def tearDown(self):
        self.db.stop()
        del self.db

    @staticmethod
    def _get_task(uid=TEST_UID, deletion_started_at=TEST_DATETIME, task_id=None):
        data = {'uid': uid, 'deletion_started_at': deletion_started_at}
        if task_id is not None:
            data['task_id'] = task_id
        return PhoneBindingsHistoryDeleteTask().parse(data)

    def _task_to_db(self, task):
        with self.db.no_recording():
            self.db.insert(
                pbt.name,
                'passportdbcentral',
                task_id=task.task_id,
                uid=task.uid,
                deletion_started_at=task.deletion_started_at,
            )

    def test_no_action(self):
        task = self._get_task()
        s1 = task.snapshot()
        queries = self.serializer.serialize(
            s1,
            task,
            diff(s1, task),
        )
        eq_eav_queries(queries, [])

    def test_create_task(self):
        task = self._get_task()
        queries = self.serializer.serialize(
            None,
            task,
            diff(None, task),
        )
        eq_eav_queries(  # Почему EAV? Никто не знает. Без eav не работает
            queries,
            [
                'BEGIN',
                pbt.insert().values(uid=TEST_UID, deletion_started_at=TEST_DATETIME),
                'COMMIT',
            ],
            inserted_keys=(1,)
        )
        self.assertEqual(task.task_id, 1)

        self.db._serialize_to_eav(task)
        self.db.check_table_contents(
            pbt.name,
            'passportdbcentral',
            [
                {
                    'task_id': 1,
                    'uid': TEST_UID,
                    'deletion_started_at': TEST_DATETIME,
                },
            ],
        )

    def test_delete_task(self):
        task = self._get_task(task_id=5)
        queries = self.serializer.serialize(
            task,
            None,
            diff(task, None),
        )
        eq_eav_queries(  # Почему EAV? Никто не знает. Без eav не работает
            queries,
            [
                'BEGIN',
                pbt.delete().where(pbt.c.task_id == 5),
                'COMMIT',
            ],
        )

        self._task_to_db(task)
        self.db._serialize_to_eav(None, task)
        self.db.check_table_contents(pbt.name, 'passportdbcentral', [])

    def test_update_task(self):
        task = self._get_task(task_id=5)
        s1 = task.snapshot()
        s1.uid = TEST_UID + 5
        with self.assertRaises(NotImplementedError):
            g = self.serializer.serialize(
                task,
                s1,
                diff(task, s1),
            )
            eq_eav_queries(g, [])
