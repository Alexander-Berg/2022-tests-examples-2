# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime

from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response_multiple
from passport.backend.core.models.phones.faker import build_phone_bound
from passport.backend.core.types.bit_vector.bit_vector import PhoneBindingsFlags
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.social.api.test import ApiV3TestCase
from passport.backend.social.common.chrono import now
from passport.backend.social.common.db.schemas import profile_table
from passport.backend.social.common.providers.Vkontakte import Vkontakte
from passport.backend.social.common.providers.Yandex import Yandex
from passport.backend.social.common.test.consts import (
    CONSUMER1,
    CONSUMER2,
    CONSUMER_IP1,
    LITE_LOGIN1,
    MAILISH_LOGIN1,
    NEOPHONISH_LOGIN1,
    PHONISH_LOGIN1,
    SOCIAL_LOGIN1,
    UID1,
    UID2,
    UID3,
    UID4,
    UNIXTIME1,
    UNIXTIME2,
    USER_IP1,
    USERNAME1,
)
from passport.backend.utils.common import deep_merge


PHONE_NUMBER1 = PhoneNumber.parse('+79026411724')
PHONE_NUMBER2 = PhoneNumber.parse('+79259164525')


class WhoSharesTaxiDataV2TestCase(ApiV3TestCase):
    REQUEST_HTTP_METHOD = 'GET'
    REQUEST_URL = '/api/special/who_shares_taxi_data_v2'
    REQUEST_QUERY = {
        'consumer': CONSUMER1,
        'provider': Yandex.code,
        'userid': UID1,
    }
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumer-Client-Ip': USER_IP1,
    }

    def setUp(self):
        super(WhoSharesTaxiDataV2TestCase, self).setUp()

        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['who-shares-taxi-data-v2'],
        )

    def _create_binding(self, uid, provider, userid):
        with self._fake_db.no_recording() as db:
            query = profile_table.insert().values(
                uid=uid,
                provider_id=provider.id,
                userid=userid,
                username=USERNAME1,
                created=now(),
            )
            db.execute(query)

    def _assert_who_shares_taxi_data_ok_response(self, rv, yandex=None):
        self._assert_ok_response(
            rv,
            {
                'accounts': {'ya': yandex or []},
            },
        )

    def _setup_blackbox(self, subject, related=None):
        related = related or []

        if subject is None:
            subject = self._build_not_existent_account()

        for i, rel_account in enumerate(related):
            if rel_account is None:
                related[i] = self._build_not_existent_account()

        self._fake_blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response_multiple([subject['userinfo']]),
                blackbox_userinfo_response_multiple([a['userinfo'] for a in related]),
            ],
        )

    def _build_portal_account(self, uid):
        return dict(
            userinfo=dict(uid=uid),
        )

    def _build_social_account(self, uid):
        return dict(
            userinfo=dict(
                uid=uid,
                aliases=dict(social=SOCIAL_LOGIN1),
            ),
        )

    def _build_lite_account(self, uid):
        return dict(
            userinfo=dict(
                uid=uid,
                aliases=dict(social=LITE_LOGIN1),
            ),
        )

    def _build_neophonish_account(self, uid, phone_number, phone_confirmed):
        userinfo = dict(
            uid=uid,
            aliases=dict(neophonish=NEOPHONISH_LOGIN1),
        )
        binding_flags = PhoneBindingsFlags()
        binding_flags.should_ignore_binding_limit = True
        userinfo = deep_merge(
            userinfo,
            build_phone_bound(
                phone_id=1,
                phone_number=phone_number.e164,
                phone_created=datetime.fromtimestamp(phone_confirmed),
                phone_bound=datetime.fromtimestamp(phone_confirmed),
                phone_confirmed=datetime.fromtimestamp(phone_confirmed),
                binding_flags=binding_flags,
            ),
        )

        return dict(userinfo=userinfo)

    def _build_phonish_account(self, uid, phone_number, phone_confirmed):
        userinfo = dict(
            uid=uid,
            aliases=dict(phonish=PHONISH_LOGIN1),
        )
        binding_flags = PhoneBindingsFlags()
        binding_flags.should_ignore_binding_limit = True
        userinfo = deep_merge(
            userinfo,
            build_phone_bound(
                phone_id=1,
                phone_number=phone_number.e164,
                phone_created=datetime.fromtimestamp(phone_confirmed),
                phone_bound=datetime.fromtimestamp(phone_confirmed),
                phone_confirmed=datetime.fromtimestamp(phone_confirmed),
                binding_flags=binding_flags,
            ),
        )

        return dict(userinfo=userinfo)

    def _build_mailish_account(self, uid):
        return dict(
            userinfo=dict(
                uid=uid,
                aliases=dict(mailish=MAILISH_LOGIN1),
            ),
        )

    def _build_not_existent_account(self):
        return dict(
            userinfo=dict(uid=None),
        )

    def _assert_linked_uids_requested_from_blackbox(self, uids):
        self.assertEqual(len(self._fake_blackbox.requests), 2)
        request = self._fake_blackbox.requests[1]
        request.assert_post_data_contains({'uid': ','.join(map(str, uids))})

    def build_settings(self):
        settings = super(WhoSharesTaxiDataV2TestCase, self).build_settings()
        settings['social_config'].update(max_federation_size=2)
        return settings


class TestWhoSharesTaxiDataV2PortalAccountChildBinding(WhoSharesTaxiDataV2TestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataV2PortalAccountChildBinding, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[
                self._build_phonish_account(
                    uid=UID2,
                    phone_number=PHONE_NUMBER1,
                    phone_confirmed=UNIXTIME1,
                ),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(
            rv,
            yandex=[
                {
                    'userid': str(UID2),
                    'phones': [
                        {
                            'number': PHONE_NUMBER1.e164,
                            'confirmed': UNIXTIME1,
                        },
                    ],
                },
            ],
        )


class TestWhoSharesTaxiDataV2Portal150Children(WhoSharesTaxiDataV2TestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataV2Portal150Children, self).setUp()
        for i in range(150):
            self._create_binding(UID1, Yandex, i + 100)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[
                self._build_phonish_account(
                    uid=i+100,
                    phone_number=PHONE_NUMBER1,
                    phone_confirmed=UNIXTIME1,
                ) for i in range(150)
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(
            rv,
            yandex=[
                {
                    'userid': uid,
                    'phones': [
                        {
                            'number': PHONE_NUMBER1.e164,
                            'confirmed': UNIXTIME1,
                        },
                    ],
                } for uid in ['248', '249']
            ],
        )


class TestWhoSharesTaxiDataV2NeophonishAccountChildBinding(WhoSharesTaxiDataV2TestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataV2NeophonishAccountChildBinding, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_neophonish_account(
                uid=UID1,
                phone_number=PHONE_NUMBER1,
                phone_confirmed=UNIXTIME1,
            ),
            related=[
                self._build_phonish_account(
                    uid=UID2,
                    phone_number=PHONE_NUMBER1,
                    phone_confirmed=UNIXTIME1,
                ),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(
            rv,
            yandex=[
                {
                    'userid': str(UID2),
                    'phones': [
                        {
                            'number': PHONE_NUMBER1.e164,
                            'confirmed': UNIXTIME1,
                        },
                    ],
                },
            ],
        )


class TestWhoSharesTaxiDataV2SocialAccountChildBinding(WhoSharesTaxiDataV2TestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataV2SocialAccountChildBinding, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_social_account(uid=UID1),
            related=[
                self._build_phonish_account(
                    uid=UID2,
                    phone_number=PHONE_NUMBER1,
                    phone_confirmed=UNIXTIME1,
                ),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(
            rv,
            yandex=[
                {
                    'userid': str(UID2),
                    'phones': [
                        {
                            'number': PHONE_NUMBER1.e164,
                            'confirmed': UNIXTIME1,
                        },
                    ],
                },
            ],
        )


class TestWhoSharesTaxiDataV2LiteAccountChildBinding(WhoSharesTaxiDataV2TestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataV2LiteAccountChildBinding, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_lite_account(uid=UID1),
            related=[
                self._build_phonish_account(
                    uid=UID2,
                    phone_number=PHONE_NUMBER1,
                    phone_confirmed=UNIXTIME1,
                ),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(
            rv,
            yandex=[
                {
                    'userid': str(UID2),
                    'phones': [
                        {
                            'number': PHONE_NUMBER1.e164,
                            'confirmed': UNIXTIME1,
                        },
                    ],
                },
            ],
        )


class TestWhoSharesTaxiDataV2MailishAccountChildBinding(WhoSharesTaxiDataV2TestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataV2MailishAccountChildBinding, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_mailish_account(uid=UID1),
            related=[
                self._build_phonish_account(
                    uid=UID2,
                    phone_number=PHONE_NUMBER1,
                    phone_confirmed=UNIXTIME1,
                ),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataV2PhonishAccountPortalChildBinding(WhoSharesTaxiDataV2TestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataV2PhonishAccountPortalChildBinding, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(
                uid=UID1,
                phone_number=PHONE_NUMBER1,
                phone_confirmed=UNIXTIME1,
            ),
            related=[self._build_portal_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataV2PhonishAccountPhonishChildBinding(WhoSharesTaxiDataV2TestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataV2PhonishAccountPhonishChildBinding, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(
                uid=UID1,
                phone_number=PHONE_NUMBER1,
                phone_confirmed=UNIXTIME1,
            ),
            related=[
                self._build_phonish_account(
                    uid=UID2,
                    phone_number=PHONE_NUMBER1,
                    phone_confirmed=UNIXTIME1,
                ),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataV2ChildPortal(WhoSharesTaxiDataV2TestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataV2ChildPortal, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[self._build_portal_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataV2VkontakteChildBinding(WhoSharesTaxiDataV2TestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataV2VkontakteChildBinding, self).setUp()
        self._create_binding(UID1, Vkontakte, UID2)
        self._setup_blackbox(subject=self._build_portal_account(uid=UID1))

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataV2AccountNotFound(WhoSharesTaxiDataV2TestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataV2AccountNotFound, self).setUp()
        self._setup_blackbox(subject=None)

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataV2PortalAccountNoBindings(WhoSharesTaxiDataV2TestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataV2PortalAccountNoBindings, self).setUp()
        self._setup_blackbox(subject=self._build_portal_account(uid=UID1))

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataV2ManyChildBindings(WhoSharesTaxiDataV2TestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataV2ManyChildBindings, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._create_binding(UID1, Yandex, UID3)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[
                self._build_phonish_account(
                    uid=UID2,
                    phone_number=PHONE_NUMBER1,
                    phone_confirmed=UNIXTIME1,
                ),
                self._build_phonish_account(
                    uid=UID3,
                    phone_number=PHONE_NUMBER2,
                    phone_confirmed=UNIXTIME2,
                ),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(
            rv,
            yandex=[
                {
                    'userid': str(UID2),
                    'phones': [
                        {
                            'number': PHONE_NUMBER1.e164,
                            'confirmed': UNIXTIME1,
                        },
                    ],
                },
                {
                    'userid': str(UID3),
                    'phones': [
                        {
                            'number': PHONE_NUMBER2.e164,
                            'confirmed': UNIXTIME2,
                        },
                    ],
                },
            ],
        )


class TestWhoSharesTaxiDataV2ChildAccountNotExist(WhoSharesTaxiDataV2TestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataV2ChildAccountNotExist, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[None],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataV2TooMuchChildBindings(WhoSharesTaxiDataV2TestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataV2TooMuchChildBindings, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._create_binding(UID1, Yandex, UID3)
        self._create_binding(UID1, Yandex, UID4)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[
                self._build_phonish_account(
                    uid=UID3,
                    phone_number=PHONE_NUMBER1,
                    phone_confirmed=UNIXTIME1,
                ),
                self._build_phonish_account(
                    uid=UID4,
                    phone_number=PHONE_NUMBER2,
                    phone_confirmed=UNIXTIME2,
                ),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(
            rv,
            yandex=[
                {
                    'userid': str(UID3),
                    'phones': [
                        {
                            'number': PHONE_NUMBER1.e164,
                            'confirmed': UNIXTIME1,
                        },
                    ],
                },
                {
                    'userid': str(UID4),
                    'phones': [
                        {
                            'number': PHONE_NUMBER2.e164,
                            'confirmed': UNIXTIME2,
                        },
                    ],
                },
            ],
        )
        self._assert_linked_uids_requested_from_blackbox([UID3, UID4])


class TestWhoSharesTaxiDataV2RequestPhonesFromBlackbox(WhoSharesTaxiDataV2TestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataV2RequestPhonesFromBlackbox, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[None],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)

        self.assertEqual(len(self._fake_blackbox.requests), 2)
        request = self._fake_blackbox.requests[1]
        request.assert_post_data_contains({
            'getphones': 'all',
            'phone_attributes': '1,2,3,4,5,6',
        })


class TestWhoSharesTaxiDataV2(WhoSharesTaxiDataV2TestCase):
    def test_no_consumer(self):
        rv = self._make_request(exclude_query=['consumer'])
        self._assert_error_response(rv, ['consumer.empty'])

    def test_no_grants(self):
        self._fake_grants_config.add_consumer(CONSUMER2, networks=[CONSUMER_IP1])

        rv = self._make_request(query={'consumer': CONSUMER2})

        self._assert_error_response(rv, ['access.denied'])

    def test_no_provider(self):
        rv = self._make_request(exclude_query=['provider'])
        self._assert_error_response(rv, ['provider.empty'])

    def test_unknown_provider(self):
        rv = self._make_request(query={'provider': 'unknown'})
        self._assert_who_shares_taxi_data_ok_response(rv)

    def test_vkontakte_provider(self):
        rv = self._make_request(query={'provider': Vkontakte.code})
        self._assert_who_shares_taxi_data_ok_response(rv)

    def test_no_userid(self):
        rv = self._make_request(exclude_query=['userid'])
        self._assert_error_response(rv, ['userid.empty'])

    def test_no_userip(self):
        rv = self._make_request(exclude_headers=['Ya-Consumer-Client-Ip'])
        self._assert_error_response(rv, ['user_ip.empty'])
