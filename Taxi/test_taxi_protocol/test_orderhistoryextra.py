# pylint: disable=unused-variable

import copy
import json

import bson
import pytest

from taxi.pytest_plugins import core

from taxi_protocol.logic.orderhistoryextra import provider_getter
from taxi_protocol.logic.orderhistoryextra.providers import base
from test_taxi_protocol import plugins as conftest


class MockProvider(base.Provider):
    response: dict

    @staticmethod
    def get_key() -> str:
        return 'mock_provider'

    async def get_info(self) -> dict:
        return self.response


class MockProviderGenerator:
    response: dict

    def __init__(self, response: dict) -> None:
        self.response = response

    def __call__(self, *args, **kwargs):
        mock = MockProvider(*args, **kwargs)
        mock.response = self.response
        return mock


TEST_RESPONSE = {'test_response': [{'title1': 'value1'}, {'title2': 'value2'}]}


@pytest.mark.parametrize(
    'uid, order_id, expected_code, expected_response',
    [
        ('yandex_uid', 'order_id', 200, TEST_RESPONSE),  # in config
        ('yandex_uid', 'order_id_moscow', 200, {}),  # not in config
        ('yandex_uid', 'unknown_order_id', 404, {}),  # order not in db
        ('yandex_uid', 'order_id_processing', 400, {}),  # order not finished
        (
            'yandex_uid',
            'order_id_without_cost',  # order was cancelled
            400,
            {},
        ),
        (
            'yandex_uid',
            'order_id_another_user',  # order from another user
            400,
            {},
        ),
    ],
)
@pytest.mark.config(
    ORDERS_HISTORY_EXTRA_INFO_PROVIDER_BY_COUNTRY={'fin': ['test']},
)
async def test_orderhistoryextra(
        monkeypatch,
        protocol_client,
        protocol_app,
        mock_get_users,
        uid,
        order_id,
        expected_code,
        patch_aiohttp_session,
        expected_response,
):
    class Response(core.Response):
        @property
        def content(self):
            return self

    @patch_aiohttp_session(
        'http://archive-api.taxi.yandex.net/v1/yt/lookup_rows', 'POST',
    )
    def lookup_rows_request(*args, **kwargs):
        return Response(
            read=bson.BSON.encode({'items': []}),
            headers={'Content-Type': 'application/bson'},
        )

    monkeypatch.setattr(
        provider_getter,
        '__PROVIDERS__',
        {'test': MockProviderGenerator(TEST_RESPONSE)},
    )

    monkeypatch.setattr(
        protocol_app, 'passport', conftest.MockPassportClient(),
    )

    headers = {'X-Real-IP': '1.1.1.1', 'Authorization': 'Bearer %s' % uid}

    response = await protocol_client.post(
        '/3.0/orderhistoryextra',
        headers=headers,
        data=json.dumps({'order_id': order_id}),
    )

    assert response.status == expected_code
    assert await response.json() == expected_response


TEST_FINLAND_RESPONSE_EN = {
    'receipt_fields': [
        # available translations: en
        {'title': 'en partner name', 'value': 'IP henkilökuljetus Oy'},
        # available translations: fi
        # (no translation for partner_address)
        # available translations: ru
        # (no translation for inn)
        # available translations: en, fi
        {'title': 'en invoice number', 'value': 'order_id'},
        # available translations: en, ru
        {'title': 'en invoice date', 'value': '11.12.18 14:26'},
        # available translations: fi, ru
        # (no translation for order date)
        # available translations: en, fi, ru
        {'title': 'en description', 'value': 'en yandex taxi in fin'},
        # available translations: en
        {'title': 'en without nds', 'value': '3.64 €'},
        # available translations: en
        {'title': 'VAT 10%', 'value': '0.36 €'},
        # available translations: en
        {'title': 'en full price', 'value': '4.00 €'},
    ],
}

TEST_NORWAY_RESPONSE_EN = {
    'receipt_fields': [
        # available translations: en
        {'title': 'en partner name', 'value': 'OsloPark'},
        # available translations: fi
        # (no translation for partner_address)
        # available translations: ru
        # (no translation for inn)
        # available translations: en, fi
        {'title': 'en invoice number', 'value': 'order_id_no'},
        # available translations: en, ru
        {'title': 'en invoice date', 'value': '11.12.18 13:26'},
        # available translations: fi, ru
        # (no translation for order date)
        # available translations: en, fi, ru
        {'title': 'en description', 'value': 'en yandex taxi in fin'},
        # available translations: en
        {'title': 'en without nds', 'value': '3.77 €'},
        # available translations: en
        {'title': 'VAT 6%', 'value': '0.23 €'},
        # available translations: en
        {'title': 'en full price', 'value': '4.00 €'},
    ],
}

TEST_FINLAND_RESPONSE_FI = {
    'receipt_fields': [
        # available translations: en
        {'title': 'en partner name', 'value': 'IP henkilökuljetus Oy'},
        # available translations: fi
        {
            'title': 'fi partner address',
            'value': 'Agronominkatu 4 B 38 Helsinki',
        },
        # available translations: ru
        # (no translation for inn)
        # available translations: en, fi
        {'title': 'fi invoice number', 'value': 'order_id'},
        # available translations: en, ru
        {'title': 'en invoice date', 'value': '11.12.18 14:26'},
        # available translations: fi, ru
        {'title': 'fi order date', 'value': '11.12.18 14:26'},
        # available translations: en, fi, ru
        {'title': 'fi description', 'value': 'fi yandex taxi in fin'},
        # available translations: en
        {'title': 'en without nds', 'value': '3.64 €'},
        # available translations: en
        {'title': 'VAT 10%', 'value': '0.36 €'},
        # available translations: en
        {'title': 'en full price', 'value': '4.00 €'},
    ],
}

TEST_FINLAND_RESPONSE_RU = {
    'receipt_fields': [
        # available translations: en
        {'title': 'en partner name', 'value': 'IP henkilökuljetus Oy'},
        # available translations: fi
        # (no translation for partner address)
        # available translations: ru
        {'title': 'ru inn', 'value': 'FI123456789'},
        # available translations: en, fi
        {'title': 'en invoice number', 'value': 'order_id'},
        # available translations: en, ru
        {'title': 'ru invoice date', 'value': '11.12.18 14:26'},
        # available translations: fi, ru
        {'title': 'ru order date', 'value': '11.12.18 14:26'},
        # available translations: en, fi, ru
        {'title': 'ru description', 'value': 'ru yandex taxi in fin'},
        # available translations: en
        {'title': 'en without nds', 'value': '3.64 €'},
        # available translations: en
        {'title': 'NDS', 'value': '0.36 €'},
        # available translations: en
        {'title': 'en full price', 'value': '4.00 €'},
    ],
}


TEST_FINLAND_RESPONSE_RU_WITHOUT_DATE = {
    'receipt_fields': [
        {'title': 'en partner name', 'value': 'IP henkilökuljetus Oy'},
        {'title': 'ru inn', 'value': 'FI123456789'},
        {
            'title': 'en invoice number',
            'value': 'order_id_without_complete_time',
        },
        # complete_time not in order -> use "status_updated"
        {'title': 'ru invoice date', 'value': '11.11.15 13:11'},
        {'title': 'ru order date', 'value': '11.11.15 13:11'},
        {'title': 'ru description', 'value': 'ru yandex taxi in fin'},
        {'title': 'en without nds', 'value': '3.64 €'},
        {'title': 'NDS', 'value': '0.36 €'},
        {'title': 'en full price', 'value': '4.00 €'},
    ],
}


TEST_ROMANIA_RESPONSE_EN = {
    'receipt_fields': [
        {'title': 'en issued', 'value': 'en issued on bahalf'},
        {'title': 'en partner name', 'value': 'IPayTaxes Park'},
        {'title': 'en invoice number', 'value': 'PVTJ-0012345'},
        {'title': 'en invoice date', 'value': '11.12.18 14:26'},
        {'title': 'en description', 'value': 'en yandex taxi in fin'},
        {'title': 'en without nds', 'value': '3.39 €'},
        {'title': 'VAT 18%', 'value': '0.61 €'},
        {'title': 'en full price', 'value': '4.00 €'},
    ],
}

TEST_ROMANIA_RESPONSE_EN_AGGREGATOR = copy.deepcopy(TEST_ROMANIA_RESPONSE_EN)
TEST_ROMANIA_RESPONSE_EN_AGGREGATOR['receipt_fields'][2][
    'value'
] = 'PVTJ-0012345'

TEST_ROMANIA_RESPONSE_EN_NOVAT = {
    'receipt_fields': [
        {'title': 'en issued', 'value': 'en issued on bahalf'},
        {'title': 'en partner name', 'value': 'IHateTaxes Park'},
        {'title': 'en invoice number', 'value': 'WKHI-0012345'},
        {'title': 'en invoice date', 'value': '11.12.18 14:26'},
        {'title': 'en description', 'value': 'en yandex taxi in fin'},
        {'title': 'en full price', 'value': '4.00 €'},
    ],
}


@pytest.mark.parametrize(
    'accept_language, order_id, expected_response',
    [
        ('en', 'order_id', TEST_FINLAND_RESPONSE_EN),
        ('fi', 'order_id', TEST_FINLAND_RESPONSE_FI),
        ('ru', 'order_id', TEST_FINLAND_RESPONSE_RU),
        ('', 'order_id', TEST_FINLAND_RESPONSE_FI),  # accept-language is empty
        ('xx', 'order_id', TEST_FINLAND_RESPONSE_FI),  # unknown language
        ('uk', 'order_id', TEST_FINLAND_RESPONSE_EN),  # translation not avlbl
        (
            'ru',
            'order_id_without_complete_time',
            TEST_FINLAND_RESPONSE_RU_WITHOUT_DATE,
        ),  # date not available
        ('en', 'order_id_ro_vat', TEST_ROMANIA_RESPONSE_EN),
        ('en', 'order_id_ro_novat', TEST_ROMANIA_RESPONSE_EN_NOVAT),
        ('en', 'order_id_ro_aggregator', TEST_ROMANIA_RESPONSE_EN_AGGREGATOR),
        # norway - same as finland
        ('no', 'order_id_no', TEST_NORWAY_RESPONSE_EN),
    ],
)
@pytest.mark.config(
    ORDERS_HISTORY_EXTRA_INFO_PROVIDER_BY_COUNTRY={
        'fin': ['finland_receipt_info'],
        'rou': ['romania_receipt_info'],
        'nor': ['norway_receipt_info'],
    },
    ORDERS_HISTORY_EXTRA_VAT_BY_COUNTRY={'fin': 10, 'rou': 18, 'nor': 6},
    CURRENCY_FORMATTING_RULES={'EUR': {'__default__': 2}},
)
@pytest.mark.translations(
    tariff={
        'currency_sign.eur': {'ru': '€'},  # sign always taken from 'ru'
        'currency.eur': {'en': 'eur.'},
        'currency_with_sign.default': {'en': '$VALUE$ $SIGN$$CURRENCY$'},
    },
    client_messages={
        'orderhistoryextra.finland_receipt_info.partner_name': {
            'en': 'en partner name',
        },
        'orderhistoryextra.finland_receipt_info.partner_address': {
            'fi': 'fi partner address',
        },
        'orderhistoryextra.finland_receipt_info.vat_number': {'ru': 'ru inn'},
        'orderhistoryextra.finland_receipt_info.invoice_number': {
            'en': 'en invoice number',
            'fi': 'fi invoice number',
        },
        'orderhistoryextra.finland_receipt_info.invoice_date': {
            'en': 'en invoice date',
            'ru': 'ru invoice date',
        },
        'orderhistoryextra.finland_receipt_info.order_date': {
            'fi': 'fi order date',
            'ru': 'ru order date',
        },
        'orderhistoryextra.finland_receipt_info.description_title': {
            'en': 'en description',
            'fi': 'fi description',
            'ru': 'ru description',
        },
        'orderhistoryextra.finland_receipt_info.description_value': {
            'en': 'en yandex taxi in fin',
            'fi': 'fi yandex taxi in fin',
            'ru': 'ru yandex taxi in fin',
        },
        'orderhistoryextra.finland_receipt_info.net': {'en': 'en without nds'},
        'orderhistoryextra.finland_receipt_info.vat': {
            'en': 'VAT {0}%',
            'ru': 'NDS',
        },
        'orderhistoryextra.finland_receipt_info.full_cost': {
            'en': 'en full price',
        },
        'orderhistoryextra.romania_receipt_info.issued': {'en': 'en issued'},
        'orderhistoryextra.romania_receipt_info.issued_on_behalf': {
            'en': 'en issued on bahalf',
        },
    },
)
async def test_orderhistoryextra_finland(
        monkeypatch,
        mockserver,
        protocol_client,
        protocol_app,
        mock_get_users,
        db,
        accept_language,
        order_id,
        expected_response,
):
    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def get_order(request):
        return {'orders': [{'order': {'short_id': 12345}}]}

    monkeypatch.setattr(
        protocol_app, 'passport', conftest.MockPassportClient(),
    )

    monkeypatch.setattr(
        protocol_app,
        'territories_client',
        conftest.MockTerritoriesCllient(db),
    )

    headers = {
        'X-Real-IP': '1.1.1.1',
        'Authorization': 'Bearer yandex_uid',
        'Accept-language': accept_language,
    }

    response = await protocol_client.post(
        '/3.0/orderhistoryextra',
        headers=headers,
        data=json.dumps({'order_id': order_id}),
    )

    assert response.status == 200
    assert await response.json() == expected_response


MULTIPLE_TEST_RESPONSE_1 = {'test1': 'value1'}
MULTIPLE_TEST_RESPONSE_2 = {'test2': ['value1', 'value2', 'value3']}
MULTIPLE_TEST_RESPONSE_3 = {'test3': {'key': 'value'}, 'test4': 'value5'}

EXPECTED_MULTIPLE_RESPONSE = {
    'test1': 'value1',
    'test2': ['value1', 'value2', 'value3'],
    'test3': {'key': 'value'},
    'test4': 'value5',
}


@pytest.mark.config(
    ORDERS_HISTORY_EXTRA_INFO_PROVIDER_BY_COUNTRY={
        'fin': ['test1', 'unknown', 'test2', 'test3'],
    },
    ORDERS_HISTORY_EXTRA_VAT_BY_COUNTRY={'fin': 10},
)
async def test_multiple_providers(
        monkeypatch, protocol_client, protocol_app, mock_get_users,
):
    monkeypatch.setattr(
        provider_getter,
        '__PROVIDERS__',
        {
            'test1': MockProviderGenerator(MULTIPLE_TEST_RESPONSE_1),
            'test2': MockProviderGenerator(MULTIPLE_TEST_RESPONSE_2),
            'test3': MockProviderGenerator(MULTIPLE_TEST_RESPONSE_3),
        },
    )

    monkeypatch.setattr(
        protocol_app, 'passport', conftest.MockPassportClient(),
    )

    headers = {'X-Real-IP': '1.1.1.1', 'Authorization': 'Bearer yandex_uid'}

    response = await protocol_client.post(
        '/3.0/orderhistoryextra',
        headers=headers,
        data=json.dumps({'order_id': 'order_id'}),
    )

    assert response.status == 200
    assert await response.json() == EXPECTED_MULTIPLE_RESPONSE
