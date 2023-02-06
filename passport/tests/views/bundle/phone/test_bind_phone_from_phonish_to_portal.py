# -*- coding: utf-8 -*-

from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.models.phones.faker import (
    assert_secure_phone_being_bound,
    assert_secure_phone_bound,
    assert_simple_phone_bound,
    build_phone_being_bound,
    build_phone_being_bound_replaces_secure_operations,
    build_phone_bound,
    build_phone_secured,
    build_phone_unbound,
    build_secure_phone_being_bound,
    PhoneIdGeneratorFaker,
)
from passport.backend.core.models.phones.phones import (
    ReplaceSecurePhoneWithNonboundPhoneOperation,
    SecureBindOperation,
    SimpleBindOperation,
)
from passport.backend.core.test.consts import *
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
    TimeSpan,
)
from passport.backend.core.types.bit_vector.bit_vector import PhoneBindingsFlags
from passport.backend.utils.common import deep_merge
from passport.backend.utils.time import datetime_to_integer_unixtime as datetime_to_unixtimei


TEST_PHONE_OPERATION_TTL1 = 10

TEST_DATETIME_2016 = datetime(2016, 1, 1, 12, 0, 0)
TEST_DATETIME_2017 = datetime(2017, 2, 2, 12, 0, 0)


@with_settings_hosts(
    YASMS_MARK_OPERATION_TTL=TEST_PHONE_OPERATION_TTL1,
)
class TestBindPhoneFromPhonishToPortal(BaseBundleTestViews):
    consumer = TEST_CONSUMER1
    default_url = '/2/bundle/phone/bind_phone_from_phonish_to_portal/'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP1,
    }
    http_query_args = {
        'portal_uid': TEST_UID1,
        'phonish_uid': TEST_UID2,
    }

    def setUp(self):
        super(TestBindPhoneFromPhonishToPortal, self).setUp()
        self.env = ViewsTestEnvironment()
        self._phone_id_generator_faker = PhoneIdGeneratorFaker()

        self.__patches = [
            self.env,
            self._phone_id_generator_faker,
        ]

        for patch in self.__patches:
            patch.start()

        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    networks=['127.0.0.1'],
                    grants={
                        'phone_bundle': ['bind_phone_from_phonish_to_portal'],
                    },
                ),
            },
        )
        self._phone_id_generator_faker.set_list([TEST_PHONE_ID2])
        self._setup_statbox_templates()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        del self.__patches
        del self._phone_id_generator_faker
        del self.env
        super(TestBindPhoneFromPhonishToPortal, self).tearDown()

    def _setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'base',
            uid=str(TEST_UID1),
            consumer=TEST_CONSUMER1,
            ip=TEST_USER_IP1,
        )
        self.env.statbox.bind_entry(
            'simple_bind_operation_created',
            _inherit_from=['simple_bind_operation_created', 'base'],
            number=TEST_PHONE_NUMBER1.masked_format_for_statbox,
            phone_id=str(TEST_PHONE_ID2),
            user_agent='-',
        )
        self.env.statbox.bind_entry(
            'simple_phone_bound',
            _inherit_from=['simple_phone_bound', 'base'],
            _exclude=['user_agent'],
            mode='bind_phone_from_phonish_to_portal',
            number=TEST_PHONE_NUMBER1.masked_format_for_statbox,
            phone_id=str(TEST_PHONE_ID2),
        )
        self.env.statbox.bind_entry(
            'phone_operation_cancelled',
            _inherit_from=['phone_operation_cancelled', 'base'],
            _exclude=['user_agent'],
            mode='bind_phone_from_phonish_to_portal',
            operation_id=str(TEST_PHONE_OPERATION_ID1),
        )
        self.env.statbox.bind_entry(
            'new_phone_copied_from_phonish',
            _inherit_from=['base'],
            mode='bind_phone_from_phonish_to_portal',
            action='new_phone_copied_from_phonish',
            source_uid=str(TEST_UID2),
        )
        self.env.statbox.bind_entry(
            'old_phone_updated_from_phonish',
            _inherit_from=['base'],
            mode='bind_phone_from_phonish_to_portal',
            action='old_phone_updated_from_phonish',
            source_uid=str(TEST_UID2),
        )

    def _build_portal_account(self, with_phone=False, phone_bound_at=TEST_DATETIME1,
                              phone_confirmed_at=TEST_DATETIME1, phone_secured_at=None,
                              phone_operation=None, enabled=True):
        account = dict(
            uid=TEST_UID1,
            enabled=enabled,
        )
        if not with_phone:
            pass
        elif with_phone and phone_bound_at is not None and phone_secured_at is None:
            account = deep_merge(
                account,
                build_phone_bound(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                    phone_created=TEST_DATETIME1,
                    phone_confirmed=phone_confirmed_at,
                    phone_bound=phone_bound_at,
                ),
            )
        elif with_phone and phone_bound_at is not None and phone_secured_at is not None:
            account = deep_merge(
                account,
                build_phone_secured(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                    phone_created=TEST_DATETIME1,
                    phone_confirmed=phone_confirmed_at,
                    phone_bound=phone_bound_at,
                    phone_secured=phone_secured_at,
                ),
            )
        elif with_phone and phone_bound_at is None and phone_operation is None:
            account = deep_merge(
                account,
                build_phone_unbound(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                    phone_created=TEST_DATETIME1,
                    phone_confirmed=phone_confirmed_at,
                ),
            )
        elif with_phone and phone_bound_at is None and phone_operation is SimpleBindOperation:
            account = deep_merge(
                account,
                build_phone_being_bound(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                    operation_id=TEST_PHONE_OPERATION_ID1,
                ),
            )
        elif with_phone and phone_bound_at is None and phone_operation is SecureBindOperation:
            account = deep_merge(
                account,
                build_secure_phone_being_bound(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                    operation_id=TEST_PHONE_OPERATION_ID1,
                ),
            )
        elif with_phone and phone_bound_at is None and phone_operation is ReplaceSecurePhoneWithNonboundPhoneOperation:
            account = deep_merge(
                account,
                build_phone_unbound(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                ),
                build_phone_secured(
                    phone_id=TEST_PHONE_ID3,
                    phone_number=TEST_PHONE_NUMBER2.e164,
                ),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=TEST_PHONE_OPERATION_ID1,
                    secure_phone_id=TEST_PHONE_ID3,
                    being_bound_phone_id=TEST_PHONE_ID2,
                    being_bound_phone_number=TEST_PHONE_NUMBER1.e164,
                    being_bound_operation_id=TEST_PHONE_OPERATION_ID2,
                ),
            )
        else:
            raise NotImplementedError()  # pragma: no cover
        return account

    def _build_phonish_account(self, phone_confirmed_at=TEST_DATETIME1, enabled=True):
        binding_flags = PhoneBindingsFlags()
        binding_flags.should_ignore_binding_limit = True
        return deep_merge(
            dict(
                uid=TEST_UID2,
                aliases={'phonish': TEST_PHONISH_LOGIN1},
                enabled=enabled,
            ),
            build_phone_bound(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER1.e164,
                phone_confirmed=phone_confirmed_at,
                binding_flags=binding_flags,
            ),
        )

    def _build_not_existent_account(self, uid):
        return dict(uid=None, id=uid)

    def _build_neophonish_account(self):
        return dict(
            uid=TEST_UID1,
            aliases=dict(neophonish=TEST_NEOPHONISH_LOGIN1),
        )

    def _build_lite_account(self):
        return dict(
            uid=TEST_UID1,
            aliases=dict(lite=TEST_EMAIL1),
        )

    def _build_social_account(self):
        return dict(
            uid=TEST_UID1,
            aliases=dict(social=TEST_SOCIAL_LOGIN1),
        )

    def _build_pdd_account(self):
        return dict(
            uid=TEST_PDD_UID1,
            aliases=dict(pdd=TEST_PDD_LOGIN1),
        )

    def _setup_blackbox(self, portal_account=None, phonish_account=None):
        if portal_account is None:
            portal_account = self._build_portal_account()
        if phonish_account is None:
            phonish_account = self._build_phonish_account()
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response_multiple(
                    [
                        portal_account,
                        phonish_account,
                    ],
                ),
            ],
        )
        self.env.blackbox.set_response_side_effect(
            'phone_bindings',
            [
                blackbox_phone_bindings_response([]),
            ],
        )

    def _setup_database(self, portal_account):
        userinfo_response = blackbox_userinfo_response(**portal_account)
        self.env.db.serialize(userinfo_response)

    def _build_event(self, uid, records):
        return [{'uid': str(uid), 'name': r[0], 'value': r[1]} for r in records]

    def _cancel_phone_operation_than_create_and_acquire_phone_event(self):
        return self._build_event(
            TEST_UID1,
            [
                ('phone.20.action', 'changed'),
                ('phone.20.created', TimeNow()),
                ('phone.20.number', TEST_PHONE_NUMBER1.e164),
                ('phone.20.operation.35513.action', 'deleted'),
                ('phone.20.operation.35513.security_identity', TEST_PHONE_NUMBER1.digital),
                ('phone.20.operation.35513.type', 'bind'),
                ('phone.20.operation.35514.action', 'created'),
                ('phone.20.operation.35514.finished', TimeNow(offset=TEST_PHONE_OPERATION_TTL1)),
                ('phone.20.operation.35514.security_identity', TEST_PHONE_NUMBER1.digital),
                ('phone.20.operation.35514.started', TimeNow()),
                ('phone.20.operation.35514.type', 'bind'),
                ('action', 'acquire_phone'),
                ('consumer', TEST_CONSUMER1),
            ],
        )

    def _create_and_acquire_phone_event(self):
        return self._build_event(
            TEST_UID1,
            [
                ('phone.20.action', 'created'),
                ('phone.20.created', TimeNow()),
                ('phone.20.number', TEST_PHONE_NUMBER1.e164),
                ('phone.20.operation.1.action', 'created'),
                ('phone.20.operation.1.finished', TimeNow(offset=TEST_PHONE_OPERATION_TTL1)),
                ('phone.20.operation.1.security_identity', TEST_PHONE_NUMBER1.digital),
                ('phone.20.operation.1.started', TimeNow()),
                ('phone.20.operation.1.type', 'bind'),
                ('action', 'acquire_phone'),
                ('consumer', TEST_CONSUMER1),
            ],
        )

    def _acquire_phone_event(self):
        return self._build_event(
            TEST_UID1,
            [
                ('phone.20.number', TEST_PHONE_NUMBER1.e164),
                ('phone.20.operation.1.action', 'created'),
                ('phone.20.operation.1.finished', TimeNow(offset=TEST_PHONE_OPERATION_TTL1)),
                ('phone.20.operation.1.security_identity', TEST_PHONE_NUMBER1.digital),
                ('phone.20.operation.1.started', TimeNow()),
                ('phone.20.operation.1.type', 'bind'),
                ('action', 'acquire_phone'),
                ('consumer', TEST_CONSUMER1),
            ],
        )

    def _bind_phone_event(self, bound_at, confirmed_at, operation_id=1):
        return self._build_event(
            TEST_UID1,
            [
                ('phone.20.action', 'changed'),
                ('phone.20.bound', TimeSpan(datetime_to_unixtimei(bound_at))),
                ('phone.20.confirmed', str(datetime_to_unixtimei(confirmed_at))),
                ('phone.20.number', TEST_PHONE_NUMBER1.e164),
                ('phone.20.operation.%s.action' % operation_id, 'deleted'),
                ('phone.20.operation.%s.security_identity' % operation_id, TEST_PHONE_NUMBER1.digital),
                ('phone.20.operation.%s.type' % operation_id, 'bind'),
                ('action', 'bind_phone_from_phonish_to_portal'),
                ('consumer', TEST_CONSUMER1),
            ],
        )

    def _assert_new_phone_bound_to_portal_account(self, confirmed_at, bound_at):
        assert_simple_phone_bound.check_db(
            self.env.db,
            TEST_UID1,
            phone_attributes={
                'id': TEST_PHONE_ID2,
                'number': TEST_PHONE_NUMBER1.e164,
                'created': DatetimeNow(),
                'bound': bound_at,
                'confirmed': confirmed_at,
            },
            binding_flags=PhoneBindingsFlags(),
        )

    def _assert_old_phone_bound_to_portal_account(self, confirmed_at, bound_at):
        assert_simple_phone_bound.check_db(
            self.env.db,
            TEST_UID1,
            phone_attributes={
                'id': TEST_PHONE_ID2,
                'number': TEST_PHONE_NUMBER1.e164,
                'created': TEST_DATETIME1,
                'bound': bound_at,
                'confirmed': confirmed_at,
            },
            binding_flags=PhoneBindingsFlags(),
        )

    def _assert_old_secure_phone_bound_to_portal_account(self, confirmed_at, bound_at):
        assert_secure_phone_bound.check_db(
            self.env.db,
            TEST_UID1,
            phone_attributes={
                'id': TEST_PHONE_ID2,
                'number': TEST_PHONE_NUMBER1.e164,
                'created': TEST_DATETIME1,
                'bound': bound_at,
                'confirmed': confirmed_at,
            },
            binding_flags=PhoneBindingsFlags(),
        )

    def _assert_sms_not_sent(self):
        eq_(self.env.yasms.requests, [])

    def test_no_phone_on_portal(self):
        portal_account = self._build_portal_account(with_phone=False)
        phonish_account = self._build_phonish_account(phone_confirmed_at=TEST_DATETIME1)
        self._setup_blackbox(
            portal_account=portal_account,
            phonish_account=phonish_account,
        )
        self._setup_database(portal_account=portal_account)

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_new_phone_bound_to_portal_account(
            confirmed_at=TEST_DATETIME1,
            bound_at=DatetimeNow(),
        )
        self.env.statbox_logger.assert_has_written(
            [
                self.env.statbox.entry('simple_bind_operation_created'),
                self.env.statbox.entry('simple_phone_bound'),
                self.env.statbox.entry('new_phone_copied_from_phonish'),
            ],
        )
        self.env.event_logger.assert_events_are_logged(
            self._create_and_acquire_phone_event() +
            self._bind_phone_event(
                bound_at=DatetimeNow(),
                confirmed_at=TEST_DATETIME1,
            ),
            in_order=True,
        )
        self._assert_sms_not_sent()

    def test_phone_unbound_on_portal(self):
        portal_account = self._build_portal_account(
            with_phone=True,
            phone_bound_at=None,
            phone_confirmed_at=TEST_DATETIME_2016,
        )
        phonish_account = self._build_phonish_account(
            phone_confirmed_at=TEST_DATETIME_2017,
        )
        self._setup_blackbox(
            portal_account=portal_account,
            phonish_account=phonish_account,
        )
        self._setup_database(portal_account=portal_account)

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_old_phone_bound_to_portal_account(
            confirmed_at=TEST_DATETIME_2017,
            bound_at=DatetimeNow(),
        )
        self.env.statbox_logger.assert_has_written(
            [
                self.env.statbox.entry('simple_bind_operation_created'),
                self.env.statbox.entry('simple_phone_bound'),
                self.env.statbox.entry('new_phone_copied_from_phonish'),
            ],
        )
        self.env.event_logger.assert_events_are_logged(
            self._acquire_phone_event() +
            self._bind_phone_event(
                bound_at=DatetimeNow(),
                confirmed_at=TEST_DATETIME_2017,
            ),
            in_order=True,
        )
        self._assert_sms_not_sent()

    def test_phone_being_simple_bound_on_portal(self):
        portal_account = self._build_portal_account(
            with_phone=True,
            phone_bound_at=None,
            phone_confirmed_at=None,
            phone_operation=SimpleBindOperation,
        )
        phonish_account = self._build_phonish_account(
            phone_confirmed_at=TEST_DATETIME1,
        )
        self._setup_blackbox(
            portal_account=portal_account,
            phonish_account=phonish_account,
        )
        self._setup_database(portal_account=portal_account)

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_new_phone_bound_to_portal_account(
            confirmed_at=TEST_DATETIME1,
            bound_at=DatetimeNow(),
        )
        self.env.statbox_logger.assert_has_written(
            [
                self.env.statbox.entry(
                    'phone_operation_cancelled',
                    operation_id=str(TEST_PHONE_OPERATION_ID1),
                ),
                self.env.statbox.entry(
                    'simple_bind_operation_created',
                    operation_id=str(TEST_PHONE_OPERATION_ID1 + 1),
                ),
                self.env.statbox.entry(
                    'simple_phone_bound',
                    operation_id=str(TEST_PHONE_OPERATION_ID1 + 1),
                ),
                self.env.statbox.entry('new_phone_copied_from_phonish'),
            ],
        )
        self.env.event_logger.assert_events_are_logged(
            self._cancel_phone_operation_than_create_and_acquire_phone_event() +
            self._bind_phone_event(
                bound_at=DatetimeNow(),
                confirmed_at=TEST_DATETIME1,
                operation_id=str(TEST_PHONE_OPERATION_ID1 + 1),
            ),
            in_order=True,
        )
        self._assert_sms_not_sent()

    def test_phone_being_secure_bound_on_portal(self):
        portal_account = self._build_portal_account(
            with_phone=True,
            phone_bound_at=None,
            phone_confirmed_at=None,
            phone_operation=SecureBindOperation,
        )
        self._setup_blackbox(portal_account=portal_account)
        self._setup_database(portal_account=portal_account)

        rv = self.make_request()

        self.assert_error_response(rv, ['operation.exists'])
        assert_secure_phone_being_bound.check_db(
            self.env.db,
            TEST_UID1,
            phone_attributes={
                'id': TEST_PHONE_ID2,
                'number': TEST_PHONE_NUMBER1.e164,
            },
        )

    def test_phone_replacing_secure_on_portal(self):
        portal_account = self._build_portal_account(
            with_phone=True,
            phone_bound_at=None,
            phone_confirmed_at=None,
            phone_operation=ReplaceSecurePhoneWithNonboundPhoneOperation,
        )
        self._setup_blackbox(portal_account=portal_account)
        self._setup_database(portal_account=portal_account)

        rv = self.make_request()

        self.assert_error_response(rv, ['operation.exists'])

    def test_secure_phone_bound_on_portal(self):
        portal_account = self._build_portal_account(
            with_phone=True,
            phone_bound_at=TEST_DATETIME_2016,
            phone_confirmed_at=TEST_DATETIME_2016,
            phone_secured_at=TEST_DATETIME_2016,
        )
        phonish_account = self._build_phonish_account(
            phone_confirmed_at=TEST_DATETIME_2017,
        )
        self._setup_blackbox(
            portal_account=portal_account,
            phonish_account=phonish_account,
        )
        self._setup_database(portal_account=portal_account)

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_old_secure_phone_bound_to_portal_account(
            confirmed_at=TEST_DATETIME_2017,
            bound_at=TEST_DATETIME_2016,
        )

        self.env.statbox_logger.assert_has_written([
            self.env.statbox.entry('old_phone_updated_from_phonish'),
        ])
        self.env.event_logger.assert_events_are_logged(
            self._build_event(
                TEST_UID1,
                [
                    ('phone.20.action', 'changed'),
                    ('phone.20.confirmed', str(datetime_to_unixtimei(TEST_DATETIME_2017))),
                    ('phone.20.number', TEST_PHONE_NUMBER1.e164),
                    ('action', 'bind_phone_from_phonish_to_portal'),
                    ('consumer', TEST_CONSUMER1),
                ],
            ),
            in_order=True,
        )

    def test_phone_bound_on_portal_and_confirmed_before_phonish(self):
        portal_account = self._build_portal_account(
            with_phone=True,
            phone_bound_at=TEST_DATETIME_2016,
            phone_confirmed_at=TEST_DATETIME_2016,
        )
        phonish_account = self._build_phonish_account(
            phone_confirmed_at=TEST_DATETIME_2017,
        )
        self._setup_blackbox(
            portal_account=portal_account,
            phonish_account=phonish_account,
        )
        self._setup_database(portal_account=portal_account)

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_old_phone_bound_to_portal_account(
            confirmed_at=TEST_DATETIME_2017,
            bound_at=TEST_DATETIME_2016,
        )
        self.env.statbox_logger.assert_has_written([
            self.env.statbox.entry('old_phone_updated_from_phonish'),
        ])
        self.env.event_logger.assert_events_are_logged(
            self._build_event(
                TEST_UID1,
                [
                    ('phone.20.action', 'changed'),
                    ('phone.20.confirmed', str(datetime_to_unixtimei(TEST_DATETIME_2017))),
                    ('phone.20.number', TEST_PHONE_NUMBER1.e164),
                    ('action', 'bind_phone_from_phonish_to_portal'),
                    ('consumer', TEST_CONSUMER1),
                ],
            ),
            in_order=True,
        )

    def test_phone_bound_on_portal_and_confirmed_after_phonish(self):
        portal_account = self._build_portal_account(
            with_phone=True,
            phone_bound_at=TEST_DATETIME_2017,
            phone_confirmed_at=TEST_DATETIME_2017,
        )
        phonish_account = self._build_phonish_account(
            phone_confirmed_at=TEST_DATETIME_2016,
        )
        self._setup_blackbox(
            portal_account=portal_account,
            phonish_account=phonish_account,
        )
        self._setup_database(portal_account=portal_account)

        rv = self.make_request()

        self.assert_ok_response(rv)
        self._assert_old_phone_bound_to_portal_account(
            confirmed_at=TEST_DATETIME_2017,
            bound_at=TEST_DATETIME_2017,
        )
        self.env.statbox_logger.assert_has_written([])
        self.env.event_logger.assert_events_are_logged([])

    def test_request_phones_from_blackbox(self):
        self._setup_blackbox()

        rv = self.make_request()

        eq_(len(self.env.blackbox.requests), 2)
        self.env.blackbox.requests[0].assert_post_data_contains({
            'getphones': 'all',
            'phone_attributes': '1,2,3,4,5,6,109',
            'getphonebindings': 'all',
            'getphoneoperations': '1',
        })
        self.env.blackbox.requests[0].assert_contains_attributes({'phones.default'})

        self.assert_ok_response(rv)

    def test_portal_account_not_found(self):
        self._setup_blackbox(portal_account=self._build_not_existent_account(TEST_UID1))
        rv = self.make_request()
        self.assert_error_response(rv, ['account.not_found'])

    def test_portal_account_disabled(self):
        self._setup_blackbox(portal_account=self._build_portal_account(enabled=False))
        rv = self.make_request()
        self.assert_error_response(rv, ['account.disabled'])

    def test_portal_uid_belongs_to_portal(self):
        self._setup_blackbox(portal_account=self._build_portal_account())
        rv = self.make_request()
        self.assert_ok_response(rv)

    def test_portal_uid_belongs_to_neophonish(self):
        self._setup_blackbox(portal_account=self._build_neophonish_account())
        rv = self.make_request()
        self.assert_ok_response(rv)

    def test_portal_uid_belongs_to_lite(self):
        self._setup_blackbox(portal_account=self._build_lite_account())
        rv = self.make_request()
        self.assert_ok_response(rv)

    def test_portal_uid_belongs_to_social(self):
        self._setup_blackbox(portal_account=self._build_social_account())
        rv = self.make_request()
        self.assert_ok_response(rv)

    def test_portal_uid_belongs_to_pdd(self):
        self._setup_blackbox(portal_account=self._build_pdd_account())

        rv = self.make_request(
            query_args={
                'portal_uid': TEST_PDD_UID1,
                'phonish_uid': TEST_UID2,
            },
        )

        self.assert_ok_response(rv)

    def test_portal_uid_belongs_to_phonish(self):
        self._setup_blackbox(portal_account=self._build_phonish_account())
        rv = self.make_request()
        self.assert_error_response(rv, ['account.invalid_type'])

    def test_phonish_account_not_found(self):
        self._setup_blackbox(phonish_account=self._build_not_existent_account(TEST_UID2))
        rv = self.make_request()
        self.assert_error_response(rv, ['account.not_found'])

    def test_phonish_account_disabled(self):
        self._setup_blackbox(phonish_account=self._build_phonish_account(enabled=False))
        rv = self.make_request()
        self.assert_error_response(rv, ['account.disabled'])

    def test_phonish_uid_belongs_to_phonish(self):
        self._setup_blackbox(phonish_account=self._build_phonish_account())
        rv = self.make_request()
        self.assert_ok_response(rv)

    def test_phonish_uid_belongs_to_portal(self):
        self._setup_blackbox(phonish_account=self._build_portal_account())
        rv = self.make_request()
        self.assert_error_response(rv, ['account.invalid_type'])

    def test_blackbox_returned_swapped_accounts(self):
        self._setup_blackbox(
            portal_account=self._build_phonish_account(),
            phonish_account=self._build_portal_account(),
        )
        rv = self.make_request()
        self.assert_ok_response(rv)
