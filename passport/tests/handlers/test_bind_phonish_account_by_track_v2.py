# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import abc
from datetime import datetime

from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_json_error_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.passport.faker.fake_passport import (
    FakePassport,
    passport_bundle_api_error_response,
    passport_ok_response,
)
from passport.backend.core.models.phones.faker.phones import (
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common.db.schemas import profile_table
from passport.backend.social.common.providers.Yandex import Yandex
from passport.backend.social.common.test.consts import (
    CONSUMER1,
    CONSUMER_IP1,
    LITE_LOGIN1,
    NEOPHONISH_LOGIN1,
    PHONE_ID1,
    PHONE_NUMBER1,
    PHONE_NUMBER2,
    PHONISH_LOGIN1,
    TRACK_ID1,
    UID1 as NEOPHONISH_UID1,
    UID2 as PHONISH_UID1,
    UID3 as LITE_UID1,
    UNIXTIME1,
    USER_IP1,
    USERNAME1,
)
from passport.backend.social.common.test.fake_billing_api import (
    billing_api_invalidate_account_bindings_response,
    FakeBillingApi,
)
from passport.backend.utils.common import deep_merge
from sqlalchemy import (
    and_ as sql_and,
    select as sql_select,
)


SERVICE_TOKEN1 = 'service_token1'
IVORY_COAST_8_DIGITS_PHONE_NUMBER1 = PhoneNumber.parse('+22503123456')
IVORY_COAST_10_DIGITS_PHONE_NUMBER1 = PhoneNumber.parse('+2250103123456')


class IBlackboxResponse(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def kwargs(self):
        pass

    @abc.abstractmethod
    def setup(self):
        pass


class UserinfoBlackboxResponse(IBlackboxResponse):
    def __init__(self):
        self._kwargs = dict()

    @property
    def kwargs(self):
        return self._kwargs

    def setup(self):
        pass


class NeophonishBlackboxResponse(IBlackboxResponse):
    def __init__(self):
        self._userinfo_response = UserinfoBlackboxResponse()
        self._userinfo_response.kwargs.update(
            deep_merge(
                dict(
                    aliases=dict(neophonish=NEOPHONISH_LOGIN1),
                    login=NEOPHONISH_LOGIN1,
                    uid=NEOPHONISH_UID1,
                ),
                build_phone_secured(PHONE_ID1, PHONE_NUMBER1.e164),
            ),
        )

    @classmethod
    def with_phone_number(cls, phone_number):
        self = NeophonishBlackboxResponse()
        self.kwargs.clear()
        self.kwargs.update(
            deep_merge(
                dict(
                    aliases=dict(neophonish=NEOPHONISH_LOGIN1),
                    login=NEOPHONISH_LOGIN1,
                    uid=NEOPHONISH_UID1,
                ),
                build_phone_secured(PHONE_ID1, phone_number.e164),
            ),
        )
        return self

    @property
    def kwargs(self):
        return self._userinfo_response.kwargs

    def setup(self):
        self._userinfo_response.setup()


class PhonishBlackboxResponse(IBlackboxResponse):
    def __init__(self):
        self._userinfo_response = UserinfoBlackboxResponse()
        self._userinfo_response.kwargs.update(
            deep_merge(
                dict(
                    aliases=dict(phonish=PHONISH_LOGIN1),
                    display_name=dict(name=USERNAME1),
                    login=PHONISH_LOGIN1,
                    uid=PHONISH_UID1,
                ),
                build_phone_bound(PHONE_ID1, PHONE_NUMBER1.e164),
            ),
        )

    @classmethod
    def with_phone_number(cls, phone_number):
        self = PhonishBlackboxResponse()
        self.kwargs.clear()
        self.kwargs.update(
            deep_merge(
                dict(
                    aliases=dict(phonish=PHONISH_LOGIN1),
                    login=PHONISH_LOGIN1,
                    uid=PHONISH_UID1,
                ),
                build_phone_bound(PHONE_ID1, phone_number.e164),
            ),
        )
        return self

    @property
    def kwargs(self):
        return self._userinfo_response.kwargs

    def setup(self):
        self._userinfo_response.setup()


class SuperliteBlackboxResponse(IBlackboxResponse):
    def __init__(self):
        self._userinfo_response = UserinfoBlackboxResponse()
        self._userinfo_response.kwargs.update(
            deep_merge(
                dict(
                    aliases=dict(lite=LITE_LOGIN1),
                    login=LITE_LOGIN1,
                    uid=LITE_UID1,
                ),
                build_phone_secured(PHONE_ID1, PHONE_NUMBER1.e164),
            ),
        )

    @property
    def kwargs(self):
        return self._userinfo_response.kwargs

    def setup(self):
        self._userinfo_response.setup()


class BlackboxMultiUserinfoResponse(object):
    def __init__(self, fake_blackbox):
        self._fake_blackbox = fake_blackbox
        self._responses = list()

    @property
    def responses(self):
        return self._responses

    def setup(self):
        self._fake_blackbox.extend_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response_multiple([r.kwargs for r in self._responses]),
            ],
        )


class PhonishUidByPhoneResponse(IBlackboxResponse):
    def __init__(self, fake_passport):
        self._fake_passport = fake_passport
        self._kwargs = dict(uid=PHONISH_UID1)

    @property
    def kwargs(self):
        return self._kwargs

    def setup(self):
        self._fake_passport.extend_response_side_effect(
            'get_phonish_uid_by_phone',
            [
                passport_ok_response(**self.kwargs),
            ],
        )


class BaseBindPhonishAccountByTrackTestEnv(object):
    __metaclass__ = abc.ABCMeta

    def setup(self):
        self.setup_phonish_uid()
        self.setup_master_account_and_phonish()
        self.setup_billing()

    @abc.abstractmethod
    def setup_phonish_uid(self):
        pass

    @abc.abstractmethod
    def setup_master_account_and_phonish(self):
        pass

    @abc.abstractmethod
    def setup_billing(self):
        pass


class BindPhonishAccountByTrackTestEnv(BaseBindPhonishAccountByTrackTestEnv):
    def __init__(
        self,
        fake_billing_api,
        fake_blackbox,
        fake_passport,
    ):
        self._fake_billing_api = fake_billing_api
        self._fake_blackbox = fake_blackbox

        self.phonish_uid_by_phone_response = PhonishUidByPhoneResponse(fake_passport)
        self.phonish_blackbox_response = PhonishBlackboxResponse()
        self.master_account_blackbox_response = NeophonishBlackboxResponse()

        self.phonish_and_master_account_userinfo_response = BlackboxMultiUserinfoResponse(self._fake_blackbox)
        self.phonish_and_master_account_userinfo_response.responses.append(self.phonish_blackbox_response)
        self.phonish_and_master_account_userinfo_response.responses.append(self.master_account_blackbox_response)

    def setup_phonish_uid(self):
        self.phonish_uid_by_phone_response.setup()

    def setup_master_account_and_phonish(self):
        for _ in range(2):
            self.phonish_and_master_account_userinfo_response.setup()

    def setup_billing(self):
        self._fake_billing_api.set_response_value(
            'invalidate_account_bindings',
            billing_api_invalidate_account_bindings_response(),
        )


class TestBindPhonishAccountByTrack(TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/bind_phonish_account_by_track_v2'
    REQUEST_HEADERS = {
        'Ya-Consumer-Client-Ip': USER_IP1,
        'X-Real-Ip': CONSUMER_IP1,
    }
    REQUEST_DATA = dict(
        consumer=CONSUMER1,
        uid=NEOPHONISH_UID1,
        track_id=TRACK_ID1,
    )

    def setUp(self):
        super(TestBindPhonishAccountByTrack, self).setUp()

        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['bind-phonish-account-by-track'],
        )

        self._fake_passport = FakePassport()
        self._fake_billing_api = FakeBillingApi()

        self.__patches = [
            self._fake_billing_api,
            self._fake_passport,
        ]
        for patch in self.__patches:
            patch.start()

        self._test_env = BindPhonishAccountByTrackTestEnv(
            self._fake_billing_api,
            self._fake_blackbox,
            self._fake_passport,
        )

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()

        super(TestBindPhonishAccountByTrack, self).tearDown()

    def build_settings(self):
        settings = super(TestBindPhonishAccountByTrack, self).build_settings()
        settings['social_config'].update(
            dict(
                account_binding_allow_device_id_check=True,
                billing_http_api_retries=1,
                billing_http_api_timeout=1,
                billing_http_api_url='http://balance-simple.yandex.net:8028/',
                billing_http_api_service_token=SERVICE_TOKEN1,
                blackbox_url='https://blackbox.yandex.net/blackbox',
                invalidate_billing_binding_cache=True,
                passport_api_consumer='socialism',
                passport_api_retries=1,
                passport_api_timeout=1,
                passport_api_url='https://passport-internal.yandex.ru',
            ),
        )
        return settings

    def _assert_binding_exists(self, uid, provider, userid):
        bindings = self._find_bindings(uid, provider, userid)
        self.assertEqual(len(bindings), 1)
        binding = bindings[0]

        self.assertEqual(binding.allow_auth, 0)
        self.assertEqual(binding.created, DatetimeNow())
        self.assertEqual(binding.username, '')

    def _find_bindings(self, uid, provider, userid):
        with self._fake_db.no_recording() as db:
            query = (
                sql_select([profile_table])
                .where(
                    sql_and(
                        profile_table.c.uid == uid,
                        profile_table.c.provider_id == provider.id,
                        profile_table.c.userid == userid,
                    ),
                )
            )
            return db.execute(query).fetchall()

    def _create_binding(self, uid, provider, userid):
        with self._fake_db.no_recording() as db:
            query = profile_table.insert().values(
                uid=uid,
                provider_id=provider.id,
                userid=userid,
                created=datetime.fromtimestamp(UNIXTIME1),
            )
            db.execute(query)

    def _assert_passport_request_ok(self, request):
        request.assert_url_starts_with('https://passport-internal.yandex.ru/1/bundle/account/phonish/uid_by_phone/?')

        query = dict(
            consumer='socialism',
            track_id=TRACK_ID1,
            use_device_id='True',
        )
        request.assert_query_equals(query)
        request.assert_properties_equal(
            headers={
                'X-Ya-Service-Ticket': self.get_ticket_from_tvm_alias('passport'),
                'Ya-Consumer-Client-Ip': USER_IP1,
            },
        )

    def _assert_blackbox_request_ok(self, request):
        request.assert_url_starts_with('https://blackbox.yandex.net/blackbox')
        request.assert_contains_attributes(
            {
                'account.is_disabled',
                'phones.secure',
                'phones.default',
            },
        )
        request.assert_post_data_contains(
            dict(
                aliases='all',
                format='json',
                getphonebindings='all',
                getphones='all',
                is_display_name_empty='yes',
                method='userinfo',
                phone_attributes='1,2,3,4,5,6',
                regname='yes',
                uid=str(NEOPHONISH_UID1) + ',' + str(PHONISH_UID1),
                userip=USER_IP1,
            ),
        )

    def _assert_blackbox_request_ok1(self, request):
        request.assert_url_starts_with('https://blackbox.yandex.net/blackbox')
        request.assert_post_data_contains(
            dict(
                uid=str(NEOPHONISH_UID1) + ',' + str(PHONISH_UID1),
                format='json',
                method='userinfo',
            ),
        )

    def _build_bind_phonish_account_by_track_ok_response(
        self,
        old=False,
        uid=NEOPHONISH_UID1,
    ):
        response = dict(
            uid=uid,
            phonish_uid=PHONISH_UID1,
        )
        if old:
            response.update(old=True)
        return response

    def test_ok(self):
        self._test_env.setup()
        rv = self._make_request()

        self._assert_ok_response(rv, self._build_bind_phonish_account_by_track_ok_response())
        self._assert_binding_exists(uid=NEOPHONISH_UID1, provider=Yandex, userid=PHONISH_UID1)

        self.assertEqual(len(self._fake_passport.requests), 1)
        self._assert_passport_request_ok(self._fake_passport.requests[0])

        self.assertEqual(len(self._fake_blackbox.requests), 2)
        self._assert_blackbox_request_ok(self._fake_blackbox.requests[0])
        self._assert_blackbox_request_ok1(self._fake_blackbox.requests[1])

    def test_binding_already_exists(self):
        self._create_binding(NEOPHONISH_UID1, Yandex, PHONISH_UID1)
        self._test_env.setup()

        rv = self._make_request()

        self._assert_ok_response(rv, self._build_bind_phonish_account_by_track_ok_response(old=True))

        bindings = self._find_bindings(NEOPHONISH_UID1, Yandex, PHONISH_UID1)
        self.assertEqual(len(bindings), 1)
        binding = bindings[0]
        self.assertEqual(binding.created, datetime.fromtimestamp(UNIXTIME1))

    def test_other_accounts_order(self):
        def setup_master_account_and_phonish():
            phonish_and_master_account_userinfo_response = BlackboxMultiUserinfoResponse(self._fake_blackbox)
            phonish_and_master_account_userinfo_response.responses.append(NeophonishBlackboxResponse())
            phonish_and_master_account_userinfo_response.responses.append(PhonishBlackboxResponse())
            for _ in range(2):
                phonish_and_master_account_userinfo_response.setup()

        self._test_env.setup_master_account_and_phonish = setup_master_account_and_phonish
        self._test_env.setup()

        rv = self._make_request()

        self._assert_ok_response(rv, self._build_bind_phonish_account_by_track_ok_response())
        self._assert_binding_exists(uid=NEOPHONISH_UID1, provider=Yandex, userid=PHONISH_UID1)

    def test_no_uid(self):
        self._test_env.setup()

        rv = self._make_request(exclude_data=['uid'])

        self._assert_error_response(rv, ['uid.empty'])

    def test_empty_uid(self):
        self._test_env.setup()

        rv = self._make_request(data=dict(uid=''))

        self._assert_error_response(rv, ['uid.empty'])

    def test_no_track_id(self):
        self._test_env.setup()

        rv = self._make_request(exclude_data=['track_id'])

        self._assert_error_response(rv, ['track_id.empty'])

    def test_empty_track_id(self):
        self._test_env.setup()

        rv = self._make_request(data=dict(track_id=''))

        self._assert_error_response(rv, ['track_id.empty'])

    def test_track_not_found(self):
        def setup_phonish_uid():
            self._fake_passport.extend_response_side_effect(
                'get_phonish_uid_by_phone',
                [
                    passport_bundle_api_error_response('track.not_found'),
                ],
            )

        self._test_env.setup_phonish_uid = setup_phonish_uid
        self._test_env.setup()

        rv = self._make_request()

        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_track_invalid_state(self):
        def setup_phonish_uid():
            self._fake_passport.extend_response_side_effect(
                'get_phonish_uid_by_phone',
                [
                    passport_bundle_api_error_response('track.invalid_state'),
                ],
            )

        self._test_env.setup_phonish_uid = setup_phonish_uid
        self._test_env.setup()

        rv = self._make_request()

        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_phone_not_verified(self):
        def setup_phonish_uid():
            self._fake_passport.extend_response_side_effect(
                'get_phonish_uid_by_phone',
                [
                    passport_bundle_api_error_response('user.not_verified'),
                ],
            )

        self._test_env.setup_phonish_uid = setup_phonish_uid
        self._test_env.setup()

        rv = self._make_request()

        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_phonish_disabled(self):
        def setup_phonish_uid():
            self._fake_passport.extend_response_side_effect(
                'get_phonish_uid_by_phone',
                [
                    passport_bundle_api_error_response('account.disabled'),
                ],
            )

        self._test_env.setup_phonish_uid = setup_phonish_uid
        self._test_env.phonish_blackbox_response.kwargs.update(enabled=False)
        self._test_env.setup()

        rv = self._make_request()

        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_phonish_not_found_by_phone(self):
        def setup_phonish_uid():
            self._fake_passport.extend_response_side_effect(
                'get_phonish_uid_by_phone',
                [
                    passport_bundle_api_error_response('account.not_found'),
                ],
            )

        self._test_env.setup_phonish_uid = setup_phonish_uid
        self._test_env.setup()

        rv = self._make_request()

        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_passport_temporary_failed(self):
        def setup_phonish_uid():
            self._fake_passport.extend_response_side_effect(
                'get_phonish_uid_by_phone',
                [
                    passport_bundle_api_error_response('backend.blackbox_failed'),
                ],
            )

        self._test_env.setup_phonish_uid = setup_phonish_uid
        self._test_env.setup()

        rv = self._make_request()

        self._assert_error_response(rv, ['internal_error'], 'Passport failed')

    def test_passport_unknown_error(self):
        def setup_phonish_uid():
            self._fake_passport.extend_response_side_effect(
                'get_phonish_uid_by_phone',
                [
                    passport_bundle_api_error_response('unknown'),
                ],
            )

        self._test_env.setup_phonish_uid = setup_phonish_uid
        self._test_env.setup()

        rv = self._make_request()

        self._assert_error_response(rv, ['internal_error'], 'Passport failed')

    def test_phonish_not_found_by_uid(self):
        self._test_env.phonish_blackbox_response.kwargs.update(id=PHONISH_UID1, uid=None)
        self._test_env.setup()

        rv = self._make_request()

        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_master_account_not_found(self):
        self._test_env.master_account_blackbox_response.kwargs.update(id=NEOPHONISH_UID1, uid=None)
        self._test_env.setup()

        rv = self._make_request()

        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_master_account_disabled(self):
        self._test_env.master_account_blackbox_response.kwargs.update(enabled=False)
        self._test_env.setup()

        rv = self._make_request()

        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_master_account_is_superlite(self):
        def setup_master_account_and_phonish():
            response = BlackboxMultiUserinfoResponse(self._fake_blackbox)
            response.responses.append(SuperliteBlackboxResponse())
            response.responses.append(PhonishBlackboxResponse())
            for _ in range(2):
                response.setup()

        self._test_env.setup_master_account_and_phonish = setup_master_account_and_phonish
        self._test_env.setup()

        rv = self._make_request(data=dict(uid=str(LITE_UID1)))

        self._assert_ok_response(rv, self._build_bind_phonish_account_by_track_ok_response(uid=LITE_UID1))
        self._assert_binding_exists(uid=LITE_UID1, provider=Yandex, userid=PHONISH_UID1)

    def test_master_account_is_phonish(self):
        def setup_master_account_and_phonish():
            response = BlackboxMultiUserinfoResponse(self._fake_blackbox)
            master_response = PhonishBlackboxResponse()
            master_response.kwargs.update(uid=NEOPHONISH_UID1)
            response.responses.append(master_response)
            response.responses.append(PhonishBlackboxResponse())
            for _ in range(2):
                response.setup()

        self._test_env.setup_master_account_and_phonish = setup_master_account_and_phonish
        self._test_env.setup()

        rv = self._make_request()

        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_different_phone_numbers(self):
        self._test_env.phonish_blackbox_response = PhonishBlackboxResponse.with_phone_number(PHONE_NUMBER2)
        self._test_env.phonish_and_master_account_userinfo_response.responses[0] = self._test_env.phonish_blackbox_response
        self._test_env.setup()

        rv = self._make_request()

        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_blackbox_temporary_failed(self):
        def setup_master_account_and_phonish():
            self._fake_blackbox.extend_response_side_effect(
                'userinfo',
                [
                    blackbox_json_error_response('DB_EXCEPTION'),
                ],
            )
        self._test_env.setup_master_account_and_phonish = setup_master_account_and_phonish
        self._test_env.setup()

        rv = self._make_request()

        self._assert_error_response(rv, ['internal_error'], 'Blackbox failed')

    def test_ivory_coast_10d_phone_number(self):
        self.check_ivory_coast_phone_number(
            master_account_phone_number=IVORY_COAST_10_DIGITS_PHONE_NUMBER1,
            phonish_phone_number=IVORY_COAST_8_DIGITS_PHONE_NUMBER1,
        )

    def test_ivory_coast_8d_phone_number(self):
        self.check_ivory_coast_phone_number(
            master_account_phone_number=IVORY_COAST_8_DIGITS_PHONE_NUMBER1,
            phonish_phone_number=IVORY_COAST_10_DIGITS_PHONE_NUMBER1,
        )

    def check_ivory_coast_phone_number(self, master_account_phone_number, phonish_phone_number):
        self._test_env.phonish_blackbox_response = PhonishBlackboxResponse.with_phone_number(phonish_phone_number)
        self._test_env.phonish_and_master_account_userinfo_response.responses[0] = self._test_env.phonish_blackbox_response

        self._test_env.master_account_blackbox_response = NeophonishBlackboxResponse.with_phone_number(master_account_phone_number)
        self._test_env.phonish_and_master_account_userinfo_response.responses[1] = self._test_env.master_account_blackbox_response

        self._test_env.setup()

        rv = self._make_request()

        self._assert_ok_response(rv, self._build_bind_phonish_account_by_track_ok_response())
        self._assert_binding_exists(uid=NEOPHONISH_UID1, provider=Yandex, userid=PHONISH_UID1)
