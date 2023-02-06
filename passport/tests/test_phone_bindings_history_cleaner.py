# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import (
    datetime,
    timedelta,
)

import mock
from nose_parameterized import parameterized
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.db.schemas import (
    phone_bindings_history_delete_tasks_table as pbh_delete_table,
    phone_bindings_history_table as pbh_table,
)
from passport.backend.core.dbmanager.sharder import (
    build_mod_shard_function,
    get_sharder,
)
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.dbscripts.phone_bindings_history_cleaner.cli import Main
from passport.backend.dbscripts.phone_bindings_history_cleaner.delete import PhoneBindingsHistoryDeleter
from passport.backend.dbscripts.test.base import TestCase
from passport.backend.dbscripts.test.consts import (
    TEST_DATETIME1,
    TEST_DATETIME2,
    TEST_PHONE_NUMBER1,
    TEST_PHONE_NUMBER2,
    TEST_UID1,
    TEST_UID2,
    TEST_UID3,
)


TEST_NOW = datetime(2020, 5, 15, 12, 30, 45)
TEST_TS_BEFORE_THRESHOLD1 = datetime(2020, 5, 4, 10, 30, 45)
TEST_TS_BEFORE_THRESHOLD2 = datetime(2020, 4, 10, 12, 15, 44)
TEST_TS_BEFORE_THRESHOLD3 = datetime(2008, 4, 10, 12, 15, 44)
TEST_TS_AFTER_THRESHOLD1 = datetime(2020, 5, 16, 6, 10, 43)
TEST_TS_AFTER_THRESHOLD2 = datetime(2025, 5, 25, 16, 44, 12)
TEST_UID4 = TEST_UID3 + 2
TEST_UID5 = TEST_UID4 + 2
TEST_UID6 = TEST_UID5 + 2
TEST_UID7 = TEST_UID6 + 2

SECOND = timedelta(seconds=1)


class BaseBindingsHistoryCleanerTestCase(TestCase):
    def _assert_blackbox_userinfo_called(self, uids):
        expected_uids = sorted(map(str, uids))
        actual_uids = []
        for request in self._blackbox_faker.get_requests_by_method('userinfo'):
            actual_uids.extend(request.post_args['uid'].split(','))
        actual_uids.sort()
        assert actual_uids == expected_uids

    def _assert_tasks(self, *tasks):
        self._db_faker.check_table_contents(pbh_delete_table.name, 'passportdbcentral', tasks)


@with_settings_hosts(
    PHONE_BINDING_DELETION_THRESHOLD_DAYS=10,
    DATABASE_DELETE_RETRIES=2,
    TASKS_QUERY_CHUNK_SIZE=3,
    DATABASE_WRITE_PER_SECOND=100,
)
class TestPhoneBindingsHistoryCleaner(BaseBindingsHistoryCleanerTestCase):
    def setUp(self):
        super(TestPhoneBindingsHistoryCleaner, self).setUp()
        self._sharder = get_sharder(pbh_table.name)
        self._sharder_config = {
            0: 'passportdbshard1',
            1: 'passportdbshard2',
        }
        self._sharder.configure(
            self._sharder_config,
            shard_function=build_mod_shard_function(2),
        )
        self._datetime_patch = mock.patch(
            'passport.backend.dbscripts.phone_bindings_history_cleaner.delete.datetime',
            mock.Mock(now=mock.Mock(return_value=TEST_NOW)),
        )
        self._datetime_patch.start()

        self._throttler = mock.Mock(name='throttler', throttle=mock.Mock(name='throttler.throttle'))
        self._throttler_class = mock.Mock(name='Throttler', return_value=self._throttler)
        self._throttler_patch = mock.patch(
            'passport.backend.dbscripts.phone_bindings_history_cleaner.delete.Throttler',
            self._throttler_class,
        )
        self._throttler_patch.start()

    def tearDown(self):
        self._throttler_patch.stop()
        self._datetime_patch.stop()
        super(TestPhoneBindingsHistoryCleaner, self).tearDown()

    def _create_tasks(self, *tasks):
        for task in tasks:
            self._db_faker.insert(pbh_delete_table.name, 'passportdbcentral', **task)

    def _create_bindings(self, *bindings):
        for binding in bindings:
            db_name = self._sharder.key_to_db_name(binding['uid'])
            self._db_faker.insert(pbh_table.name, db_name, **binding)

    def _setup_blackbox(self, uids):
        self._blackbox_faker.set_blackbox_response_side_effect(
            method='userinfo',
            side_effect=(blackbox_userinfo_response(uid=uid) for uid in uids),
        )

    def _run(self):
        Main().run(mock.Mock(command='clean'))

    def _assert_bindings(self, *bindings):
        bindings_by_db_names = defaultdict(list)
        for binding in bindings:
            db_name = self._sharder.key_to_db_name(binding['uid'])
            bindings_by_db_names[db_name].append(binding)
        for db_name in self._sharder_config.values():
            bindings = bindings_by_db_names[db_name]
            self._db_faker.check_table_contents(pbh_table.name, db_name, bindings)

    def _assert_blackbox_userinfo_called(self, uids):
        requests = self._blackbox_faker.get_requests_by_method('userinfo')
        self.assertEqual(list(uids), list(r.post_args['uid'] for r in requests))

    def _assert_throttled(self, calls):
        self.assertEqual(self._throttler.throttle.call_count, len(calls))
        self._throttler.throttle.assert_has_calls([mock.call(num) for num in calls])

    def test_throttler_init(self):
        PhoneBindingsHistoryDeleter(mock.Mock())
        self._throttler_class.assert_called_once_with(rps=100)

    def test_delete_single_task__ok(self):
        self._create_tasks(
            {'uid': TEST_UID1, 'deletion_started_at': TEST_TS_BEFORE_THRESHOLD1},
        )
        self._create_bindings(
            {'uid': TEST_UID1, 'number': str(TEST_PHONE_NUMBER1), 'bound': TEST_DATETIME1},
            {'uid': TEST_UID1, 'number': str(TEST_PHONE_NUMBER2), 'bound': TEST_DATETIME2},
        )
        self._setup_blackbox([None])
        self._run()
        self._assert_tasks()
        self._assert_bindings()
        self._assert_blackbox_userinfo_called([TEST_UID1])
        self._assert_throttled([2])

    def test_delete_single_task__account_exists(self):
        self._create_tasks(
            {'uid': TEST_UID1, 'deletion_started_at': TEST_TS_BEFORE_THRESHOLD1},
        )
        self._create_bindings(
            {'uid': TEST_UID1, 'number': str(TEST_PHONE_NUMBER1), 'bound': TEST_DATETIME1},
            {'uid': TEST_UID1, 'number': str(TEST_PHONE_NUMBER2), 'bound': TEST_DATETIME2},
        )
        self._setup_blackbox([TEST_UID1])
        self._run()
        self._assert_tasks()
        self._assert_bindings(
            {'uid': TEST_UID1, 'number': str(TEST_PHONE_NUMBER1), 'bound': TEST_DATETIME1},
            {'uid': TEST_UID1, 'number': str(TEST_PHONE_NUMBER2), 'bound': TEST_DATETIME2},
        )
        self._assert_blackbox_userinfo_called([TEST_UID1])
        self._assert_throttled([1])

    def test_delete_multiple_tasks(self):
        """
        Множество аккаунтов:
        UID1 - есть таск, 2 связки, нет аккаунта, время пришло: выполняем
        UID2 - есть таск, 2 связки, нет аккаунта, время не пришло: не выполняем
        UID3 - есть таск, 1 связка, нет аккаунта, время пришло: выполняем
        UID4 - есть таск, 1 связка, нет аккаунта, время не пришло: не выполняем
        UID5 - есть таск, нет связок, нет аккаунта, время пришло: выполняем
        UID6 - нет таска, 2 связки, нет аккаунта: не выполняем
        UID7 - есть таск, 2 связки, есть аккаунт, время пришло: не выполняем
        """
        self._create_tasks(
            {'uid': TEST_UID1, 'deletion_started_at': TEST_TS_BEFORE_THRESHOLD1},
            {'uid': TEST_UID2, 'deletion_started_at': TEST_TS_AFTER_THRESHOLD1},
            {'uid': TEST_UID3, 'deletion_started_at': TEST_TS_BEFORE_THRESHOLD2},
            {'uid': TEST_UID4, 'deletion_started_at': TEST_TS_AFTER_THRESHOLD2},
            {'uid': TEST_UID5, 'deletion_started_at': TEST_TS_BEFORE_THRESHOLD3},
            {'uid': TEST_UID7, 'deletion_started_at': TEST_TS_BEFORE_THRESHOLD3},
        )
        self._create_bindings(
            {'uid': TEST_UID1, 'number': str(TEST_PHONE_NUMBER1), 'bound': TEST_DATETIME1},
            {'uid': TEST_UID1, 'number': str(TEST_PHONE_NUMBER2), 'bound': TEST_DATETIME2},
            {'uid': TEST_UID2, 'number': str(TEST_PHONE_NUMBER1), 'bound': TEST_DATETIME1},
            {'uid': TEST_UID2, 'number': str(TEST_PHONE_NUMBER2), 'bound': TEST_DATETIME2},
            {'uid': TEST_UID3, 'number': str(TEST_PHONE_NUMBER1), 'bound': TEST_DATETIME1},
            {'uid': TEST_UID4, 'number': str(TEST_PHONE_NUMBER1), 'bound': TEST_DATETIME1},
            {'uid': TEST_UID6, 'number': str(TEST_PHONE_NUMBER1), 'bound': TEST_DATETIME1},
            {'uid': TEST_UID6, 'number': str(TEST_PHONE_NUMBER2), 'bound': TEST_DATETIME2},
            {'uid': TEST_UID7, 'number': str(TEST_PHONE_NUMBER1), 'bound': TEST_DATETIME1},
            {'uid': TEST_UID7, 'number': str(TEST_PHONE_NUMBER2), 'bound': TEST_DATETIME2},
        )
        self._setup_blackbox([None, None, None, TEST_UID7])
        self._run()
        self._assert_tasks(
            {'task_id': 2, 'uid': TEST_UID2, 'deletion_started_at': TEST_TS_AFTER_THRESHOLD1},
            {'task_id': 4, 'uid': TEST_UID4, 'deletion_started_at': TEST_TS_AFTER_THRESHOLD2},
        )
        self._assert_bindings(
            {'uid': TEST_UID2, 'number': str(TEST_PHONE_NUMBER1), 'bound': TEST_DATETIME1},
            {'uid': TEST_UID2, 'number': str(TEST_PHONE_NUMBER2), 'bound': TEST_DATETIME2},
            {'uid': TEST_UID4, 'number': str(TEST_PHONE_NUMBER1), 'bound': TEST_DATETIME1},
            {'uid': TEST_UID6, 'number': str(TEST_PHONE_NUMBER1), 'bound': TEST_DATETIME1},
            {'uid': TEST_UID6, 'number': str(TEST_PHONE_NUMBER2), 'bound': TEST_DATETIME2},
            {'uid': TEST_UID7, 'number': str(TEST_PHONE_NUMBER1), 'bound': TEST_DATETIME1},
            {'uid': TEST_UID7, 'number': str(TEST_PHONE_NUMBER2), 'bound': TEST_DATETIME2},
        )
        self._assert_blackbox_userinfo_called([TEST_UID1, TEST_UID3, TEST_UID5, TEST_UID7])
        self._assert_throttled([2, 2, 2, 1])

    def test_delete_no_tasks(self):
        self._create_tasks(
            {'uid': TEST_UID1, 'deletion_started_at': TEST_TS_AFTER_THRESHOLD1},
        )
        self._create_bindings(
            {'uid': TEST_UID1, 'number': str(TEST_PHONE_NUMBER1), 'bound': TEST_DATETIME1},
            {'uid': TEST_UID1, 'number': str(TEST_PHONE_NUMBER2), 'bound': TEST_DATETIME2},
        )
        self._run()
        self._assert_tasks(
            {'task_id': 1, 'uid': TEST_UID1, 'deletion_started_at': TEST_TS_AFTER_THRESHOLD1},
        )
        self._assert_bindings(
            {'uid': TEST_UID1, 'number': str(TEST_PHONE_NUMBER1), 'bound': TEST_DATETIME1},
            {'uid': TEST_UID1, 'number': str(TEST_PHONE_NUMBER2), 'bound': TEST_DATETIME2},
        )
        self._assert_blackbox_userinfo_called([])
        self._assert_throttled([])

    def test_many_chunks(self):
        self._create_tasks(
            *[
                {
                    'uid': [TEST_UID1, TEST_UID2][i & 1],
                    'deletion_started_at': TEST_TS_BEFORE_THRESHOLD1
                } for i in range(9)
            ]
        )
        self._setup_blackbox([None] * 9)

        with settings_context(
            PHONE_BINDING_DELETION_THRESHOLD_DAYS=10,
            DATABASE_DELETE_RETRIES=2,
            TASKS_QUERY_CHUNK_SIZE=2,
            DATABASE_WRITE_PER_SECOND=100,
        ):
            self._run()

        self._assert_bindings()
        self._assert_tasks()
        delete_until = TEST_NOW - timedelta(days=10)
        base_query = pbh_delete_table.select(pbh_delete_table.c.deletion_started_at <= delete_until)
        base_query = base_query.limit(2)
        queries_gen = (
            [
                base_query.where(pbh_delete_table.c.task_id > i).order_by(pbh_delete_table.c.task_id),
                pbh_table.delete(pbh_table.c.uid == TEST_UID1),
                'BEGIN',
                pbh_delete_table.delete(pbh_delete_table.c.task_id == i + 1),
                'COMMIT',
                pbh_table.delete(pbh_table.c.uid == TEST_UID2),
                'BEGIN',
                pbh_delete_table.delete(pbh_delete_table.c.task_id == i + 2),
                'COMMIT',
            ] for i in range(0, 9, 2)
        )
        queries = sum(queries_gen, [])[:-4]
        self._db_faker.assert_executed_queries_equal(queries)
        self._assert_blackbox_userinfo_called([[TEST_UID1, TEST_UID2][i & 1] for i in range(9)])
        self._assert_throttled([2] * 9)


class TestArgparse(BaseBindingsHistoryCleanerTestCase):
    def setUp(self):
        super(TestArgparse, self).setUp()
        self._argparse_print_patch = mock.patch('argparse.ArgumentParser._print_message', mock.Mock())
        self._argparse_print_patch.start()

    def tearDown(self):
        self._argparse_print_patch.stop()
        super(TestArgparse, self).tearDown()

    def _get_parser(self):
        return Main().get_arg_parser()

    @parameterized.expand([
        (
            ['clean'],
            dict(command='clean'),
        ),
    ])
    def test_args_ok(self, argv, expectation):
        args = self._get_parser().parse_args(argv)
        for k, v in expectation.items():
            try:
                val = getattr(args, k)
            except AttributeError:
                raise AssertionError('{}: no attribute {}'.format(args, k))
            if v is None:
                self.assertIsNone(val, '{}: {} is not None'.format(args, k))
            else:
                self.assertEqual(val, v, '{}: wrong {} value: {} != {}'.format(args, k, val, v))

    @parameterized.expand([
        ([],),
        (['clean', '--dry-run'],),
    ])
    def test_args_not_ok(self, argv):
        try:
            self._get_parser().parse_args(argv)
        except SystemExit:
            pass
        else:
            self.assertFalse(False, 'SystemExit is not raised')
