# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response_multiple
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
    PHONISH_LOGIN1,
    SOCIAL_LOGIN1,
    UID1,
    UID2,
    UID3,
    UID4,
    USER_IP1,
    USERNAME1,
)


class WhoSharesTaxiDataTestCase(ApiV3TestCase):
    REQUEST_HTTP_METHOD = 'GET'
    REQUEST_URL = '/api/special/who_shares_taxi_data'
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
        super(WhoSharesTaxiDataTestCase, self).setUp()

        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['who-shares-taxi-data'],
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

    def _build_phonish_account(self, uid):
        return dict(
            userinfo=dict(
                uid=uid,
                aliases=dict(phonish=PHONISH_LOGIN1),
            ),
        )

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
        settings = super(WhoSharesTaxiDataTestCase, self).build_settings()
        settings['social_config'].update(max_federation_size=2)
        return settings


class TestWhoSharesTaxiDataAccountNotFound(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataAccountNotFound, self).setUp()
        self._setup_blackbox(subject=None)

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataPortalAccountNoBindings(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPortalAccountNoBindings, self).setUp()
        self._setup_blackbox(subject=self._build_portal_account(uid=UID1))

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataPhonishAccountNoBindings(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPhonishAccountNoBindings, self).setUp()
        self._setup_blackbox(subject=self._build_phonish_account(uid=UID1))

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataMailishAccountParentBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataMailishAccountParentBinding, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._setup_blackbox(
            subject=self._build_mailish_account(uid=UID1),
            related=[self._build_portal_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataMailishAccountParentAndSiblingBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataMailishAccountParentAndSiblingBinding, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._create_binding(UID2, Yandex, UID3)
        self._setup_blackbox(
            subject=self._build_mailish_account(uid=UID1),
            related=[
                self._build_portal_account(uid=UID2),
                self._build_phonish_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataMailishAccountChildBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataMailishAccountChildBinding, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_mailish_account(uid=UID1),
            related=[self._build_phonish_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataPortalAccountParentBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPortalAccountParentBinding, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[self._build_portal_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataPortalAccountParentAndSiblingBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPortalAccountParentAndSiblingBinding, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._create_binding(UID2, Yandex, UID3)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[
                self._build_portal_account(uid=UID2),
                self._build_phonish_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataPortalAccountChildBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPortalAccountChildBinding, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[self._build_phonish_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2)])


class TestWhoSharesTaxiDataPortalAccount150Children(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPortalAccount150Children, self).setUp()
        for i in range(150):
            self._create_binding(UID1, Yandex, i + 100)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[self._build_phonish_account(uid=i+100) for i in range(150)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=['248', '249'])


class TestWhoSharesTaxiDataSocialAccountChildBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataSocialAccountChildBinding, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_social_account(uid=UID1),
            related=[self._build_phonish_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2)])


class TestWhoSharesTaxiDataLiteAccountChildBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataLiteAccountChildBinding, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_lite_account(uid=UID1),
            related=[self._build_phonish_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2)])


class TestWhoSharesTaxiDataPhonishAccountParentBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPhonishAccountParentBinding, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[self._build_portal_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2)])


class TestWhoSharesTaxiDataPhonish150Parents(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPhonish150Parents, self).setUp()
        for i in range(150):
            self._create_binding(i + 100, Yandex, UID1)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[self._build_portal_account(uid=i+100) for i in range(150)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=['248', '249'])


class TestWhoSharesTaxiDataPhonishAccountSiblingBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPhonishAccountSiblingBinding, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID3, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                # Связующий родитель удалён, поэтому до брата не добраться.
                None,
                self._build_phonish_account(uid=UID2),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataPhonishAccountParentAndSiblingBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPhonishAccountParentAndSiblingBinding, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID3, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_phonish_account(uid=UID2),
                self._build_portal_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2), str(UID3)])


class TestWhoSharesTaxiDataPhonish150Siblings(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPhonish150Siblings, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        for i in range(150):
            self._create_binding(UID3, Yandex, i + 100)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[self._build_portal_account(uid=UID3)] + [
                self._build_phonish_account(uid=i+100) for i in range(150)
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=['249', str(UID3)])


class TestWhoSharesTaxiDataPhonish50Parents50Siblings(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPhonish50Parents50Siblings, self).setUp()
        for i in range(50):
            self._create_binding(i+100, Yandex, UID1)
            self._create_binding(i+100, Yandex, i + 1000)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_portal_account(uid=i+100) for i in range(50)
            ] + [
                self._build_phonish_account(uid=i+1000) for i in range(50)
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=['148', '149'])


class TestWhoSharesTaxiDataPhonishAccountPhonishChildBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPhonishAccountPhonishChildBinding, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[self._build_phonish_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataPhonishAccountPortalChildBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPhonishAccountPortalChildBinding, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[self._build_portal_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataManyParentBindings(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataManyParentBindings, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._create_binding(UID3, Yandex, UID1)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_portal_account(uid=UID2),
                self._build_portal_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2), str(UID3)])


class TestWhoSharesTaxiDataManySiblingBindings(WhoSharesTaxiDataTestCase):
    def build_settings(self):
        settings = super(WhoSharesTaxiDataTestCase, self).build_settings()
        settings['social_config'].update(max_federation_size=3)
        return settings

    def setUp(self):
        super(TestWhoSharesTaxiDataManySiblingBindings, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._create_binding(UID2, Yandex, UID3)
        self._create_binding(UID2, Yandex, UID4)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_portal_account(uid=UID2),
                self._build_phonish_account(uid=UID3),
                self._build_phonish_account(uid=UID4),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2), str(UID3), str(UID4)])


class TestWhoSharesTaxiDataManyChildBindings(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataManyChildBindings, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._create_binding(UID1, Yandex, UID3)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[
                self._build_phonish_account(uid=UID2),
                self._build_phonish_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2), str(UID3)])


class TestWhoSharesTaxiDataYandexParentBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataYandexParentBinding, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[self._build_portal_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2)])


class TestWhoSharesTaxiDataVkontakteParentBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataVkontakteParentBinding, self).setUp()
        self._create_binding(UID2, Vkontakte, UID1)
        self._setup_blackbox(subject=self._build_phonish_account(uid=UID1))

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataYandexSiblingBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataYandexSiblingBinding, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID3, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_portal_account(uid=UID3),
                self._build_phonish_account(uid=UID2),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2), str(UID3)])


class TestWhoSharesTaxiDataVkontakteSiblingBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataVkontakteSiblingBinding, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID3, Vkontakte, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[self._build_portal_account(uid=UID3)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID3)])


class TestWhoSharesTaxiDataYandexChildBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataYandexChildBinding, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[self._build_phonish_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2)])


class TestWhoSharesTaxiDataVkontakteChildBinding(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataVkontakteChildBinding, self).setUp()
        self._create_binding(UID1, Vkontakte, UID2)
        self._setup_blackbox(subject=self._build_portal_account(uid=UID1))

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataParentAccountExists(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataParentAccountExists, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[self._build_portal_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2)])


class TestWhoSharesTaxiDataParentAccountNotExist(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataParentAccountNotExist, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[None],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataSiblingAccountExists(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataSiblingAccountExists, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID3, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_portal_account(uid=UID3),
                self._build_phonish_account(uid=UID2),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2), str(UID3)])


class TestWhoSharesTaxiDataSiblingAccountNotExist(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataSiblingAccountNotExist, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID3, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_portal_account(uid=UID3),
                None,
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID3)])


class TestWhoSharesTaxiDataChildAccountExists(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataChildAccountExists, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[self._build_phonish_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2)])


class TestWhoSharesTaxiDataChildAccountNotExist(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataChildAccountNotExist, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[None],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataParentPortal(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataParentPortal, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[self._build_portal_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2)])


class TestWhoSharesTaxiDataParentSocial(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataParentSocial, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[self._build_social_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2)])


class TestWhoSharesTaxiDataParentLite(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataParentLite, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[self._build_lite_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2)])


class TestWhoSharesTaxiDataParentPhonish(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataParentPhonish, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[self._build_phonish_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataParentMailish(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataParentMailish, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[self._build_mailish_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataSiblingPortal(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataSiblingPortal, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID3, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_portal_account(uid=UID2),
                self._build_portal_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID3)])


class TestWhoSharesTaxiDataSiblingSocial(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataSiblingSocial, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID3, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_social_account(uid=UID2),
                self._build_portal_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID3)])


class TestWhoSharesTaxiDataSiblingLite(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataSiblingLite, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID3, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_lite_account(uid=UID2),
                self._build_portal_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID3)])


class TestWhoSharesTaxiDataSiblingPhonish(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataSiblingPhonish, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID3, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_phonish_account(uid=UID2),
                self._build_portal_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2), str(UID3)])


class TestWhoSharesTaxiDataSiblingMailish(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataSiblingMailish, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID3, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_mailish_account(uid=UID2),
                self._build_portal_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID3)])


class TestWhoSharesTaxiDataChildPortal(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataChildPortal, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[self._build_portal_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataChildSocial(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataChildSocial, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[self._build_social_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataChildLite(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataChildLite, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[self._build_lite_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataChildPhonish(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataChildPhonish, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[self._build_phonish_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2)])


class TestWhoSharesTaxiDataChildMailish(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataChildMailish, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[self._build_mailish_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataSiblingWithParentPortal(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataSiblingWithParentPortal, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID3, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_phonish_account(uid=UID2),
                self._build_portal_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2), str(UID3)])


class TestWhoSharesTaxiDataSiblingWithParentSocial(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataSiblingWithParentSocial, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID3, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_phonish_account(uid=UID2),
                self._build_social_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2), str(UID3)])


class TestWhoSharesTaxiDataSiblingWithParentLite(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataSiblingWithParentLite, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID3, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_phonish_account(uid=UID2),
                self._build_lite_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2), str(UID3)])


class TestWhoSharesTaxiDataSiblingWithParentPhonish(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataSiblingWithParentPhonish, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID3, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_phonish_account(uid=UID2),
                self._build_phonish_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataSiblingWithParentMailish(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataSiblingWithParentMailish, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID3, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_phonish_account(uid=UID2),
                self._build_mailish_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiDataTooMuchChildBindings(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataTooMuchChildBindings, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._create_binding(UID1, Yandex, UID3)
        self._create_binding(UID1, Yandex, UID4)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[
                self._build_phonish_account(uid=UID3),
                self._build_phonish_account(uid=UID4),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID3), str(UID4)])
        self._assert_linked_uids_requested_from_blackbox([UID3, UID4])


class TestWhoSharesTaxiDataTooMuchParentBindings(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataTooMuchParentBindings, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID4, Yandex, UID1)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_portal_account(uid=UID3),
                self._build_portal_account(uid=UID4),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID3), str(UID4)])
        self._assert_linked_uids_requested_from_blackbox([UID3, UID4])


class TestWhoSharesTaxiDataTooMuchSiblingBindings(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataTooMuchSiblingBindings, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._create_binding(UID2, Yandex, UID3)
        self._create_binding(UID2, Yandex, UID4)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_portal_account(uid=UID2),
                self._build_phonish_account(uid=UID4),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2), str(UID4)])
        self._assert_linked_uids_requested_from_blackbox([UID2, UID4])


class TestWhoSharesTaxiDataPhonishAccountBindingIsChildAndSibling(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPhonishAccountBindingIsChildAndSibling, self).setUp()
        self._create_binding(UID1, Yandex, UID3)
        self._create_binding(UID2, Yandex, UID1)
        self._create_binding(UID2, Yandex, UID3)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_portal_account(uid=UID2),
                self._build_phonish_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2), str(UID3)])
        self._assert_linked_uids_requested_from_blackbox([UID2, UID3])


class TestWhoSharesTaxiDataPortalAccountBindingIsChildAndSibling(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPortalAccountBindingIsChildAndSibling, self).setUp()
        self._create_binding(UID1, Yandex, UID3)
        self._create_binding(UID2, Yandex, UID1)
        self._create_binding(UID2, Yandex, UID3)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[self._build_phonish_account(uid=UID3)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID3)])
        self._assert_linked_uids_requested_from_blackbox([UID3])


class TestWhoSharesTaxiDataPhonishAccountBindingIsParentAndSibling(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPhonishAccountBindingIsParentAndSibling, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID2, Yandex, UID1)
        self._create_binding(UID2, Yandex, UID3)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[
                self._build_portal_account(uid=UID2),
                self._build_phonish_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        # Нет UID3 потому что по кратчайшему пути UID3 является родителем UID1,
        # т.е. фониш родитель фониша, а такие связи не отдаются ручкой.
        self._assert_who_shares_taxi_data_ok_response(rv, yandex=[str(UID2)])
        self._assert_linked_uids_requested_from_blackbox([UID2, UID3])


class TestWhoSharesTaxiDataPortalAccountBindingIsParentAndSibling(WhoSharesTaxiDataTestCase):
    def setUp(self):
        super(TestWhoSharesTaxiDataPortalAccountBindingIsParentAndSibling, self).setUp()
        self._create_binding(UID3, Yandex, UID1)
        self._create_binding(UID2, Yandex, UID1)
        self._create_binding(UID2, Yandex, UID3)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[
                self._build_portal_account(uid=UID2),
                self._build_phonish_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request()
        # По кратчайшем пути UID3 (портальный) отец UID1 (портальный), а такие
        # связи ручка не отдаёт.
        self._assert_who_shares_taxi_data_ok_response(rv)


class TestWhoSharesTaxiData(WhoSharesTaxiDataTestCase):
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
