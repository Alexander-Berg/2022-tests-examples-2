# -*- coding: utf-8 -*-
import datetime

import pytest

from taxi import config
from taxi.conf import settings
from taxi.core import async
from taxi.internal import dbh
from taxi.internal.order_kit import const
from taxi.internal.order_kit import payment_helpers


BILLING_VEZET = 'vezet'


@pytest.mark.parametrize('order_data,billings,expected_billing', [
    (
        {'payment_tech': {'type': const.CORP}},
        {settings.BILLING_CARD: {}},
        settings.BILLING_CORP,
    ),
    (
        {'payment_tech': {'type': const.PERSONAL_WALLET}},
        {settings.BILLING_PERSONAL_WALLET: {}},
        settings.BILLING_CARD,
    ),
    (
        {'payment_tech': {'type': const.COOP_ACCOUNT}},
        {settings.BILLING_COOP_ACCOUNT: {}},
        settings.BILLING_CARD,
    ),
    (
        {'payment_tech': {'type': const.CARD}},
        {settings.BILLING_CARD: {}},
        settings.BILLING_CARD,
    ),
    (
        {},
        {settings.BILLING_CARD: {}},
        settings.BILLING_CARD,
    ),
    (
        {'source': const.YANDEX_SOURCE},
        {settings.BILLING_CARD: {}},
        settings.BILLING_CARD,
    ),
    (
        {
            'source': const.YANDEX_SOURCE,
            'statistics': {'application': 'android'},
        },
        {settings.BILLING_CARD: {}},
        settings.BILLING_CARD,
    ),
    (
        {
            'source': const.UBER_SOURCE,
            'statistics': {'application': 'uber_android'},
        },
        {settings.BILLING_CARD: {}},
        settings.BILLING_CARD,
    ),
    (
        {
            'source': const.UBER_SOURCE,
            'statistics': {'application': 'uber_android'},
        },
        {settings.BILLING_CARD: {}, settings.BILLING_UBER: {}},
        settings.BILLING_UBER,
    ),
    (
        {
            'source': const.YAUBER_SOURCE,
            'statistics': {'application': 'uber_android'},
        },
        {settings.BILLING_CARD: {}, settings.BILLING_UBER: {}},
        settings.BILLING_UBER,
    ),
])
@pytest.mark.parametrize('billing_by_brand_enabled', [False, True])
@pytest.inline_callbacks
def test_billing_service_type_from_order(
        monkeypatch, order_data, billings, expected_billing,
        billing_by_brand_enabled,
):
    monkeypatch.setattr(settings, 'BILLINGS', billings)
    yield config.BILLING_SERVICE_NAME_MAP_BY_BRAND_ENABLED.save(
        billing_by_brand_enabled,
    )
    actual_billing = yield payment_helpers.billing_service_type_from_order(
        dbh.orders.Doc(order_data), caller_id='tests',
    )
    assert actual_billing == expected_billing


@pytest.mark.config(
    BILLING_SERVICE_NAME_MAP_BY_BRAND_ENABLED=True,
    BILLING_SERVICE_NAME_MAP_BY_BRAND={
        '__default__': 'card',
        'yataxi': 'card',
        'yango': 'card',
        'yauber': 'uber',
        'vezet': 'vezet',
    },
)
@pytest.mark.parametrize('application', [
    'android', 'iphone', 'uber_android', 'vezet_android', 'yango_iphone',
    'rutaxi_android', 'unknown_app', None,
])
@pytest.mark.parametrize('billings', [
    {},
    {settings.BILLING_CARD: {}},
    {settings.BILLING_UBER: {}},
    {settings.BILLING_CARD: {}, settings.BILLING_UBER: {}},
    {settings.BILLING_CARD: {}, settings.BILLING_UBER: {}, BILLING_VEZET: {}},
])
@pytest.inline_callbacks
def test_get_billing_by_brand(monkeypatch, application, billings):
    monkeypatch.setattr(settings, 'BILLINGS', billings)

    order_data = {'statistics': {'application': application}}

    brand_map = yield config.APPLICATION_MAP_BRAND.get()
    brand = brand_map.get(application) or brand_map.get('__default__')

    billing_map = yield config.BILLING_SERVICE_NAME_MAP_BY_BRAND.get()
    expected_billing = billing_map.get(brand) or billing_map.get('__default__')

    if expected_billing not in billings:
        expected_billing = settings.BILLING_CARD

    actual_billing = yield payment_helpers.billing_service_type_from_order(
        dbh.orders.Doc(order_data), caller_id='tests',
    )
    assert actual_billing == expected_billing


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('use_resp_code,non_technical_errors,input,output', [
    # По умолчанию ошибка считается нетехнической
    (True, [], {}, False),
    (False, [], {}, False),
    # Техническая ошибка, если payment_resp_code из BILLING_RESP_CODE_TECHNICAL_ERRORS
    (
        True,
        [],
        {'payment_resp_code': 'payment_gateway_technical_error'},
        True
    ),
    # Нетехническая ошибка, если payment_resp_code не из BILLING_RESP_CODE_TECHNICAL_ERRORS
    (
        True,
        [],
        {'payment_resp_code': 'expired_card'},
        False
    ),
    # Нетехническая ошибка, если payment_resp_code из BILLING_RESP_CODE_NON_TECHNICAL_ERRORS
    (
        True,
        ['non_technical_error'],
        {'payment_resp_code': 'non_technical_error'},
        False
    ),
    # Нетехническая ошибка, если payment_resp_code не из заданного BILLING_RESP_CODE_NON_TECHNICAL_ERRORS
    (
        True,
        ['non_technical_error'],
        {'payment_resp_code': 'expired_card'},
        True
    ),
    # Старый вариант парсинга status_desc, ошибка из BILLING_TECHNICAL_ERRORS
    (
        False,
        [],
        {'status_desc': 'http 500 Internal Server Error'},
        True
    ),
    # Старый вариант парсинга status_desc, ошибка не из BILLING_TECHNICAL_ERRORS
    (
        False,
        [],
        {'status_desc': '3D Secure check failed'},
        False
    ),
])
@pytest.inline_callbacks
def test_is_technical_error(patch, use_resp_code, non_technical_errors, input, output):

    @patch('taxi.config.BILLING_USE_RESP_CODE.get')
    @async.inline_callbacks
    def BILLING_USE_RESP_CODE():
        yield
        async.return_value(use_resp_code)

    @patch('taxi.config.BILLING_RESP_CODE_NON_TECHNICAL_ERRORS.get')
    @async.inline_callbacks
    def BILLING_RESP_CODE_NON_TECHNICAL_ERRORS():
        yield
        async.return_value(non_technical_errors)

    assert (yield payment_helpers.is_technical_error(input)) == output


@pytest.mark.parametrize('cost,vat,expected', [
    (100, 2, 200),
    (None, None, None),
    (0, None, 0),
])
@pytest.mark.filldb(_fill=False)
def test_apply_vat(cost, vat, expected):
    assert payment_helpers.apply_vat(cost, vat) == expected


@pytest.mark.filldb(_fill=False)
def test_apply_vat_failure():
    with pytest.raises(payment_helpers.UnknownVatError):
        payment_helpers.apply_vat(3, None)


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_get_country_vat_by_date():
    country = {'_id': 'fra', 'vat': 12000}
    vat = yield payment_helpers.get_country_vat_by_date(
        country, datetime.datetime.utcnow()
    )
    assert vat == 12000


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_get_country_vat_by_date_failure():
    country = {'_id': 'fra'}
    with pytest.raises(payment_helpers.UnknownVatError):
        yield payment_helpers.get_country_vat_by_date(
            country, datetime.datetime.utcnow()
        )
