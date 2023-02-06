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
    TEST_CONFIRMATION_CODE,
    TEST_DEVICE_INFO,
    TEST_OTHER_EXIST_PHONE_NUMBER,
    TEST_PHONE_NUMBER,
    TEST_USER_AGENT,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_yakey_backup_response
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.test.fake_code_generator import CodeGeneratorFaker
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.time import datetime_to_integer_unixtime


YAKEY_BACKUP_PROCESS_NAME = 'yakey_backup'


class BaseYaKeyBackupTestView(BaseBundleTestViews):
    http_headers = dict(
        user_agent=TEST_USER_AGENT,
        user_ip=TEST_USER_IP,
    )

    step = None

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='mobileproxy',
                grants={'allow_yakey_backup': ['*']},
            ),
        )
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('register')
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        self.code_generator_faker = CodeGeneratorFaker()
        self.code_generator_faker.set_return_value(TEST_CONFIRMATION_CODE)
        self.code_generator_faker.start()

        self.setup_statbox_templates()
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

    def setup_blackbox_response(self, is_found=True, updated=None,
                                device_name=TEST_DEVICE_INFO['device_name'], info_only=False):
        self.env.blackbox.set_blackbox_response_value(
            'yakey_backup',
            blackbox_yakey_backup_response(
                is_found=is_found,
                updated=updated or datetime_to_integer_unixtime(DatetimeNow()),
                backup=TEST_BACKUP,
                phone_number=TEST_PHONE_NUMBER.digital,
                device_name=device_name,
                info_only=info_only,
            ),
        )

    def setup_track(self, phone_number=TEST_PHONE_NUMBER, is_confirmed=True, confirmation_method='by_sms',
                    process_name=YAKEY_BACKUP_PROCESS_NAME):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            if process_name:
                track.process_name = process_name
            if phone_number:
                track.phone_confirmation_phone_number_original = phone_number.original
            track.phone_confirmation_is_confirmed = is_confirmed
            track.phone_confirmation_method = confirmation_method

    def tearDown(self):
        self.code_generator_faker.stop()
        self.track_id_generator.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self.code_generator_faker

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='yakey_backup',
            step=self.step,
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            track_id=self.track_id,
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'succeeded',
            _inherit_from=['local_base'],
            status='ok',
        )
        self.env.statbox.bind_entry(
            'check_code',
            _inherit_from=['local_base'],
            action='confirm_phone',
            code_checks_count='0',
        )
        self.env.statbox.bind_entry(
            'phone_confirmed',
            step='check_code',
            _exclude=['uid', 'phone_id', 'operation_id', 'consumer'],
            _inherit_from=['phone_confirmed', 'local_base'],
        )

    def assert_sms_not_sent(self):
        ok_(not len(self.env.yasms.requests))

    def assert_sms_sent(self):
        eq_(len(self.env.yasms.requests), 1)
        self.env.yasms.get_requests_by_method('send_sms')[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
        })

    def assert_db_no_backup_for_number(self, phone_number=TEST_PHONE_NUMBER.digital):
        self.env.db.check_missing(
            'yakey_backups',
            attr='phone_number',
            phone_number=int(phone_number),
            db='passportdbcentral',
        )

    def assert_db_ok(self, phone_number=TEST_PHONE_NUMBER.digital,
                     backup=TEST_BACKUP, queries=None, device_name=None):
        db = 'passportdbcentral'

        self.env.db.check('yakey_backups', 'phone_number', int(phone_number), db=db)
        self.env.db.check('yakey_backups', 'updated', DatetimeNow(), db=db)
        self.env.db.check('yakey_backups', 'backup', backup, db=db)
        self.env.db.check('yakey_backups', 'device_name', device_name, db=db)
        if queries is not None:
            self.env.db.assert_executed_queries_equal(queries, db=db)


class CommonYakeyBackupTestMixin(object):
    def test_invalid_headers(self):
        resp = self.make_request(exclude_headers=['user_ip', 'user_agent'])
        self.assert_error_response(resp, ['ip.empty', 'useragent.empty'])
        eq_(len(self.env.blackbox.requests), 0)
        self.env.statbox.assert_has_written([])

    def test_missing_grants(self):
        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='mobileproxy',
                grants={},
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['access.denied'], status_code=403)
        eq_(len(self.env.blackbox.requests), 0)
        self.env.statbox.assert_has_written([])

    def test_no_process_name_error(self):
        self.setup_track(process_name=None)
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])
        eq_(len(self.env.blackbox.requests), 0)
        self.env.statbox.assert_has_written([])

    def test_wrong_process_name_error(self):
        self.setup_track(process_name='restore')
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])
        eq_(len(self.env.blackbox.requests), 0)
        self.env.statbox.assert_has_written([])

    def test_inconsistent_numbers_error(self):
        self.setup_track(phone_number=TEST_OTHER_EXIST_PHONE_NUMBER)
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])
        eq_(len(self.env.blackbox.requests), 0)
        self.env.statbox.assert_has_written([])

    def test_no_tracked_number_error(self):
        self.setup_track(phone_number=None)
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])
        eq_(len(self.env.blackbox.requests), 0)
        self.env.statbox.assert_has_written([])

    def test_number_not_confirmed_error(self):
        self.setup_track(is_confirmed=False)
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])
        eq_(len(self.env.blackbox.requests), 0)
        self.env.statbox.assert_has_written([])

    def test_number_confirmed_by_flash_call_error(self):
        self.setup_track(confirmation_method='by_flash_call')
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])
        eq_(len(self.env.blackbox.requests), 0)
        self.env.statbox.assert_has_written([])
