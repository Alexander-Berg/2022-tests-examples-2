# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_FAKE_PHONE_NUMBER,
    TEST_LOGIN,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER1,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_IP,
    TEST_YANDEX_TEST_LOGIN,
)
from passport.backend.core.builders.blackbox import BLACKBOX_PASSWORD_BAD_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_login_response,
    blackbox_phone_bindings_response,
)
from passport.backend.core.models.phones.faker import (
    assert_secure_phone_bound,
    assert_simple_phone_bound,
    build_account,
    build_phone_secured,
    PhoneIdGeneratorFaker,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import deep_merge


@with_settings_hosts(
    IS_BIND_TEST_PHONE_TO_NONTEST_ACCOUNT_ALLOWED=False,
)
class TestConfirmAndBindPhone(BaseBundleTestViews):
    default_url = '/1/bundle/test/confirm_and_bind_phone/'
    consumer = 'dev'
    http_method = 'POST'
    http_headers = {
        'user_agent': TEST_USER_AGENT,
        'user_ip': TEST_USER_IP,
    }
    http_query_args = {
        'uid': TEST_UID,
        'password': 'testpassword',
        'number': TEST_FAKE_PHONE_NUMBER.e164,
        'secure': True,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)
        self.phone_id_generator_faker = PhoneIdGeneratorFaker()
        self.phone_id_generator_faker.start()
        self.phone_id_generator_faker.set_list([TEST_PHONE_ID1])
        self.env.grants.set_grants_return_value(mock_grants(grants={'internal': ['bind_test_phone']}))
        self.setup_statbox_templates()

    def tearDown(self):
        self.phone_id_generator_faker.stop()
        self.track_id_generator.stop()
        self.env.stop()
        del self.phone_id_generator_faker
        del self.track_id_generator
        del self.track_manager
        del self.track_id
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            track_id=self.track_id,
            mode='bind_test_phone',
            ip=TEST_USER_IP,
            consumer='dev',
            user_agent=TEST_USER_AGENT,
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'local_base',
            number=TEST_FAKE_PHONE_NUMBER.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'password_not_matched',
            operation='check_password',
            error='password.not_matched',
        )
        self.env.statbox.bind_entry(
            'simple_bind_operation_created',
            _inherit_from=['simple_bind_operation_created', 'local_base'],
            _exclude=['mode', 'step', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'secure_bind_operation_created',
            _inherit_from=['secure_bind_operation_created', 'local_base'],
            _exclude=['mode', 'step', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'local_account_modification',
            _exclude=['track_id', 'step', 'number', 'mode'],
            _inherit_from=['frodo_karma', 'local_base'],
            action='bind_test_phone',
            login=TEST_YANDEX_TEST_LOGIN,
            registration_datetime='-',
            new='6000',
            old='0',
        )
        self.env.statbox.bind_entry(
            'phone_confirmed',
            _inherit_from=['phone_confirmed', 'local_base'],
            code_checks_count='0',
        )
        self.env.statbox.bind_entry(
            'simple_phone_bound',
            _inherit_from=['simple_phone_bound', 'local_base'],
        )
        self.env.statbox.bind_entry(
            'secure_phone_bound',
            _inherit_from=['secure_phone_bound', 'local_base'],
        )
        self.env.statbox.bind_entry(
            'account_phones_secure',
            _inherit_from=['account_modification', 'local_base'],
            _exclude=['mode', 'step', 'track_id', 'number'],
            entity='phones.secure',
            operation='created',
            old='-',
            old_entity_id='-',
            new=TEST_FAKE_PHONE_NUMBER.masked_format_for_statbox,
            new_entity_id='1',
        )

    def _build_account(self, login=TEST_YANDEX_TEST_LOGIN, enabled=True):
        return dict(
            uid=TEST_UID,
            login=login,
            attributes={'password.encrypted': '1:testpassword'},
            enabled=enabled,
        )

    def setup_blackbox_responses(self, account, with_phone=False):
        if with_phone:
            phone_args = build_phone_secured(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_FAKE_PHONE_NUMBER.e164,
            )
            account = deep_merge(account, phone_args)

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**account),
        )
        build_account(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            **account
        )

    def assert_blackbox_is_called(self, call_count=1):
        eq_(len(self.env.blackbox.requests), call_count)

    def assert_secure_phone_is_bound(self, uid=TEST_UID):
        assert_secure_phone_bound.check_db(
            self.env.db,
            uid,
            {'id': TEST_PHONE_ID1, 'secured': DatetimeNow(), 'confirmed': DatetimeNow()},
        )

    def assert_simple_phone_is_bound(self, uid=TEST_UID):
        assert_simple_phone_bound.check_db(
            self.env.db,
            uid,
            {'id': TEST_PHONE_ID1, 'confirmed': DatetimeNow()},
        )

    def assert_statbox_is_ok(self, secure=True):
        if secure:
            self.env.statbox.assert_has_written([
                self.env.statbox.entry('secure_bind_operation_created'),
                self.env.statbox.entry('account_phones_secure'),
                self.env.statbox.entry('local_account_modification', action='confirm_and_bind_secure'),
                self.env.statbox.entry('phone_confirmed'),
                self.env.statbox.entry('secure_phone_bound'),
            ])
        else:
            self.env.statbox.assert_has_written([
                self.env.statbox.entry('simple_bind_operation_created'),
                self.env.statbox.entry('local_account_modification', action='confirm_and_bind'),
                self.env.statbox.entry('phone_confirmed'),
                self.env.statbox.entry('simple_phone_bound'),
            ])

    def test_success_bind_secure_phone(self):
        self.setup_blackbox_responses(self._build_account())

        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_blackbox_is_called(call_count=4)
        self.env.blackbox.requests[0].assert_post_data_contains({
            'method': 'userinfo',
            'uid': TEST_UID,
        })
        self.env.blackbox.requests[1].assert_post_data_contains({
            'method': 'login',
            'uid': TEST_UID,
            'password': 'testpassword',
        })
        self.assert_secure_phone_is_bound()
        self.assert_statbox_is_ok()

    def test_success_bind_simple_phone(self):
        self.setup_blackbox_responses(self._build_account())

        rv = self.make_request(query_args={'secure': False})

        self.assert_ok_response(rv)
        self.assert_blackbox_is_called(call_count=4)
        self.env.blackbox.requests[0].assert_post_data_contains({
            'method': 'userinfo',
            'uid': TEST_UID,
        })
        self.env.blackbox.requests[1].assert_post_data_contains({
            'method': 'login',
            'uid': TEST_UID,
            'password': 'testpassword',
        })
        self.assert_simple_phone_is_bound()
        self.assert_statbox_is_ok(secure=False)

    def test_no_uid_in_form(self):
        self.setup_blackbox_responses(self._build_account())

        rv = self.make_request(exclude_args=['uid'])

        self.assert_error_response(rv, [u'uid.empty'])

    def test_no_number_in_form(self):
        self.setup_blackbox_responses(self._build_account())

        rv = self.make_request(exclude_args=['number'])

        self.assert_error_response(rv, [u'number.empty'])

    def test_no_password_in_form(self):
        self.setup_blackbox_responses(self._build_account())

        rv = self.make_request(exclude_args=['password'])

        self.assert_error_response(rv, [u'password.empty'])

    def test_no_secure_in_form(self):
        self.setup_blackbox_responses(self._build_account())

        rv = self.make_request(exclude_args=['secure'])

        self.assert_error_response(rv, [u'secure.empty'])

    def test_account_disabled(self):
        self.setup_blackbox_responses(self._build_account(enabled=False))

        rv = self.make_request()

        self.assert_error_response(rv, [u'account.disabled'])
        self.assert_blackbox_is_called(call_count=1)
        self.env.statbox.assert_has_written([])

    def test_wrong_password(self):
        self.setup_blackbox_responses(self._build_account())
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=BLACKBOX_PASSWORD_BAD_STATUS,
                uid=TEST_UID,
            ),
        )

        rv = self.make_request()

        self.assert_error_response(rv, [u'password.not_matched'])
        self.assert_blackbox_is_called(call_count=2)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('password_not_matched'),
        ])

    def test_not_test_number(self):
        self.setup_blackbox_responses(self._build_account())

        rv = self.make_request(query_args={'number': TEST_PHONE_NUMBER1.e164})  # номер не начинается с +7000

        self.assert_error_response(rv, [u'phone.not_test_number'])
        self.assert_blackbox_is_called(call_count=0)
        self.env.statbox.assert_has_written([])

    def test_not_test_login(self):
        self.setup_blackbox_responses(self._build_account(login=TEST_LOGIN))  # логин не начинается с тестового префикса

        rv = self.make_request()

        self.assert_error_response(rv, [u'account.not_test_account'])
        self.assert_blackbox_is_called(call_count=1)
        self.env.statbox.assert_has_written([])

    def test_should_get_error_when_secure_phone_is_already_bound(self):
        self.setup_blackbox_responses(self._build_account(), with_phone=True)

        rv = self.make_request()

        self.assert_error_response(rv, [u'phone_secure.already_exists'])
        self.assert_blackbox_is_called(call_count=2)
        self.env.statbox.assert_has_written([])

    def test_should_get_error_when_bind_simple_phone_that_is_bound_as_secure(self):
        self.setup_blackbox_responses(self._build_account(), with_phone=True)

        rv = self.make_request(query_args={'secure': False})

        self.assert_error_response(rv, [u'phone_secure.bound_and_confirmed'])
        self.assert_blackbox_is_called(call_count=2)
        self.env.statbox.assert_has_written([])
