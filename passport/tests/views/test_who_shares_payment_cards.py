# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response_multiple
from passport.backend.social.api.test import ApiV3TestCase
from passport.backend.social.common.chrono import now
from passport.backend.social.common.db.schemas import profile_table
from passport.backend.social.common.providers.Kinopoisk import Kinopoisk
from passport.backend.social.common.providers.Vkontakte import Vkontakte
from passport.backend.social.common.providers.Yandex import Yandex
from passport.backend.social.common.test.consts import (
    CONSUMER1,
    CONSUMER2,
    CONSUMER_IP1,
    NEOPHONISH_LOGIN1,
    PHONISH_LOGIN1,
    SIMPLE_USERID1,
    UID1,
    UID2,
    UID3,
    UID4,
    USER_IP1,
    USERNAME1,
)


class WhoSharesPaymentCardsTestCase(ApiV3TestCase):
    REQUEST_HTTP_METHOD = 'GET'
    REQUEST_URL = '/api/special/who_shares_payment_cards'
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
        super(WhoSharesPaymentCardsTestCase, self).setUp()

        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['who-shares-payment-cards'],
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

    def _assert_who_shares_payment_cards_ok_response(self, rv, yandex=None, kinopoisk=None):
        self._assert_ok_response(
            rv,
            {
                'accounts': {
                    'kp': kinopoisk or [],
                    'ya': yandex or [],
                },
            },
        )

    def _setup_blackbox(self, subject, related=None):
        related = related or []

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

    def _build_neophonish_account(self, uid):
        return dict(
            userinfo=dict(
                uid=uid,
                aliases=dict(neophonish=NEOPHONISH_LOGIN1),
            ),
        )

    def _build_phonish_account(self, uid):
        return dict(
            userinfo=dict(
                uid=uid,
                aliases=dict(phonish=PHONISH_LOGIN1),
            ),
        )

    def _build_kinopoisk_account(self, uid):
        return dict(
            userinfo=dict(
                uid=uid,
                aliases=dict(kinopoisk=str(uid)),
            ),
        )

    def _build_not_existent_account(self, uid):
        return dict(
            userinfo=dict(
                id=uid,
                uid=None,
            ),
        )

    def _assert_linked_uids_requested_from_blackbox(self, uids):
        self.assertEqual(len(self._fake_blackbox.requests), 2)
        request = self._fake_blackbox.requests[1]
        request.assert_post_data_contains({'uid': ','.join(map(str, uids))})

    def build_settings(self):
        settings = super(WhoSharesPaymentCardsTestCase, self).build_settings()
        settings['social_config'].update(max_federation_size=2)
        return settings


class TestWhoSharesPaymentCardsNoBindings(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsNoBindings, self).setUp()
        self._setup_blackbox(subject=self._build_portal_account(uid=UID1))

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_payment_cards_ok_response(rv)


class TestWhoSharesPaymentCardsAccountNotFound(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsAccountNotFound, self).setUp()
        self._setup_blackbox(subject=self._build_not_existent_account(UID1))

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_payment_cards_ok_response(rv)


class TestWhoSharesPaymentCardsYandexBinding(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsYandexBinding, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[self._build_phonish_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_payment_cards_ok_response(rv, yandex=[str(UID2)])


class TestWhoSharesPaymentCardsYandexBindingNeophonish(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsYandexBindingNeophonish, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_neophonish_account(uid=UID1),
            related=[self._build_phonish_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_payment_cards_ok_response(rv, yandex=[str(UID2)])


class TestWhoSharesPaymentCardsManyYandexBindings(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsManyYandexBindings, self).setUp()
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
        self._assert_who_shares_payment_cards_ok_response(rv, yandex=[str(UID2), str(UID3)])


class TestWhoSharesPaymentCardsSubjectIsPhonish(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsSubjectIsPhonish, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_phonish_account(uid=UID1),
            related=[self._build_phonish_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_payment_cards_ok_response(rv)


class TestWhoSharesPaymentCardsYandexBindingIsPortal(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsYandexBindingIsPortal, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[self._build_portal_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_payment_cards_ok_response(rv)


class TestWhoSharesPaymentCardsAccountHasVkontakteBinding(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsAccountHasVkontakteBinding, self).setUp()
        self._create_binding(UID1, Vkontakte, SIMPLE_USERID1)
        self._setup_blackbox(subject=self._build_portal_account(uid=UID1))

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_payment_cards_ok_response(rv)


class TestWhoSharesPaymentCardsYandexAccountIsSlave(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsYandexAccountIsSlave, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._setup_blackbox(subject=self._build_phonish_account(uid=UID1))

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_payment_cards_ok_response(rv, yandex=[])


class TestWhoSharesPaymentCardsYandexAccountIsSibling(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsYandexAccountIsSibling, self).setUp()
        self._create_binding(UID2, Yandex, UID1)
        self._create_binding(UID2, Yandex, UID3)
        self._setup_blackbox(subject=self._build_phonish_account(uid=UID1))

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_payment_cards_ok_response(rv, yandex=[])


class TestWhoSharesPaymentCardsVkontakteAccount(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsVkontakteAccount, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._create_binding(UID1, Vkontakte, SIMPLE_USERID1)

    def test(self):
        rv = self._make_request(query={'provider': Vkontakte.code})
        self._assert_who_shares_payment_cards_ok_response(rv)


class TestWhoSharesPaymentCards(WhoSharesPaymentCardsTestCase):
    def test_no_consumer(self):
        rv = self._make_request(exclude_query=['consumer'])
        self._assert_error_response(rv, ['consumer.empty'])

    def test_no_provider(self):
        rv = self._make_request(exclude_query=['provider'])
        self._assert_error_response(rv, ['provider.empty'])

    def test_unknown_provider(self):
        rv = self._make_request(query={'provider': 'unknown'})
        self._assert_who_shares_payment_cards_ok_response(rv)

    def test_no_userid(self):
        rv = self._make_request(exclude_query=['userid'])
        self._assert_error_response(rv, ['userid.empty'])

    def test_no_grants(self):
        self._fake_grants_config.add_consumer(CONSUMER2, networks=[CONSUMER_IP1])

        rv = self._make_request(query={'consumer': CONSUMER2})

        self._assert_error_response(rv, ['access.denied'])

    def test_no_userip(self):
        rv = self._make_request(exclude_headers=['Ya-Consumer-Client-Ip'])
        self._assert_error_response(rv, ['user_ip.empty'])


class TestWhoSharesPaymentCardsTooMuchBindings(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsTooMuchBindings, self).setUp()
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

        self._assert_who_shares_payment_cards_ok_response(
            rv,
            yandex=[str(UID3), str(UID4)],
        )
        self._assert_linked_uids_requested_from_blackbox([UID3, UID4])


class TestWhoSharesPaymentCardsCuttingEdgeBindings(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsCuttingEdgeBindings, self).setUp()
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

        self._assert_who_shares_payment_cards_ok_response(rv, yandex=[str(UID2), str(UID3)])
        self._assert_linked_uids_requested_from_blackbox([UID2, UID3])


class TestWhoSharesPaymentCardsKinopoiskBinding(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsKinopoiskBinding, self).setUp()
        self._create_binding(UID1, Kinopoisk, UID2)
        self._setup_blackbox(subject=self._build_portal_account(uid=UID1))

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_payment_cards_ok_response(rv, kinopoisk=[str(UID2)])


class TestWhoSharesPaymentCardsManyKinopoiskBindings(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsManyKinopoiskBindings, self).setUp()
        self._create_binding(UID1, Kinopoisk, UID2)
        self._create_binding(UID1, Kinopoisk, UID3)
        self._setup_blackbox(subject=self._build_portal_account(uid=UID1))

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_payment_cards_ok_response(rv, kinopoisk=[str(UID2), str(UID3)])


class TestWhoSharesPaymentCardsManyDifferentBindings(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsManyDifferentBindings, self).setUp()
        self._create_binding(UID1, Yandex, UID2)
        self._create_binding(UID1, Kinopoisk, UID3)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[self._build_phonish_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request()
        self._assert_who_shares_payment_cards_ok_response(
            rv,
            kinopoisk=[str(UID3)],
            yandex=[str(UID2)],
        )


class TestWhoSharesPaymentCardsKinopoiskAccountPhonishSibling(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsKinopoiskAccountPhonishSibling, self).setUp()
        self._create_binding(UID3, Kinopoisk, UID1)
        self._create_binding(UID3, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_kinopoisk_account(uid=UID1),
            related=[
                self._build_phonish_account(uid=UID2),
                self._build_portal_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request(query={'provider': Kinopoisk.code})
        self._assert_who_shares_payment_cards_ok_response(
            rv,
            yandex=[str(UID2), str(UID3)],
        )


class TestWhoSharesPaymentCardsKinopoiskAccountKinopoiskSibling(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsKinopoiskAccountKinopoiskSibling, self).setUp()
        self._create_binding(UID3, Kinopoisk, UID1)
        self._create_binding(UID3, Kinopoisk, UID2)
        self._setup_blackbox(
            subject=self._build_kinopoisk_account(uid=UID1),
            related=[self._build_portal_account(uid=UID3)],
        )

    def test(self):
        rv = self._make_request(query={'provider': Kinopoisk.code})
        self._assert_who_shares_payment_cards_ok_response(
            rv,
            kinopoisk=[str(UID2)],
            yandex=[str(UID3)],
        )


class TestWhoSharesPaymentCardsKinopoiskAccountVkontakteSibling(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsKinopoiskAccountVkontakteSibling, self).setUp()
        self._create_binding(UID3, Kinopoisk, UID1)
        self._create_binding(UID3, Vkontakte, UID2)
        self._setup_blackbox(
            subject=self._build_kinopoisk_account(uid=UID1),
            related=[self._build_portal_account(uid=UID3)],
        )

    def test(self):
        rv = self._make_request(query={'provider': Kinopoisk.code})
        self._assert_who_shares_payment_cards_ok_response(rv, yandex=[str(UID3)])


class TestWhoSharesPaymentCardsKinopoiskAccountPhonishSiblingParentAccountNotFound(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsKinopoiskAccountPhonishSiblingParentAccountNotFound, self).setUp()
        self._create_binding(UID3, Kinopoisk, UID1)
        self._create_binding(UID3, Yandex, UID2)
        self._setup_blackbox(
            subject=self._build_kinopoisk_account(uid=UID1),
            related=[
                self._build_phonish_account(uid=UID2),
                self._build_not_existent_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request(query={'provider': Kinopoisk.code})
        self._assert_who_shares_payment_cards_ok_response(rv)


class TestWhoSharesPaymentCardsKinopoiskAccountManyParents(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsKinopoiskAccountManyParents, self).setUp()
        self._create_binding(UID2, Kinopoisk, UID1)
        self._create_binding(UID3, Kinopoisk, UID1)
        self._setup_blackbox(
            subject=self._build_kinopoisk_account(uid=UID1),
            related=[
                self._build_portal_account(uid=UID2),
                self._build_portal_account(uid=UID3),
            ],
        )

    def test(self):
        rv = self._make_request(query={'provider': Kinopoisk.code})
        self._assert_who_shares_payment_cards_ok_response(rv, yandex=[str(UID2), str(UID3)])


class TestWhoSharesPaymentCardsProviderYandexUseridKinopoisk(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsProviderYandexUseridKinopoisk, self).setUp()
        self._create_binding(UID2, Kinopoisk, UID1)
        self._setup_blackbox(
            subject=self._build_kinopoisk_account(uid=UID1),
            related=[self._build_portal_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request(query={'provider': Yandex.code})
        self._assert_who_shares_payment_cards_ok_response(rv, yandex=[])


class TestWhoSharesPaymentCardsProviderKinopoiskUseridYandex(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsProviderKinopoiskUseridYandex, self).setUp()
        self._create_binding(UID1, Kinopoisk, UID2)
        self._setup_blackbox(
            subject=self._build_portal_account(uid=UID1),
            related=[self._build_kinopoisk_account(uid=UID2)],
        )

    def test(self):
        rv = self._make_request(query={'provider': Kinopoisk.code})
        self._assert_who_shares_payment_cards_ok_response(rv, yandex=[])


class TestWhoSharesPaymentCardsKinopoiskAccountManySiblings(WhoSharesPaymentCardsTestCase):
    def setUp(self):
        super(TestWhoSharesPaymentCardsKinopoiskAccountManySiblings, self).setUp()
        self._create_binding(UID2, Kinopoisk, UID1)
        self._create_binding(UID2, Yandex, UID3)
        self._create_binding(UID2, Yandex, UID4)
        self._setup_blackbox(
            subject=self._build_kinopoisk_account(uid=UID1),
            related=[
                self._build_portal_account(uid=UID2),
                self._build_phonish_account(uid=UID3),
                self._build_phonish_account(uid=UID4),
            ],
        )

    def test(self):
        rv = self._make_request(query={'provider': Kinopoisk.code})
        self._assert_who_shares_payment_cards_ok_response(
            rv,
            yandex=[str(UID2), str(UID3), str(UID4)],
        )

    def build_settings(self):
        settings = super(WhoSharesPaymentCardsTestCase, self).build_settings()
        settings['social_config'].update(max_federation_size=3)
        return settings
