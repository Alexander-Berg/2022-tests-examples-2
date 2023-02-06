# -*- coding: utf-8 -*-

from datetime import timedelta

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.eav_type_mapping import (
    EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_ANT,
    EXTENDED_ATTRIBUTES_EMAIL_TYPE,
)
from passport.backend.core.models.phones.faker import build_account
from passport.backend.core.test.consts import *
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.utils.common import deep_merge
from passport.backend.utils.time import datetime_to_integer_unixtime as to_unixtime


TIME_DELTA = timedelta(seconds=1)


@with_settings_hosts()
class TestUpdateEmail(BaseBundleTestViews):
    def setUp(self):
        super(TestUpdateEmail, self).setUp()

        self.env = ViewsTestEnvironment()
        self.env.start()

        self._assign_grants()

        self.env.statbox.bind_entry(
            'email_updated',
            event='account_modification',
            operation='updated',
            entity='account.emails',
            email_id=str(TEST_EMAIL_ID1),
            old=mask_email_for_statbox(TEST_EMAIL1),
            new=mask_email_for_statbox(TEST_EMAIL1),
            is_suitable_for_restore='1',
            uid=str(TEST_UID1),
            ip='127.0.0.1',
            user_agent='-',
            consumer='dev',
        )

    def tearDown(self):
        self.env.stop()
        del self.env
        super(TestUpdateEmail, self).tearDown()

    def _assign_grants(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={'internal': ['update_email']}))

    def _build_account(self, login=TEST_YANDEX_TEAM_LOGIN1, enabled=True, email=TEST_EMAIL1,
                       email_confirmed_at=to_unixtime(TEST_DATETIME1)):
        userinfo = dict(
            uid=TEST_UID1,
            login=login,
            enabled=enabled,
        )

        email_dict = dict(
            email_attributes=[
                dict(
                    id=TEST_EMAIL_ID1,
                    attributes={
                        EMAIL_ANT['address']: email,
                        EMAIL_ANT['created']: to_unixtime(TEST_DATETIME1),
                        EMAIL_ANT['bound']: to_unixtime(TEST_DATETIME1),
                        EMAIL_ANT['confirmed']: email_confirmed_at,
                    },
                ),
            ],
        )

        userinfo = deep_merge(userinfo, email_dict)
        return dict(userinfo=userinfo)

    def _setup_account(self, account):
        build_account(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            **account['userinfo']
        )

    def _make_request(self, args=None):
        args = args or {}

        defaults = dict(uid=TEST_UID1, email=TEST_EMAIL1)

        for arg in defaults:
            args.setdefault(arg, defaults[arg])

        return self.env.client.post('/1/bundle/test/update_email/', query_string=dict(consumer='dev'), data=args)

    def _assert_email_attrs_equal(self, updated_attrs):
        attrs = dict(
            created=TEST_DATETIME1,
            bound=TEST_DATETIME1,
            confirmed=TEST_DATETIME1,
        )
        attrs.update(updated_attrs)

        bound_at = attrs['bound']

        for attr_name in attrs:
            value = attrs[attr_name]
            if value is not None:
                attrs[attr_name] = str(to_unixtime(value))

        for attr_name, attr_value in attrs.items():
            self.env.db.check_db_ext_attr(
                uid=TEST_UID1,
                entity_type=EXTENDED_ATTRIBUTES_EMAIL_TYPE,
                entity_id=TEST_EMAIL_ID1,
                field_name=attr_name,
                value=attr_value,
            )

        self.env.db.check(
            table_name='email_bindings',
            field_name='bound',
            expected_value=bound_at,
            uid=TEST_UID1,
            email_id=TEST_EMAIL_ID1,
            db='passportdbshard1',
        )

    def _assert_email_not_updated(self):
        self._assert_email_attrs_equal({})

    def _assert_update_email_in_history(self, attrs):
        entries = {
            'action': 'update_email_attributes',
            'email.911.address': TEST_EMAIL1,
            'email.911': 'updated',
            'consumer': 'dev',
        }
        for attr in attrs:
            name = 'email.911.%s' % attr
            entries[name] = str(to_unixtime(attrs[attr]))
        self.env.event_logger.assert_events_are_logged(entries)

    def test_account_disabled(self):
        self._setup_account(self._build_account(enabled=False))

        rv = self._make_request()

        self.assert_ok_response(rv)

    def test_request_emails(self):
        self._setup_account(self._build_account())

        self._make_request()

        request = self.env.blackbox.requests[0]
        request.assert_post_data_contains(
            dict(
                getemails='all',
                email_attributes='all',
            ),
        )

    def test_email_not_found(self):
        self._setup_account(self._build_account())
        self._assert_email_not_updated()

        rv = self._make_request(dict(email=TEST_EMAIL2))

        self.assert_error_response(rv, ['email.not_found'])
        self._assert_email_not_updated()

    def test_test_login(self):
        self._setup_account(self._build_account(login=TEST_YANDEX_TEAM_LOGIN1))

        rv = self._make_request()

        self.assert_ok_response(rv)

    def test_not_test_login(self):
        self._setup_account(self._build_account(login=TEST_LOGIN1))

        rv = self._make_request()

        self.assert_error_response(rv, ['email.not_updatable'])
        self._assert_email_not_updated()

    def test_update_created(self):
        self._setup_account(self._build_account())

        rv = self._make_request(dict(created_at=to_unixtime(TEST_DATETIME1 - TIME_DELTA)))

        self.assert_ok_response(rv)
        self._assert_email_attrs_equal(dict(created=TEST_DATETIME1 - TIME_DELTA))

        self._assert_update_email_in_history(dict(created_at=TEST_DATETIME1 - TIME_DELTA))
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('email_updated', created_at=str(TEST_DATETIME1 - TIME_DELTA)),
        ])

    def test_update_created__not_confirmed(self):
        self._setup_account(self._build_account(email_confirmed_at=None))

        rv = self._make_request(dict(created_at=to_unixtime(TEST_DATETIME1 - TIME_DELTA)))

        self.assert_ok_response(rv)
        self._assert_email_attrs_equal(dict(created=TEST_DATETIME1 - TIME_DELTA, confirmed=None))

    def test_update_bound(self):
        self._setup_account(
            self._build_account(
                email_confirmed_at=to_unixtime(TEST_DATETIME1 + 2 * TIME_DELTA),
            ),
        )

        rv = self._make_request(dict(bound_at=to_unixtime(TEST_DATETIME1 + TIME_DELTA)))

        self.assert_ok_response(rv)
        self._assert_email_attrs_equal(
            dict(
                bound=TEST_DATETIME1 + TIME_DELTA,
                confirmed=TEST_DATETIME1 + 2 * TIME_DELTA,
            ),
        )

    def test_update_confirmed(self):
        self._setup_account(self._build_account())

        rv = self._make_request(dict(confirmed_at=to_unixtime(TEST_DATETIME1 + TIME_DELTA)))

        self.assert_ok_response(rv)
        self._assert_email_attrs_equal(dict(confirmed=TEST_DATETIME1 + TIME_DELTA))

    def test_update_created_and_confirmed(self):
        self._setup_account(self._build_account())

        rv = self._make_request(
            dict(
                created_at=to_unixtime(TEST_DATETIME1 - TIME_DELTA),
                confirmed_at=to_unixtime(TEST_DATETIME1 + TIME_DELTA),
            ),
        )

        self.assert_ok_response(rv)
        self._assert_email_attrs_equal(
            dict(
                created=TEST_DATETIME1 - TIME_DELTA,
                confirmed=TEST_DATETIME1 + TIME_DELTA,
            ),
        )

    def test_update_confirmed__not_confirmed(self):
        self._setup_account(self._build_account(email_confirmed_at=None))

        rv = self._make_request(dict(confirmed_at=to_unixtime(TEST_DATETIME1 + TIME_DELTA)))

        self.assert_error_response(rv, ['confirmed_at.must_be_null'])
        self._assert_email_attrs_equal(dict(confirmed=None))

    def test_created_greater_than_confirmed(self):
        self._setup_account(self._build_account())

        rv = self._make_request(dict(confirmed_at=to_unixtime(TEST_DATETIME1 - TIME_DELTA)))

        self.assert_error_response(rv, ['created_at.must_be_less_or_equal_than_confirmed_at'])
        self._assert_email_not_updated()

    def test_no_timestamps(self):
        self._setup_account(self._build_account())

        rv = self._make_request(dict(created_at=None, bound_at=None, confirmed_at=None))

        self.assert_ok_response(rv)
        self._assert_email_not_updated()

        self.env.event_logger.assert_events_are_logged({})
        self.env.statbox.assert_has_written([])

    def test_no_uid(self):
        rv = self._make_request(dict(uid=None))
        self.assert_error_response(rv, ['uid.empty'])

    def test_no_email(self):
        rv = self._make_request(dict(email=None))
        self.assert_error_response(rv, ['email.empty'])
