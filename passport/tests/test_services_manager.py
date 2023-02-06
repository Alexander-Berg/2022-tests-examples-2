# -*- coding: utf-8 -*-
from nose_parameterized import parameterized
from passport.backend.core.mail_subscriptions.services_manager import (
    get_mail_subscription_services_manager,
    SubscriptionService,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)


SENDER_SERVICE_MAIL = dict(
    id=1,
    origin_prefixes=['mail_origin1', 'mail_origin2'],
    app_ids=['ru.yandex.mail', 'ru.yandex.mail2'],
    slug='mail',
    external_list_ids=[10, 11],
)
SENDER_SERVICE_MAPS = dict(
    id=2,
    origin_prefixes=['maps_origin1', 'maps_origin2'],
    app_ids=['ru.yandex.maps', 'ru.yandex.maps2'],
    slug='maps',
    external_list_ids=[20, 21],
)
SENDER_SERVICE_MARKET = dict(
    id=3,
    origin_prefixes=['market_origin1', 'market_origin2'],
    app_ids=['ru.yandex.market', 'ru.yandex.market2'],
    slug='market',
    external_list_ids=[30, 31],
)


def _s(data):
    return SubscriptionService(**data)


@with_settings_hosts(
    SENDER_MAIL_SUBSCRIPTION_SERVICES=[
        SENDER_SERVICE_MAIL,
        SENDER_SERVICE_MAPS,
        SENDER_SERVICE_MARKET,
    ],
)
class TestMailSubscriptionServicesManager(PassportTestCase):
    def _get_manager(self):
        return get_mail_subscription_services_manager()

    def test_get_all_services(self):
        self.assertEqual(
            self._get_manager().get_all_services(),
            [
                _s(SENDER_SERVICE_MAIL),
                _s(SENDER_SERVICE_MAPS),
                _s(SENDER_SERVICE_MARKET),
            ],
        )

    @parameterized.expand([
        (1, _s(SENDER_SERVICE_MAIL)),
        (2, _s(SENDER_SERVICE_MAPS)),
        (3, _s(SENDER_SERVICE_MARKET)),
        (4, None),
    ])
    def test_get_service_by_id(self, service_id, expected):
        self.assertEqual(
            self._get_manager().get_service_by_id(service_id),
            expected,
        )

    @parameterized.expand([
        ('mail_origin1', {_s(SENDER_SERVICE_MAIL)}),
        ('mail_origin2', {_s(SENDER_SERVICE_MAIL)}),
        ('maps_origin1', {_s(SENDER_SERVICE_MAPS)}),
        ('maps_origin2', {_s(SENDER_SERVICE_MAPS)}),
        ('market_origin1', {_s(SENDER_SERVICE_MARKET)}),
        ('market_origin2', {_s(SENDER_SERVICE_MARKET)}),
        ('market_origin2_smth', {_s(SENDER_SERVICE_MARKET)}),
        ('market_origin2smth', set()),
        ('market', set()),
        ('wrong', set()),
    ])
    def get_services_by_origin(self, origin, expected):
        self.assertEqual(
            self._get_manager().get_services_by_origin(origin),
            expected,
        )

    @parameterized.expand([
        ('ru.yandex.mail', {_s(SENDER_SERVICE_MAIL)}),
        ('ru.yandex.mail2', {_s(SENDER_SERVICE_MAIL)}),
        ('ru.yandex.maps', {_s(SENDER_SERVICE_MAPS)}),
        ('ru.yandex.maps2', {_s(SENDER_SERVICE_MAPS)}),
        ('ru.yandex.market', {_s(SENDER_SERVICE_MARKET)}),
        ('ru.yandex.market2', {_s(SENDER_SERVICE_MARKET)}),
        ('ru.yandex.market2.smth', set()),
        ('ru.yandex.market2smth', set()),
        ('wrong', set()),
    ])
    def test_get_services_by_app_id(self, app_id, expected):
        self.assertEqual(
            self._get_manager().get_services_by_app_id(app_id),
            expected,
        )
