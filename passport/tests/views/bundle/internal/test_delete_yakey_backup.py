# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_BACKUP,
    TEST_DATETIME_UPDATED,
    TEST_DEVICE_INFO,
    TEST_PHONE_NUMBER,
    TEST_TIMESTAMP_UPDATED,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_yakey_backup_response
from passport.backend.core.db.schemas import yakey_backups_table as bck
from passport.backend.core.models.yakey_backup import YaKeyBackup
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts(BLACKBOX='localhost')
class TestDeleteYakeyBackup(BaseBundleTestViews):
    default_url = '/1/bundle/test/yakey_backup/'
    http_method = 'delete'
    http_query_args = {
        'number': TEST_PHONE_NUMBER.e164,
        'consumer': 'dev',
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='dev',
                grants={'internal': ['delete_yakey_backup']},
            ),
        )

    def setup_blackbox_response(self, is_found=True):
        backup_response = {
            'backup': TEST_BACKUP,
            'phone_number': TEST_PHONE_NUMBER.digital,
            'updated': TEST_TIMESTAMP_UPDATED,
            'device_name': TEST_DEVICE_INFO['device_name'],
        }
        self.env.blackbox.set_blackbox_response_value(
            'yakey_backup',
            blackbox_yakey_backup_response(
                is_found=is_found,
                **backup_response
            ),
        )
        backup = YaKeyBackup().parse(backup_response)
        self.env.db._serialize_to_eav(backup)

    def tearDown(self):
        self.env.stop()
        del self.env

    def assert_db_no_backup_for_number(self, queries=None):
        db = 'passportdbcentral'

        self.env.db.check_missing(
            'yakey_backups',
            attr='phone_number',
            phone_number=int(TEST_PHONE_NUMBER.digital),
            db='passportdbcentral',
        )
        if queries is not None:
            self.env.db.assert_executed_queries_equal(queries, db=db)

    def assert_backup_for_number(self):
        db = 'passportdbcentral'

        self.env.db.check('yakey_backups', 'phone_number', int(TEST_PHONE_NUMBER.digital), db=db)
        self.env.db.check('yakey_backups', 'updated', TEST_DATETIME_UPDATED, db=db)
        self.env.db.check('yakey_backups', 'backup', TEST_BACKUP, db=db)
        self.env.db.check('yakey_backups', 'device_name', TEST_DEVICE_INFO['device_name'], db=db)

    def test_invalid_form(self):
        resp = self.make_request(exclude_args=['number'])
        self.assert_error_response(resp, ['number.empty'])

    def test_ok(self):
        self.setup_blackbox_response(is_found=True)
        self.assert_backup_for_number()

        resp = self.make_request()
        self.assert_ok_response(resp)

        self.assert_db_no_backup_for_number(
            queries=[bck.delete().where(bck.c.phone_number == int(TEST_PHONE_NUMBER.digital))],
        )
        eq_(len(self.env.blackbox.requests), 1)
        eq_(len(self.env.blackbox.get_requests_by_method('yakey_backup')), 1)

    def test_not_found(self):
        self.setup_blackbox_response(is_found=False)
        self.assert_backup_for_number()

        resp = self.make_request()
        self.assert_error_response(resp, ['yakey_backup.not_found'])

        self.assert_backup_for_number()
        eq_(len(self.env.blackbox.requests), 1)
        eq_(len(self.env.blackbox.get_requests_by_method('yakey_backup')), 1)
        ok_(not self.env.db.query_count('passportdbcentral'))
