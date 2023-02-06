# -*- coding: utf-8 -*-

from datetime import timedelta

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.models.phones.faker import (
    assert_secure_phone_bound,
    build_account,
    build_phone_secured,
)
from passport.backend.core.test.consts import *
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import deep_merge
from passport.backend.utils.time import datetime_to_integer_unixtime as to_unixtime


TIME_DELTA = timedelta(seconds=1)


@with_settings_hosts()
class TestUpdatePhone(BaseBundleTestViews):
    def setUp(self):
        super(TestUpdatePhone, self).setUp()

        self.env = ViewsTestEnvironment()
        self.env.start()

        self._assign_grants()

    def tearDown(self):
        self.env.stop()
        del self.env
        super(TestUpdatePhone, self).tearDown()

    def _assign_grants(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={'internal': ['update_phone']}))

    def _build_account(self, login=TEST_YANDEX_TEAM_LOGIN1, enabled=True,
                       phone_number=TEST_PHONE_NUMBER1, phone_created_at=TEST_DATETIME1,
                       phone_confirmed_at=TEST_DATETIME1, phone_admitted_at=TEST_DATETIME1):
        userinfo = dict(
            uid=TEST_UID1,
            login=login,
            enabled=enabled,
        )

        phone_dict = build_phone_secured(
            phone_id=TEST_PHONE_ID1,
            phone_number=phone_number.e164,
            phone_created=phone_created_at,
            phone_bound=TEST_DATETIME1,
            phone_confirmed=phone_confirmed_at,
            phone_secured=TEST_DATETIME1,
            phone_admitted=phone_admitted_at,
        )
        userinfo = deep_merge(userinfo, phone_dict)
        return dict(userinfo=userinfo)

    def _setup_account(self, account):
        build_account(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            **account['userinfo']
        )

    def _make_request(self, args=None):
        args = args or {}

        defaults = dict(uid=TEST_UID1, phone_id=TEST_PHONE_ID1)

        for arg in defaults:
            args.setdefault(arg, defaults[arg])

        return self.env.client.post('/1/bundle/test/update_phone/', query_string=dict(consumer='dev'), data=args)

    def _assert_phone_attrs_equal(self, updated_attrs):
        attrs = dict(
            created=TEST_DATETIME1,
            bound=TEST_DATETIME1,
            confirmed=TEST_DATETIME1,
            secured=TEST_DATETIME1,
            admitted=TEST_DATETIME1,
        )
        attrs.update(updated_attrs)

        assert_secure_phone_bound.check_db(
            db_faker=self.env.db,
            uid=TEST_UID1,
            phone_attributes=dict(attrs, id=TEST_PHONE_ID1),
        )

    def _assert_phone_not_updated(self):
        self._assert_phone_attrs_equal({})

    def _assert_update_phone_in_history(self, attrs):
        entries = {
            'action': 'update_phone_attributes',
            'phone.10.number': TEST_PHONE_NUMBER1.e164,
            'phone.10.action': 'changed',
            'consumer': 'dev',
        }
        for attr in attrs:
            name = 'phone.10.%s' % attr
            entries[name] = str(to_unixtime(attrs[attr]))
        self.env.event_logger.assert_events_are_logged(entries)

    def test_account_disabled(self):
        self._setup_account(self._build_account(enabled=False))

        rv = self._make_request()

        self.assert_ok_response(rv)

    def test_request_phones(self):
        self._setup_account(self._build_account())

        self._make_request()

        request = self.env.blackbox.requests[0]
        request.assert_post_data_contains(
            dict(
                getphones='all',
                phone_attributes='1,2,3,4,5,6,109',
                getphonebindings='all',
                getphoneoperations='1',
            ),
        )
        request.assert_contains_attributes({'phones.secure'})

    def test_phone_not_found(self):
        self._setup_account(self._build_account())

        rv = self._make_request(dict(phone_id=TEST_PHONE_ID2))

        self.assert_error_response(rv, ['phone.not_found'])
        self._assert_phone_not_updated()

    def test_test_login_and_real_phone(self):
        self._setup_account(
            self._build_account(
                login=TEST_YANDEX_TEAM_LOGIN1,
                phone_number=TEST_PHONE_NUMBER1,
            ),
        )

        rv = self._make_request()

        self.assert_ok_response(rv)

    def test_not_test_login__but_fake_phone(self):
        self._setup_account(
            self._build_account(
                login=TEST_LOGIN1,
                phone_number=TEST_PHONE_NUMBER_FAKE1,
            ),
        )

        rv = self._make_request()

        self.assert_ok_response(rv)

    def test_not_test_login_and_not_fake_phone(self):
        self._setup_account(
            self._build_account(
                login=TEST_LOGIN1,
                phone_number=TEST_PHONE_NUMBER1,
            ),
        )

        rv = self._make_request()

        self.assert_error_response(rv, ['phone.not_updatable'])
        self._assert_phone_not_updated()

    def test_update_created(self):
        self._setup_account(self._build_account())

        rv = self._make_request(dict(created=to_unixtime(TEST_DATETIME1 - TIME_DELTA)))

        self.assert_ok_response(rv)
        self._assert_phone_attrs_equal(dict(created=TEST_DATETIME1 - TIME_DELTA))

        self._assert_update_phone_in_history(dict(created=TEST_DATETIME1 - TIME_DELTA))
        self.env.statbox.assert_has_written([])

    def test_update_created__not_admitted(self):
        self._setup_account(self._build_account(phone_admitted_at=None))

        rv = self._make_request(dict(created=to_unixtime(TEST_DATETIME1 - TIME_DELTA)))

        self.assert_ok_response(rv)
        self._assert_phone_attrs_equal(dict(created=TEST_DATETIME1 - TIME_DELTA, admitted=None))

    def test_update_bound(self):
        self._setup_account(
            self._build_account(
                phone_created_at=TEST_DATETIME1 - 2 * TIME_DELTA,
            ),
        )

        rv = self._make_request(dict(bound=to_unixtime(TEST_DATETIME1 - TIME_DELTA)))

        self.assert_ok_response(rv)
        self._assert_phone_attrs_equal(
            dict(
                bound=TEST_DATETIME1 - TIME_DELTA,
                created=TEST_DATETIME1 - 2 * TIME_DELTA,
            ),
        )

    def test_update_confirmed(self):
        self._setup_account(self._build_account())

        rv = self._make_request(dict(confirmed=to_unixtime(TEST_DATETIME1 + TIME_DELTA)))

        self.assert_ok_response(rv)
        self._assert_phone_attrs_equal(dict(confirmed=TEST_DATETIME1 + TIME_DELTA))

    def test_update_created_and_confirmed(self):
        self._setup_account(self._build_account())

        rv = self._make_request(dict(created=to_unixtime(TEST_DATETIME1 - TIME_DELTA), confirmed=to_unixtime(TEST_DATETIME1 + TIME_DELTA)))

        self.assert_ok_response(rv)
        self._assert_phone_attrs_equal(dict(created=TEST_DATETIME1 - TIME_DELTA, confirmed=TEST_DATETIME1 + TIME_DELTA))

    def test_update_secured(self):
        self._setup_account(
            self._build_account(
                phone_confirmed_at=TEST_DATETIME1 + 2 * TIME_DELTA,
            ),
        )

        rv = self._make_request(dict(secured=to_unixtime(TEST_DATETIME1 + TIME_DELTA)))

        self.assert_ok_response(rv)
        self._assert_phone_attrs_equal(
            dict(
                secured=TEST_DATETIME1 + TIME_DELTA,
                confirmed=TEST_DATETIME1 + 2 * TIME_DELTA,
            ),
        )

    def test_update_admitted(self):
        self._setup_account(self._build_account())

        rv = self._make_request(dict(admitted=to_unixtime(TEST_DATETIME1 + TIME_DELTA)))

        self.assert_ok_response(rv)
        self._assert_phone_attrs_equal(dict(admitted=TEST_DATETIME1 + TIME_DELTA))

    def test_update_admitted__not_admitted(self):
        self._setup_account(self._build_account(phone_admitted_at=None))

        rv = self._make_request(dict(admitted=to_unixtime(TEST_DATETIME1 + TIME_DELTA)))

        self.assert_error_response(rv, ['admitted.must_be_null'])
        self._assert_phone_attrs_equal(dict(admitted=None))

    def test_created_greater_than_bound(self):
        self._setup_account(self._build_account())

        rv = self._make_request(dict(bound=to_unixtime(TEST_DATETIME1 - TIME_DELTA)))

        self.assert_error_response(rv, ['created.must_be_less_or_equal_than_bound'])
        self._assert_phone_not_updated()

    def test_no_timestamps(self):
        self._setup_account(self._build_account())

        rv = self._make_request(
            dict(
                created=None,
                bound=None,
                confirmed=None,
                secured=None,
                admitted=None,
            ),
        )

        self.assert_ok_response(rv)
        self._assert_phone_not_updated()
        self.env.event_logger.assert_events_are_logged({})
        self.env.statbox.assert_has_written([])

    def test_no_uid(self):
        rv = self._make_request(dict(uid=None))
        self.assert_error_response(rv, ['uid.empty'])

    def test_no_phone_id(self):
        rv = self._make_request(dict(phone_id=None))
        self.assert_error_response(rv, ['phone_id.empty'])
