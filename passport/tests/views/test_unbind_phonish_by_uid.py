# -*- coding: utf-8 -*-

from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_json_error_response,
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.passport.faker.fake_passport import (
    passport_bundle_api_error_response,
    passport_ok_response,
)
from passport.backend.core.builders.yasms.faker import (
    yasms_drop_phone_response,
    yasms_error_json_response,
)
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_PHONE_NAME_TO_TYPE_MAPPING
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.social.api.test import ApiV3TestCase
from passport.backend.social.common.builders.blackbox import (
    BLACKBOX_PHONE_ATTRIBUTES,
    BLACKBOX_PHONE_EXTENDED_ATTRIBUTES,
)
from passport.backend.social.common.chrono import now
from passport.backend.social.common.db.schemas import (
    person_table,
    profile_table,
)
from passport.backend.social.common.providers.Yandex import Yandex
from passport.backend.social.common.test.consts import (
    CONSUMER1,
    CONSUMER_IP1,
    PHONISH_LOGIN1,
    PROFILE_ID1,
    SOCIAL_LOGIN1,
    UID1,
    UID2,
)
from passport.backend.social.common.test.fake_billing_api import (
    billing_api_fail_response,
    billing_api_invalidate_account_bindings_response,
    FakeBillingApi,
)
from passport.backend.social.common.test.fake_passport import FakePassport
from passport.backend.utils.common import deep_merge
from sqlalchemy import sql
from sqlalchemy.exc import DBAPIError


PHONE_ID1 = 1
PHONE_ID2 = 2
PHONE_NUMBER1 = '+79026411724'
PHONE_NUMBER2 = '+79259164525'


class TestUnbindPhonishtByUid(ApiV3TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/api/unbind_phonish_by_uid'
    REQUEST_DATA = {
        'consumer': CONSUMER1,
        'uid1': UID1,
        'uid2': UID2,
        'delete_phone': '1',
    }
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
    }

    def setUp(self):
        super(TestUnbindPhonishtByUid, self).setUp()
        self._fake_billing_api = FakeBillingApi()
        self._fake_passport = FakePassport()

        self.__patches = [
            self._fake_billing_api,
            self._fake_passport,
        ]
        for patch in self.__patches:
            patch.start()

        self._setup_statbox_templates()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        super(TestUnbindPhonishtByUid, self).tearDown()

    def build_settings(self):
        settings = super(TestUnbindPhonishtByUid, self).build_settings()
        settings['social_config'].update(
            billing_http_api_retries=1,
            billing_http_api_service_token='billing_token',
            billing_http_api_timeout=1,
            billing_http_api_url='https://billing',
            invalidate_billing_binding_cache=True,
            passport_api_consumer='socialism',
            passport_api_retries=1,
            passport_api_timeout=1,
            passport_api_url='https://passport',
        )
        return settings

    def _setup_statbox_templates(self):
        self._fake_statbox.bind_entry(
            'update_account_bindings',
            action='update_account_yandex_bindings',
            consumer=CONSUMER1,
        )

    def _setup_grants(self):
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['unbind-phonish-by-uid'],
        )

    def _setup_passport(self, account1=None, account2=None):
        if account1 is None:
            account1 = self._build_portal_account()
        if account2 is None:
            account2 = self._build_phonish_account()
        if account1 != account2:
            self._fake_blackbox.set_response_side_effect(
                'userinfo',
                [
                    blackbox_userinfo_response_multiple([account1, account2]),
                ],
            )
        else:
            self._fake_blackbox.set_response_side_effect(
                'userinfo',
                [
                    blackbox_userinfo_response(**account1),
                ],
            )

        self._fake_passport.set_response_side_effect(
            'yasms_api_drop_phone',
            [
                yasms_drop_phone_response(uid=UID1, status='OK'),
            ],
        )

        self._fake_passport.set_response_side_effect(
            'account_options',
            [
                passport_ok_response(),
                passport_ok_response(),
            ],
        )

    def _build_not_existent_account(self):
        return dict(uid=None, id=UID1)

    def _build_portal_account(self, is_phone_secure=False, enabled=True):
        account = dict(
            enabled=enabled,
            uid=UID1,
        )
        if is_phone_secure:
            account = deep_merge(
                account,
                build_phone_secured(
                    phone_id=PHONE_ID1,
                    phone_number=PHONE_NUMBER1,
                ),
            )
        else:
            account = deep_merge(
                account,
                build_phone_bound(
                    phone_id=PHONE_ID1,
                    phone_number=PHONE_NUMBER1,
                ),
            )
        return account

    def _build_social_account(self):
        return deep_merge(
            dict(
                uid=UID1,
                login=SOCIAL_LOGIN1,
                aliases=dict(social=SOCIAL_LOGIN1),
            ),
            build_phone_bound(
                phone_id=PHONE_ID1,
                phone_number=PHONE_NUMBER1,
            ),
        )

    def _build_phonish_account(self, uid=UID2, phone_number=PHONE_NUMBER1, enabled=True):
        return deep_merge(
            dict(
                aliases=dict(phonish=PHONISH_LOGIN1),
                enabled=enabled,
                uid=uid,
            ),
            build_phone_bound(
                phone_id=PHONE_ID2,
                phone_number=phone_number,
            ),
        )

    def _setup_billing(self, failed=False):
        if not failed:
            response = billing_api_invalidate_account_bindings_response()
        else:
            response = billing_api_fail_response()
        self._fake_billing_api.set_response_value('invalidate_account_bindings', response)

    def _setup_socialism(self):
        with self._fake_db.no_recording() as db:
            query = profile_table.insert().values(
                profile_id=PROFILE_ID1,
                uid=UID1,
                provider_id=Yandex.id,
                userid=str(UID2),
                created=now(),
            )
            db.execute(query)
            query = person_table.insert().values(profile_id=PROFILE_ID1)
            db.execute(query)

    def _assert_binding_not_exist(self):
        binding = self._find_binding(PROFILE_ID1)
        self.assertIsNone(binding['profile'])
        self.assertIsNone(binding['person'])

    def _assert_binding_exists(self):
        binding = self._find_binding(PROFILE_ID1)
        self.assertIsNotNone(binding['profile'])
        self.assertIsNotNone(binding['person'])

    def _find_binding(self, profile_id):
        retval = dict(
            profile=None,
            person=None,
        )

        query = (
            sql.select([profile_table])
            .where(
                profile_table.c.profile_id == profile_id,
            )
        )
        with self._fake_db.no_recording() as db:
            profiles = db.execute(query).fetchall()

        if profiles:
            retval.update(profile=profiles[0])

        query = (
            sql.select([person_table])
            .where(
                person_table.c.profile_id == PROFILE_ID1,
            )
        )
        with self._fake_db.no_recording() as db:
            persons = db.execute(query).fetchall()

        if persons:
            retval.update(person=persons[0])

        return retval

    def _assert_invalidated_billing_cache(self):
        self.assertEqual(len(self._fake_billing_api.requests), 1)
        self._fake_billing_api.requests[0].assert_properties_equal(
            method='POST',
            url='https://billing/trust-payments/v2/passport/%s/invalidate' % UID1,
            headers={'X-Service-Token': 'billing_token'},
        )

    def _assert_not_invalidated_billing_cache(self):
        self.assertEqual(len(self._fake_billing_api.requests), 0)

    def _assert_deleted_phonish_phone_from_portal_account(self, request):
        request.assert_properties_equal(
            method='POST',
            url='https://passport/yasms/api/dropphone',
            post_args={
                'phoneid': str(PHONE_ID1),
                'sender': 'socialism',
                'uid': str(UID1),
            },
        )

    def _assert_logouted_portal_account(self, request):
        self._assert_logouted_account(request, UID1)

    def _assert_logouted_phonish_account(self, request):
        self._assert_logouted_account(request, UID2)

    def _assert_logouted_account(self, request, uid):
        request.assert_query_equals(
            {
                'consumer': 'socialism',
            },
        )
        request.assert_url_starts_with(
            'https://passport/2/account/%s/options/?' % uid,
        )
        request.assert_properties_equal(
            method='POST',
            post_args={
                'global_logout': 1,
            },
        )

    def test_delete_binding_and_phone(self):
        self._setup_grants()
        self._setup_passport()
        self._setup_socialism()
        self._setup_billing()

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_binding_not_exist()
        self._fake_statbox.assert_contains([
            self._fake_statbox.entry(
                'update_account_bindings',
                uid=str(UID1),
            ),
        ])
        self._assert_invalidated_billing_cache()
        self._assert_deleted_phonish_phone_from_portal_account(self._fake_passport.requests[0])

    def test_delete_binding(self):
        self._setup_grants()
        self._setup_passport()
        self._setup_socialism()
        self._setup_billing()

        rv = self._make_request(exclude_data=['delete_phone'])

        self._assert_ok_response(rv)
        self._assert_binding_not_exist()
        self._fake_statbox.assert_contains([
            self._fake_statbox.entry(
                'update_account_bindings',
                uid=str(UID1),
            ),
        ])
        self._assert_invalidated_billing_cache()
        self.assertEqual(len(self._fake_passport.requests), 0)

    def test_delete_binding_but_not_phone(self):
        self._setup_grants()
        self._setup_passport()
        self._setup_socialism()
        self._setup_billing()

        rv = self._make_request(data={'delete_phone': '0'})

        self._assert_ok_response(rv)
        self.assertEqual(len(self._fake_passport.requests), 0)

    def test_call_billing_but_not_delete_phone_even_when_binding_not_exist(self):
        self._setup_grants()
        self._setup_passport()
        self._setup_billing()

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_binding_not_exist()
        self._fake_statbox.assert_contains([
            self._fake_statbox.entry(
                'update_account_bindings',
                uid=str(UID1),
            ),
        ])
        self._assert_invalidated_billing_cache()
        self.assertEqual(len(self._fake_passport.requests), 0)

    def test_delete_phone_empty(self):
        self._setup_grants()

        rv = self._make_request(data={'delete_phone': ''})

        self._assert_error_response(rv, ['delete_phone.empty'])

    def test_uid1_missing(self):
        self._setup_grants()

        rv = self._make_request(exclude_data=['uid1'])

        self._assert_error_response(rv, ['uid1.empty'])

    def test_uid1_empty(self):
        self._setup_grants()

        rv = self._make_request(data={'uid1': ''})

        self._assert_error_response(rv, ['uid1.empty'])

    def test_uid2_missing(self):
        self._setup_grants()

        rv = self._make_request(exclude_data=['uid2'])

        self._assert_error_response(rv, ['uid2.empty'])

    def test_uid2_empty(self):
        self._setup_grants()

        rv = self._make_request(data={'uid2': ''})

        self._assert_error_response(rv, ['uid2.empty'])

    def test_uid1_invalid(self):
        self._setup_grants()
        self._setup_socialism()
        self._setup_passport(account1=self._build_not_existent_account())

        rv = self._make_request(data={'uid1': 'invalid'})

        self._assert_error_response(rv, ['account.not_found'])
        self._assert_binding_exists()
        self.assertEqual(len(self._fake_passport.requests), 0)

    def test_uid2_invalid(self):
        self._setup_grants()
        self._setup_socialism()
        self._setup_passport(account2=self._build_not_existent_account())

        rv = self._make_request(data={'uid2': 'invalid'})

        self._assert_error_response(rv, ['account.not_found'])
        self._assert_binding_exists()
        self.assertEqual(len(self._fake_passport.requests), 0)

    def test_failed_to_invalidate_billing_cache(self):
        self._setup_grants()
        self._setup_passport()
        self._setup_socialism()
        self._setup_billing(failed=True)

        rv = self._make_request()

        self._assert_error_response(
            rv,
            ['internal_error'],
            description='Billing failed',
        )
        self._assert_binding_not_exist()
        self._assert_deleted_phonish_phone_from_portal_account(self._fake_passport.requests[0])

    def test_blackbox_failed(self):
        self._setup_grants()
        self._setup_socialism()
        self._fake_blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_json_error_response('DB_EXCEPTION'),
            ],
        )

        rv = self._make_request()

        self._assert_error_response(
            rv,
            ['internal_error'],
            description='Blackbox failed',
        )
        self._assert_binding_exists()
        self.assertEqual(len(self._fake_passport.requests), 0)
        self._fake_statbox.assert_equals([])
        self._assert_not_invalidated_billing_cache()

    def test_database_failed(self):
        self._setup_grants()
        self._setup_passport()
        self._setup_socialism()
        self._setup_billing()
        self._fake_db.set_side_effect([DBAPIError(0, 0, 0, 0)])

        rv = self._make_request()

        self._assert_error_response(
            rv,
            ['internal_error'],
            description='Database failed',
        )
        self._assert_binding_exists()
        self.assertEqual(len(self._fake_passport.requests), 0)
        self._fake_statbox.assert_equals([])
        self._assert_not_invalidated_billing_cache()

    def test_passport_failed(self):
        self._setup_grants()
        self._setup_passport()
        self._setup_socialism()
        self._setup_billing()
        self._fake_passport.set_response_side_effect(
            'yasms_api_drop_phone',
            [
                yasms_error_json_response('INTERROR'),
            ],
        )

        rv = self._make_request()

        self._assert_error_response(
            rv,
            ['internal_error'],
            description='Passport failed',
        )
        self._assert_binding_exists()
        self._fake_statbox.assert_equals([])
        self._assert_not_invalidated_billing_cache()

    def test_drop_phone_status_not_found(self):
        self._setup_grants()
        self._setup_passport()
        self._setup_socialism()
        self._setup_billing()
        self._fake_passport.set_response_side_effect(
            'yasms_api_drop_phone',
            [
                yasms_drop_phone_response(uid=UID1, status='NOTFOUND'),
            ],
        )

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_binding_not_exist()
        self._assert_deleted_phonish_phone_from_portal_account(self._fake_passport.requests[0])

    def test_drop_phone_status_unknown(self):
        self._setup_grants()
        self._setup_passport()
        self._setup_socialism()
        self._setup_billing()
        self._fake_passport.set_response_side_effect(
            'yasms_api_drop_phone',
            [
                yasms_drop_phone_response(uid=UID1, status='ABYRVALG'),
            ],
        )

        rv = self._make_request()

        self._assert_error_response(rv, ['exception.unhandled'])
        self._assert_binding_exists()
        self._fake_statbox.assert_equals([])
        self._assert_not_invalidated_billing_cache()

    def test_account1_not_found(self):
        self._setup_grants()
        self._setup_passport(account1=self._build_not_existent_account())
        self._setup_socialism()

        rv = self._make_request()

        self._assert_error_response(rv, ['account.not_found'])
        self._assert_binding_exists()
        self.assertEqual(len(self._fake_passport.requests), 0)

    def test_account2_not_found(self):
        self._setup_grants()
        self._setup_passport(account2=self._build_not_existent_account())
        self._setup_socialism()

        rv = self._make_request()

        self._assert_error_response(rv, ['account.not_found'])
        self._assert_binding_exists()
        self.assertEqual(len(self._fake_passport.requests), 0)

    def test_swapped_uids(self):
        self._setup_grants()
        self._setup_passport()
        self._setup_socialism()
        self._setup_billing()

        rv = self._make_request(
            data={
                'uid1': UID2,
                'uid2': UID1,
            },
        )

        self._assert_ok_response(rv)
        self._assert_binding_not_exist()
        self._fake_statbox.assert_contains([
            self._fake_statbox.entry(
                'update_account_bindings',
                uid=str(UID1),
            ),
        ])
        self._assert_invalidated_billing_cache()
        self._assert_deleted_phonish_phone_from_portal_account(self._fake_passport.requests[0])

    def test_social_account(self):
        self._setup_grants()
        self._setup_passport(self._build_social_account())
        self._setup_socialism()
        self._setup_billing()

        rv = self._make_request()

        self._assert_ok_response(rv)

    def test_portal_and_social(self):
        self._setup_grants()
        self._setup_passport(account2=self._build_social_account())
        self._setup_socialism()
        self._setup_billing()

        rv = self._make_request()

        self._assert_error_response(rv, ['account.invalid_type'])
        self._assert_binding_exists()
        self.assertEqual(len(self._fake_passport.requests), 0)

    def test_phonish_and_phonish(self):
        self._setup_grants()
        self._setup_passport(self._build_phonish_account(uid=UID1))
        self._setup_socialism()
        self._setup_billing()

        rv = self._make_request()

        self._assert_error_response(rv, ['account.invalid_type'])
        self._assert_binding_exists()
        self.assertEqual(len(self._fake_passport.requests), 0)

    def test_secure_phone(self):
        self._setup_grants()
        account = self._build_portal_account(is_phone_secure=True)
        self._setup_passport(account)
        self._setup_socialism()
        self._setup_billing()

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_binding_not_exist()
        self._fake_statbox.assert_contains([
            self._fake_statbox.entry(
                'update_account_bindings',
                uid=str(UID1),
            ),
        ])
        self._assert_invalidated_billing_cache()
        self.assertEqual(len(self._fake_passport.requests), 0)

    def test_no_phonish_phone(self):
        self._setup_grants()
        account = self._build_phonish_account(phone_number=PHONE_NUMBER2)
        self._setup_passport(account2=account)
        self._setup_socialism()
        self._setup_billing()

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_binding_not_exist()
        self._fake_statbox.assert_contains([
            self._fake_statbox.entry(
                'update_account_bindings',
                uid=str(UID1),
            ),
        ])
        self._assert_invalidated_billing_cache()
        self.assertEqual(len(self._fake_passport.requests), 0)

    def test_blackbox_request(self):
        self._setup_grants()
        self._setup_passport()
        self._setup_socialism()
        self._setup_billing()

        rv = self._make_request()

        self._assert_ok_response(rv)

        self.assertEqual(len(self._fake_blackbox.requests), 1)
        blackbox_request = self._fake_blackbox.requests[0]
        blackbox_request.assert_properties_equal(method='POST')
        phone_attributes = ','.join([
            str(EXTENDED_ATTRIBUTES_PHONE_NAME_TO_TYPE_MAPPING[attr_name])
            for attr_name in BLACKBOX_PHONE_EXTENDED_ATTRIBUTES
        ])
        blackbox_request.assert_post_data_contains({
            'aliases': 'all',
            'getphonebindings': 'all',
            'getphones': 'all',
            'method': 'userinfo',
            'phone_attributes': phone_attributes,
            'uid': str(UID1) + ',' + str(UID2),
            'userip': '127.0.0.1',
        })
        blackbox_request.assert_contains_attributes(BLACKBOX_PHONE_ATTRIBUTES)

    def test_disabled_portal_account(self):
        self._setup_grants()
        portal = self._build_portal_account(enabled=False)
        self._setup_passport(portal)
        self._setup_socialism()
        self._setup_billing()

        rv = self._make_request()

        self._assert_ok_response(rv)

    def test_disabled_phonish_account(self):
        self._setup_grants()
        phonish = self._build_phonish_account(enabled=False)
        self._setup_passport(account2=phonish)
        self._setup_socialism()
        self._setup_billing()

        rv = self._make_request()

        self._assert_ok_response(rv)

    def test_uids_equal(self):
        self._setup_grants()
        portal = self._build_portal_account()
        self._setup_passport(portal, portal)

        rv = self._make_request(data={'uid2': UID1})

        self._assert_error_response(rv, ['account.invalid_type'])

    def test_logout_portal(self):
        self._setup_grants()
        self._setup_passport()
        self._setup_socialism()
        self._setup_billing()

        rv = self._make_request(data={'logout_master': '1'})

        self._assert_ok_response(rv)
        self._assert_logouted_portal_account(self._fake_passport.requests[1])

    def test_logout_phonish(self):
        self._setup_grants()
        self._setup_passport()
        self._setup_socialism()
        self._setup_billing()

        rv = self._make_request(data={'logout_phonish': '1'})

        self._assert_ok_response(rv)
        self._assert_logouted_phonish_account(self._fake_passport.requests[1])

    def test_logout_portal_account_not_found(self):
        self._setup_grants()
        self._setup_passport()
        self._setup_socialism()
        self._setup_billing()
        self._fake_passport.set_response_side_effect(
            'account_options',
            [
                passport_bundle_api_error_response('account.not_found'),
                passport_ok_response(),
            ],
        )

        rv = self._make_request(
            data={
                'logout_master': '1',
                'logout_phonish': '1',
            },
        )

        self._assert_ok_response(rv)
        self._assert_logouted_portal_account(self._fake_passport.requests[1])
        self._assert_logouted_phonish_account(self._fake_passport.requests[2])

    def test_logout_phonish_account_not_found(self):
        self._setup_grants()
        self._setup_passport()
        self._setup_socialism()
        self._setup_billing()
        self._fake_passport.set_response_side_effect(
            'account_options',
            [
                passport_ok_response(),
                passport_bundle_api_error_response('account.not_found'),
            ],
        )

        rv = self._make_request(
            data={
                'logout_master': '1',
                'logout_phonish': '1',
            },
        )

        self._assert_ok_response(rv)
        self._assert_logouted_portal_account(self._fake_passport.requests[1])
        self._assert_logouted_phonish_account(self._fake_passport.requests[2])

    def test_logout_portal_passport_failed(self):
        self._setup_grants()
        self._setup_passport()
        self._setup_socialism()
        self._setup_billing()
        self._fake_passport.set_response_side_effect(
            'account_options',
            [
                passport_bundle_api_error_response('backend.database_failed'),
            ],
        )

        rv = self._make_request(
            data={
                'logout_master': '1',
                'logout_phonish': '1',
            },
        )

        self._assert_error_response(
            rv,
            ['internal_error'],
            description='Passport failed',
        )
        self._assert_binding_exists()
        self._fake_statbox.assert_equals([])
        self._assert_not_invalidated_billing_cache()

    def test_logout_phonish_passport_failed(self):
        self._setup_grants()
        self._setup_passport()
        self._setup_socialism()
        self._setup_billing()
        self._fake_passport.set_response_side_effect(
            'account_options',
            [
                passport_ok_response(),
                passport_bundle_api_error_response('backend.database_failed'),
            ],
        )

        rv = self._make_request(
            data={
                'logout_master': '1',
                'logout_phonish': '1',
            },
        )

        self._assert_error_response(
            rv,
            ['internal_error'],
            description='Passport failed',
        )
        self._assert_binding_exists()
        self._fake_statbox.assert_equals([])
        self._assert_not_invalidated_billing_cache()
