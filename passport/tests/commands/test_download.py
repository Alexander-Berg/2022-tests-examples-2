# coding: utf-8

from contextlib import contextmanager
import json

from passport.backend.core.builders.xunistater.faker.fake_xunistater import (
    FakeXunistater,
    TEST_XUNISTATER_OK_RESPONSE,
)
from passport.backend.utils.lock import lock_mock
from passport.backend.vault.api.commands.download import DOWNLOAD_ABC_LOCK_NAME
from passport.backend.vault.api.db import get_db
from passport.backend.vault.api.models import (
    ExternalRecord,
    TvmAppInfo,
    UserInfo,
)
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.fake_abc import (
    FakeABC,
    TEST_ABC_GET_ALL_DEPARTMENTS_RESPONSE,
    TEST_ABC_GET_ALL_PERSONS_RESPONSE,
    TEST_ABC_GET_ALL_ROLES_RESPONSE,
    TEST_ABC_GET_ALL_TVM_APPS_RESPONSE,
)
from passport.backend.vault.api.test.fake_staff import (
    FakeStaff,
    TEST_STAFF_GET_ALL_DEPARTMENTS_RESPONSE,
    TEST_STAFF_GET_ALL_PERSONS_RESPONSE,
)
from passport.backend.vault.api.test.logging_mock import LoggingMock
import yenv


@contextmanager
def yenv_type_mock(type_):
    old_type, yenv.type = yenv.type, type_
    yield
    yenv.type = old_type


class TestDownloadCommands(BaseTestClass):
    fill_database = False

    def setUp(self):
        super(TestDownloadCommands, self).setUp()
        self.runner = self.app.test_cli_runner()

    def assert_xunistater_request_equal(self, request, request_data):
        request.assert_properties_equal(
            url='http://localhost:10281/xpush',
            method='POST',
            post_args=json.dumps(request_data, sort_keys=True),
        )

    def test_check_environment_fail(self):
        invalid_environments = ['test-type', 'development', 'stress']
        for env in invalid_environments:
            with yenv_type_mock(env):
                result = self.runner.invoke(self.cli, ['download', 'abc', '--cron'])
                self.assertEqual(result.exit_code, 3)

    def test_check_environment_ok(self):
        with FakeXunistater() as fake_xunistater:
            fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
            with FakeABC() as fake_abc:
                with self.app.app_context():
                    fake_abc.set_response_value(
                        'get_all_persons',
                        TEST_ABC_GET_ALL_PERSONS_RESPONSE,
                    )
                    fake_abc.set_response_value(
                        'get_all_roles',
                        TEST_ABC_GET_ALL_ROLES_RESPONSE,
                    )
                    fake_abc.set_response_value(
                        'get_all_departments',
                        TEST_ABC_GET_ALL_DEPARTMENTS_RESPONSE,
                    )

                    valid_environments = ['production', 'testing']

                    for env in valid_environments:
                        with lock_mock():
                            with yenv_type_mock(env):
                                result = self.runner.invoke(self.cli, ['download', 'abc', '--cron'])
                                self.assertEqual(result.exit_code, 0)

    def test_locks_ok(self):
        with FakeXunistater() as fake_xunistater:
            fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
            with FakeABC() as fake_abc:
                with self.app.app_context():
                    fake_abc.set_response_value(
                        'get_all_persons',
                        TEST_ABC_GET_ALL_PERSONS_RESPONSE,
                    )
                    fake_abc.set_response_value(
                        'get_all_roles',
                        TEST_ABC_GET_ALL_ROLES_RESPONSE,
                    )
                    fake_abc.set_response_value(
                        'get_all_departments',
                        TEST_ABC_GET_ALL_DEPARTMENTS_RESPONSE,
                    )

                    with lock_mock():
                        with yenv_type_mock('production'):
                            with LoggingMock() as logging_mock:
                                result = self.runner.invoke(self.cli, ['download', 'abc', '--cron'])
                                self.assertEqual(result.exit_code, 0)
                            self.assertListEqual(
                                logging_mock.getLogger('info_logger').entries,
                                [('ABC: Acquire lock "download_abc" ("zookeeper", "[\'localhost\']")',
                                  'INFO',
                                  None,
                                  None),
                                 ('ABC: Lock acquired "download_abc" ("zookeeper", "[\'localhost\']")',
                                  'INFO',
                                  None,
                                  None),
                                 ('ABC: started downloading services...', 'INFO', None, None),
                                 ('ABC: started downloading persons and scopes...', 'INFO', None, None),
                                 (u"ABC: get_all_persons_and_scopes fetched an unknown members scope. Service id 14. Scope: "
                                  u"{'id': 17, 'name': {'ru': u'\\u0423\\u043f\\u0440\\u0430\\u0432\\u043b\\u0435\\u043d\\u0438\\u0435 TVM', "
                                  u"'en': u'TVM management'}, 'slug': u'tvm_management'}",
                                  'WARNING',
                                  None,
                                  None),
                                 (u"ABC: get_all_persons_and_scopes fetched an unknown members role. Service id 14. Role: "
                                  u"{'scope': {'id': 17, 'name': {'ru': u'\\u0423\\u043f\\u0440\\u0430\\u0432\\u043b\\u0435\\u043d\\u0438\\u0435 TVM', "
                                  u"'en': u'TVM management'}, 'slug': u'tvm_management'}, 'code': u'tvm_manager', 'id': 630, 'service': None, "
                                  u"'name': {'ru': u'TVM \\u043c\\u0435\\u043d\\u0435\\u0434\\u0436\\u0435\\u0440', 'en': u'TVM manager'}}",
                                  'WARNING',
                                  None,
                                  None),
                                 ('ABC: inserting...', 'INFO', None, None),
                                 ('ABC: upserted chunk of %s external records', 'INFO', (12,), None),
                                 ('ABC: upserted chunk of %s services', 'INFO', (20,), None),
                                 ('ABC: upserted 12 new external records, removed 0 old external records, deactivated 0 old services, upserted 20 services ',
                                  'INFO',
                                  None,
                                  None),
                                 ('ABC: Release lock "download_abc" ("zookeeper", "[\'localhost\']")',
                                  'INFO',
                                  None,
                                  None),
                                 ('ABC: push metrics to the Xunistater', 'INFO', None, None),
                                 (u"ABC: xunistater result: {u'status': u'OK'}", 'INFO', None, None)],
                            )

    def test_locks_fail(self):
        with FakeXunistater() as fake_xunistater:
            fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
            with FakeABC() as fake_abc:
                with self.app.app_context():
                    fake_abc.set_response_value(
                        'get_all_persons',
                        TEST_ABC_GET_ALL_PERSONS_RESPONSE,
                    )
                    fake_abc.set_response_value(
                        'get_all_roles',
                        TEST_ABC_GET_ALL_ROLES_RESPONSE,
                    )
                    fake_abc.set_response_value(
                        'get_all_departments',
                        TEST_ABC_GET_ALL_DEPARTMENTS_RESPONSE,
                    )

                    with lock_mock() as lock_manager:
                        ext_lock = lock_manager.lock(DOWNLOAD_ABC_LOCK_NAME)
                        with ext_lock:
                            with yenv_type_mock('production'):
                                with LoggingMock() as logging_mock:
                                    result = self.runner.invoke(self.cli, ['download', 'abc', '--cron'])
                                    self.assertEqual(result.exit_code, 0)
                                self.assertListEqual(
                                    logging_mock.getLogger('info_logger').entries,
                                    [('ABC: Acquire lock "download_abc" ("zookeeper", "[\'localhost\']")',
                                      'INFO',
                                      None,
                                      None),
                                     ('ABC: Lock is not acquired "download_abc" ("zookeeper", "[\'localhost\']")',
                                      'INFO',
                                      None,
                                      None),
                                     ('ABC: skip download', 'INFO', None, None),
                                     ('ABC: push metrics to the Xunistater', 'INFO', None, None),
                                     (u"ABC: xunistater result: {u'status': u'OK'}", 'INFO', None, None)],
                                )

                    self.assertEqual(len(fake_xunistater.requests), 1)
                    self.assert_xunistater_request_equal(
                        fake_xunistater.requests[0],
                        {
                            'abc_fetched_axxx': {'value': 0},
                            'abc_errors_axxx': {'value': 0},
                            'abc_new_department_infos_axxx': {'value': 0},
                            'abc_new_external_records_axxx': {'value': 0},
                            'abc_old_department_infos_axxx': {'value': 0},
                            'abc_old_external_records_axxx': {'value': 0},
                        },
                    )

    def test_download_abc(self):
        with FakeXunistater() as fake_xunistater:
            fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
            with FakeABC() as fake_abc:
                with self.app.app_context():
                    fake_abc.set_response_value(
                        'get_all_persons',
                        TEST_ABC_GET_ALL_PERSONS_RESPONSE,
                    )
                    fake_abc.set_response_value(
                        'get_all_roles',
                        TEST_ABC_GET_ALL_ROLES_RESPONSE,
                    )
                    fake_abc.set_response_value(
                        'get_all_departments',
                        TEST_ABC_GET_ALL_DEPARTMENTS_RESPONSE,
                    )

                    with LoggingMock() as logging_mock:
                        result = self.runner.invoke(self.cli, ['download', 'abc'], catch_exceptions=False)
                    self.assertEqual(result.exit_code, 0)

                    self.assertListEqual(
                        logging_mock.getLogger('info_logger').entries,
                        [('ABC: Skip lock', 'INFO', None, None),
                         ('ABC: started downloading services...', 'INFO', None, None),
                         ('ABC: started downloading persons and scopes...', 'INFO', None, None),
                         (u"ABC: get_all_persons_and_scopes fetched an unknown members scope. Service id 14. Scope: "
                          u"{'id': 17, 'name': {'ru': u'\\u0423\\u043f\\u0440\\u0430\\u0432\\u043b\\u0435\\u043d\\u0438\\u0435 TVM', "
                          u"'en': u'TVM management'}, 'slug': u'tvm_management'}",
                          'WARNING',
                          None,
                          None),
                         (u"ABC: get_all_persons_and_scopes fetched an unknown members role. Service id 14. Role: "
                          u"{'scope': {'id': 17, 'name': {'ru': u'\\u0423\\u043f\\u0440\\u0430\\u0432\\u043b\\u0435\\u043d\\u0438\\u0435 TVM', "
                          u"'en': u'TVM management'}, 'slug': u'tvm_management'}, 'code': u'tvm_manager', 'id': 630, 'service': None, "
                          u"'name': {'ru': u'TVM \\u043c\\u0435\\u043d\\u0435\\u0434\\u0436\\u0435\\u0440', 'en': u'TVM manager'}}",
                          'WARNING',
                          None,
                          None),
                         ('ABC: inserting...', 'INFO', None, None),
                         ('ABC: upserted chunk of %s external records', 'INFO', (12,), None),
                         ('ABC: upserted chunk of %s services', 'INFO', (20,), None),
                         ('ABC: upserted 12 new external records, removed 0 old external records, deactivated 0 old services, upserted 20 services ',
                          'INFO',
                           None,
                           None),
                         ('ABC: push metrics to the Xunistater', 'INFO', None, None),
                         (u"ABC: xunistater result: {u'status': u'OK'}", 'INFO', None, None)],
                    )
                    self.assertEqual(
                        ExternalRecord.query
                        .filter(
                            ExternalRecord.external_type == 'abc',
                            ExternalRecord.external_id == 14,
                            ExternalRecord.uid == 1120000000038274,
                        ).count(),
                        2,
                    )
                    self.assertEqual(len(fake_xunistater.requests), 1)
                    self.assert_xunistater_request_equal(
                        fake_xunistater.requests[0],
                        {
                            'abc_fetched_axxx': {'value': 1},
                            'abc_errors_axxx': {'value': 0},
                            'abc_new_department_infos_axxx': {'value': 20},
                            'abc_new_external_records_axxx': {'value': 12},
                            'abc_old_department_infos_axxx': {'value': 0},
                            'abc_old_external_records_axxx': {'value': 0},
                        }
                    )

    def test_download_staff(self):
        with FakeXunistater() as fake_xunistater:
            fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
            with FakeStaff() as fake_staff:
                with self.app.app_context():
                    invalid_user = UserInfo(
                        uid=99900000000011,
                        login='ppodolsky',
                        keys='[]',
                    )
                    get_db().session.add(invalid_user)
                    get_db().session.commit()

                    self.assertEqual(
                        UserInfo.query.filter(UserInfo.login == 'ppodolsky').one().uid,
                        99900000000011,
                    )

                    fake_staff.set_response_value(
                        'get_all_persons',
                        json.dumps(TEST_STAFF_GET_ALL_PERSONS_RESPONSE),
                    )
                    fake_staff.set_response_value(
                        'get_all_departments',
                        json.dumps(TEST_STAFF_GET_ALL_DEPARTMENTS_RESPONSE),
                    )
                    with LoggingMock() as logging_mock:
                        result = self.runner.invoke(self.cli, ['download', 'staff'])
                    self.assertEqual(result.exit_code, 0)

                    self.assertListEqual(
                        logging_mock.getLogger('info_logger').entries,
                        [('Staff: Skip lock', 'INFO', None, None),
                         ('Staff: started downloading departments...', 'INFO', None, None),
                         ('Staff: started downloading persons...', 'INFO', None, None),
                         ('Staff: inserting...', 'INFO', None, None),
                         ('Staff: upserted chunk of %s external records', 'INFO', (40,), None),
                         ('Staff: upserted chunk of %s users', 'INFO', (8,), None),
                         ('Staff: upserted chunk of %s departments', 'INFO', (53,), None),
                         ('Staff: upserted 40 new external records, removed 0 old external records, upserted 8 users, upserted 53 departments ',
                          'INFO',
                          None,
                          None),
                         ('Staff: push metrics to the Xunistater', 'INFO', None, None),
                         (u"Staff: xunistater result: {u'status': u'OK'}", 'INFO', None, None)],
                    )
                    self.assertEqual(
                        ExternalRecord.query
                        .filter(
                            ExternalRecord.external_type == 'staff',
                        ).count(),
                        40,
                    )
                    self.assertEqual(
                        UserInfo.query.count(),
                        8,
                    )

                    self.assertEqual(
                        UserInfo.query.filter(UserInfo.login == 'ppodolsky').one().uid,
                        99900000000011,
                    )
                    self.assertEqual(len(fake_xunistater.requests), 1)
                    self.assert_xunistater_request_equal(
                        fake_xunistater.requests[0],
                        {
                            'staff_fetched_axxx': {'value': 1},
                            'staff_errors_axxx': {'value': 0},
                            'staff_new_department_infos_axxx': {'value': 53},
                            'staff_new_external_records_axxx': {'value': 40},
                            'staff_new_user_infos_axxx': {'value': 8},
                            'staff_old_external_records_axxx': {'value': 0},
                        }
                    )

    def test_download_tvm_apps(self):
        with FakeXunistater() as fake_xunistater:
            fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))

            with FakeABC() as fake_abc:
                with self.app.app_context():
                    fake_abc.set_response_value(
                        'get_all_tvm_apps',
                        json.dumps(TEST_ABC_GET_ALL_TVM_APPS_RESPONSE),
                    )

                    with LoggingMock() as logging_mock:
                        result = self.runner.invoke(self.cli, ['download', 'tvm_apps'], catch_exceptions=False)
                    self.assertEqual(result.exit_code, 0)

                    self.assertListEqual(
                        logging_mock.getLogger('info_logger').entries,
                        [('TVM apps: Skip lock', 'INFO', None, None),
                         ('TVM apps: started downloading apps...', 'INFO', None, None),
                         ('TVM apps: inserting...', 'INFO', None, None),
                         ('TVM apps: upserted chunk of %s records', 'INFO', (14,), None),
                         ('TVM apps: push metrics to the Xunistater', 'INFO', None, None),
                         (u"TVM apps: xunistater result: {u'status': u'OK'}", 'INFO', None, None)],
                    )
                    self.assertListEqual(
                        map(
                            repr,
                            TvmAppInfo.query.order_by(TvmAppInfo.tvm_client_id),
                        ),
                        [
                            '<TvmAppInfo #2000079 name:"\xd0\x9f\xd0\xb0\xd1\x81\xd0\xbf\xd0\xbe\xd1\x80\xd1\x82 [testing]", abc_state:"granted">',
                            '<TvmAppInfo #2000196 name:"TestABC2", abc_state:"deprived">',
                            '<TvmAppInfo #2000201 name:"sandy-moodle-dev", abc_state:"granted">',
                            '<TvmAppInfo #2000220 name:"TestABC3", abc_state:"deprived">',
                            '<TvmAppInfo #2000230 name:"push-client-passport", abc_state:"granted">',
                            '<TvmAppInfo #2000232 name:"Sentry", abc_state:"granted">',
                            '<TvmAppInfo #2000347 name:"\xd0\xa2\xd0\xb5\xd1\x81\xd1\x82\xd0\xbe\xd0\xb2\xd0\xbe\xd0\xb5 '
                            '\xd1\x82\xd0\xb2\xd0\xbc \xd0\xbf\xd1\x80\xd0\xb8\xd0\xbb\xd0\xbe\xd0\xb6\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb5 3", abc_state:"granted">',
                            '<TvmAppInfo #2000348 name:"test_tvm25", abc_state:"granted">',
                            '<TvmAppInfo #2000353 name:"TestClientToBeDeleted", abc_state:"deprived">',
                            '<TvmAppInfo #2000354 name:"\xd0\x9f\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd0\xba\xd0\xb0 '
                            '\xd1\x81\xd0\xbe\xd0\xb7\xd0\xb4\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x8f TVM2", abc_state:"granted">',
                            '<TvmAppInfo #2000355 name:"passport_likers3", abc_state:"granted">',
                            '<TvmAppInfo #2000367 name:"social api (dev)", abc_state:"granted">',
                            '<TvmAppInfo #2000368 name:"test-moodle", abc_state:"granted">',
                            '<TvmAppInfo #2000371 name:"Test app", abc_state:"granted">',
                        ],
                    )
                    self.assertEqual(len(fake_xunistater.requests), 1)
                    self.assert_xunistater_request_equal(
                        fake_xunistater.requests[0],
                        {
                            'tvm_apps_fetched_axxx': {'value': 1},
                            'tvm_apps_errors_axxx': {'value': 0},
                            'tvm_apps_download_apps_axxx': {'value': 14},
                        }
                    )
