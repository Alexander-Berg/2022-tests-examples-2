import copy
import json

import pytest


PARK_ID = 'cc111111111111111111111111111111'
DRIVER_ID = 'dd111111111111111111111111111111'
ALIAS_ID = 'aa111111111111111111111111111111'
ORDER_ID = '11111111111111111111111111111111'

PARK_ID_2 = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
DRIVER_ID_2 = 'dddddddddddddddddddddddddddddddd'

DRIVER_MONEY_ORDER_FINES_SETTINGS = {
    'fine_screen_settings': {
        'allow_show_fine_screen': True,
        'is_429_rethrow_enabled': True,
        'agreement_id': 'taxi/yandex_ride',
        'sub_account': 'commission/fine_inc_vat',
        'currency': 'RUB',
    },
}

BILLING_REQUEST = {
    'accounts': [
        {
            'agreement_id': 'taxi/yandex_ride',
            'entity_external_id': f'taximeter_driver_id/{PARK_ID}/{DRIVER_ID}',
            'sub_account': 'commission/fine_inc_vat',
            'currency': 'RUB',
        },
    ],
    'begin_time': '1970-01-01T00:00:00+00:00',
    'end_time': '2021-04-17T00:00:00+00:00',
    'tags': [f'taxi/alias_id/{ALIAS_ID}'],
    'exclude': {'zero_entries': True},
}

BILLING_RESPONSE_OK = {
    'entries': {
        f'taxi/alias_id/{ALIAS_ID}': [
            {
                'entry_id': 1473120034,
                'account': {
                    'account_id': 47110034,
                    'entity_external_id': (
                        f'taximeter_driver_id/{PARK_ID}/{DRIVER_ID}'
                    ),
                    'agreement_id': 'taxi/yandex_ride',
                    'currency': 'RUB',
                    'sub_account': 'commission/fine_inc_vat',
                },
                'amount': '-354.0000',
                'doc_ref': '6611460226',
                'event_at': '2021-03-31T15:15:20.270075+00:00',
                'created': '2021-03-31T15:15:24.316767+00:00',
                'details': {
                    'alias_id': f'{ALIAS_ID}',
                    'fine_code': 'cancel_after_confirm',
                },
                'reason': '',
                'idempotency_key': '47110034',
            },
        ],
    },
}

BILLING_RESPONSE_EMPTY: dict = {'entries': {f'taxi/alias_id/{ALIAS_ID}': []}}

BILLING_RESPONSE_ZERO_SUM = {
    'entries': {
        f'taxi/alias_id/{ALIAS_ID}': [
            {
                'entry_id': 1473120034,
                'account': {
                    'account_id': 47110034,
                    'entity_external_id': (
                        f'taximeter_driver_id/{PARK_ID}/{DRIVER_ID}'
                    ),
                    'agreement_id': 'taxi/yandex_ride',
                    'currency': 'RUB',
                    'sub_account': 'commission/fine_inc_vat',
                },
                'amount': '-354.0000',
                'doc_ref': '6611460226',
                'event_at': '2021-03-31T15:15:20.270075+00:00',
                'created': '2021-03-31T15:15:24.316767+00:00',
                'details': {
                    'alias_id': f'{ALIAS_ID}',
                    'fine_code': 'cancel_after_confirm',
                },
                'reason': '',
                'idempotency_key': '47110034',
            },
            {
                'entry_id': 1473120035,
                'account': {
                    'account_id': 47110034,
                    'entity_external_id': (
                        f'taximeter_driver_id/{PARK_ID}/{DRIVER_ID}'
                    ),
                    'agreement_id': 'taxi/yandex_ride',
                    'currency': 'RUB',
                    'sub_account': 'commission/fine_inc_vat',
                },
                'amount': '354.0000',
                'doc_ref': '6611460226',
                'event_at': '2021-03-31T15:15:30.270075+00:00',
                'created': '2021-03-31T15:15:24.316767+00:00',
                'details': {
                    'alias_id': f'{ALIAS_ID}',
                    'fine_code': 'cancel_after_confirm',
                },
                'reason': '',
                'idempotency_key': '47110034',
            },
        ],
    },
}

BILLING_RESPONSE_ANOTHER_ALIAS = {
    'entries': {
        'taxi/alias_id/order_id_1': [
            {
                'entry_id': 1473120034,
                'account': {
                    'account_id': 47110034,
                    'entity_external_id': (
                        f'taximeter_driver_id/{PARK_ID}/{DRIVER_ID}'
                    ),
                    'agreement_id': 'taxi/yandex_ride',
                    'currency': 'RUB',
                    'sub_account': 'commission/fine_inc_vat',
                },
                'amount': '-354.0000',
                'doc_ref': '6611460226',
                'event_at': '2021-03-31T15:15:20.270075+00:00',
                'created': '2021-03-31T15:15:24.316767+00:00',
                'details': {
                    'alias_id': f'{ALIAS_ID}',
                    'fine_code': 'cancel_after_confirm',
                },
                'reason': '',
                'idempotency_key': '47110034',
            },
        ],
    },
}

ORDER_FINE_REQUEST_HEADERS = {
    'User-Agent': 'Taximeter 8.90 (228)',
    'Accept-Language': 'en',
    'X-Request-Application-Version': '8.90',
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
}

ORDER_FINE_REQUEST_PARAMS = {'tz': 'Europe/Moscow'}

ORDER_FINE_REQUEST_BODY = {'fine_identity': {'order_id': ALIAS_ID}}

EXPECTED_ORDER_FINE_RESPONSE_MOCK = {
    'title': 'Штраф',
    'subtitle': '14 марта, 14:10',
    'ui': {
        'items': [
            {
                'type': 'header',
                'id': '1',
                'horizontal_divider_type': 'none',
                'subtitle': '-100 ₽',
                'gravity': 'center',
            },
            {'title': 'Причина', 'type': 'title'},
            {
                'type': 'detail',
                'horizontal_divider_type': 'none',
                'title': 'Заказ был отменен после принятия',
            },
            {'title': 'Заказ', 'type': 'title'},
            {
                'type': 'tip_detail',
                'accent': False,
                'horizontal_divider_type': 'bottom_gap',
                'title': '14:10',
                'subtitle': 'Садовническая, 85 c2',
                'accent_title': False,
            },
        ],
    },
}

EXPECTED_ORDER_FINE_RESPONSE = {
    'title': 'Штраф',
    'subtitle': '31 марта, 18:15',
    'ui': {
        'items': [
            {
                'type': 'header',
                'id': '1',
                'horizontal_divider_type': 'none',
                'subtitle': '-354,00 ₽',
                'gravity': 'center',
            },
            {'title': 'Reason', 'type': 'title'},
            {
                'type': 'detail',
                'horizontal_divider_type': 'none',
                'title': 'Причина штрафа прорабатывается',
            },
            {'title': 'Заказ', 'type': 'title'},
            {
                'type': 'tip_detail',
                'accent': False,
                'horizontal_divider_type': 'bottom_gap',
                'title': '13 февраля, 12:00',
                'subtitle': 'Западная улица, 12Д',
                'accent_title': False,
            },
        ],
    },
}

TRANSLATIONS = {
    'taximeter_backend_api_controllers': {
        'DriverMoney_Order_DateWithTime': {
            'ru': '%(day)s %(month_part)s, %(time)s',
        },
    },
    'taximeter_backend_driver_messages': {
        'OrderFines_FineScreen_ScreenTitle': {'ru': 'Штраф'},
        'OrderFines_FineScreen_ReasonTitle': {'ru': 'Причина', 'en': 'Reason'},
        'OrderFines_FineScreen_OrderTitle': {'en': 'Заказ'},
        'OrderFines_FineScreen_ReasonByCode.fine_for_nothing': {
            'ru': 'Причина штрафа прорабатывается',
        },
    },
}


@pytest.mark.config(
    DRIVER_MONEY_ORDER_FINES_SETTINGS=DRIVER_MONEY_ORDER_FINES_SETTINGS,
)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.now('2021-04-16T23:00:00+00:00')
async def test_order_fine__happy_path(
        mockserver, taxi_order_fines, order_proc, save_decision,
):
    await save_decision(
        {'has_fine': True, 'fine_code': 'fine_for_nothing'}, ORDER_ID,
    )

    @mockserver.json_handler('/billing-reports/v2/journal/by_tag')
    async def _journal_by_tag(request):
        assert request.json == BILLING_REQUEST
        return BILLING_RESPONSE_OK

    response = await taxi_order_fines.post(
        '/driver/v1/order-fines/order/fine',
        headers=ORDER_FINE_REQUEST_HEADERS,
        params=ORDER_FINE_REQUEST_PARAMS,
        json=ORDER_FINE_REQUEST_BODY,
    )
    assert response.status_code == 200
    assert response.json() == EXPECTED_ORDER_FINE_RESPONSE


@pytest.mark.parametrize(
    'headers, body, expected_code',
    [
        (ORDER_FINE_REQUEST_HEADERS, ORDER_FINE_REQUEST_BODY, 200),
        (ORDER_FINE_REQUEST_HEADERS, {'fine_identity': {'order_id': ''}}, 400),
        (
            ORDER_FINE_REQUEST_HEADERS,
            {'fine_identity': {'order_id': ALIAS_ID}},
            200,
        ),
        (
            {
                'User-Agent': 'Taximeter 8.90 (228)',
                'Accept-Language': 'ru',
                'X-Request-Application-Version': '8.90',
                'X-YaTaxi-Park-Id': '',
                'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
            },
            ORDER_FINE_REQUEST_BODY,
            400,
        ),
        (
            {
                'User-Agent': 'Taximeter 8.90 (228)',
                'Accept-Language': 'ru',
                'X-Request-Application-Version': '8.90',
                'X-YaTaxi-Park-Id': PARK_ID,
                'X-YaTaxi-Driver-Profile-Id': '',
            },
            ORDER_FINE_REQUEST_BODY,
            401,
        ),
    ],
)
@pytest.mark.config(
    DRIVER_MONEY_ORDER_FINES_SETTINGS=DRIVER_MONEY_ORDER_FINES_SETTINGS,
)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.now('2021-04-16T23:00:00+00:00')
async def test_order_fine__bad_request(
        mockserver,
        taxi_order_fines,
        order_proc,
        save_decision,
        headers,
        body,
        expected_code,
):
    await save_decision(
        {'has_fine': True, 'fine_code': 'fine_for_nothing'}, ORDER_ID,
    )

    @mockserver.json_handler('/billing-reports/v2/journal/by_tag')
    async def _journal_by_tag(request):
        assert request.json == BILLING_REQUEST
        return BILLING_RESPONSE_OK

    response = await taxi_order_fines.post(
        '/driver/v1/order-fines/order/fine',
        headers=headers,
        params=ORDER_FINE_REQUEST_PARAMS,
        json=body,
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'order_fines_request_headers, billing_response, expected_code',
    [
        (ORDER_FINE_REQUEST_HEADERS, BILLING_RESPONSE_OK, 200),
        (
            {
                'User-Agent': 'Taximeter 8.90 (228)',
                'Accept-Language': 'en',
                'X-Request-Application-Version': '8.90',
                'X-YaTaxi-Park-Id': PARK_ID_2,
                'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
            },
            {
                'entries': {
                    f'taxi/alias_id/{ALIAS_ID}': [
                        {
                            'entry_id': 1473120034,
                            'account': {
                                'account_id': 47110034,
                                'entity_external_id': (
                                    'taximeter_driver_id/'
                                    f'{PARK_ID_2}/{DRIVER_ID}'
                                ),
                                'agreement_id': 'taxi/yandex_ride',
                                'currency': 'RUB',
                                'sub_account': 'commission/fine_inc_vat',
                            },
                            'amount': '-354.0000',
                            'doc_ref': '6611460226',
                            'event_at': '2021-03-31T15:15:20.270075+00:00',
                            'created': '2021-03-31T15:15:24.316767+00:00',
                            'details': {
                                'alias_id': f'{ALIAS_ID}',
                                'fine_code': 'cancel_after_confirm',
                            },
                            'reason': '',
                            'idempotency_key': '47110034',
                        },
                    ],
                },
            },
            404,
        ),
        (
            {
                'User-Agent': 'Taximeter 8.90 (228)',
                'Accept-Language': 'en',
                'X-Request-Application-Version': '8.90',
                'X-YaTaxi-Park-Id': PARK_ID,
                'X-YaTaxi-Driver-Profile-Id': DRIVER_ID_2,
            },
            {
                'entries': {
                    f'taxi/alias_id/{ALIAS_ID}': [
                        {
                            'entry_id': 1473120034,
                            'account': {
                                'account_id': 47110034,
                                'entity_external_id': (
                                    'taximeter_driver_id'
                                    f'/{PARK_ID}/{DRIVER_ID_2}'
                                ),
                                'agreement_id': 'taxi/yandex_ride',
                                'currency': 'RUB',
                                'sub_account': 'commission/fine_inc_vat',
                            },
                            'amount': '-354.0000',
                            'doc_ref': '6611460226',
                            'event_at': '2021-03-31T15:15:20.270075+00:00',
                            'created': '2021-03-31T15:15:24.316767+00:00',
                            'details': {
                                'alias_id': f'{ALIAS_ID}',
                                'fine_code': 'cancel_after_confirm',
                            },
                            'reason': '',
                            'idempotency_key': '47110034',
                        },
                    ],
                },
            },
            404,
        ),
    ],
)
@pytest.mark.config(
    DRIVER_MONEY_ORDER_FINES_SETTINGS=DRIVER_MONEY_ORDER_FINES_SETTINGS,
)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.now('2021-04-16T23:00:00+00:00')
async def test_order_fine__order_contractor_mismatch(
        mockserver,
        taxi_order_fines,
        order_proc,
        save_decision,
        order_fines_request_headers,
        billing_response,
        expected_code,
):
    await save_decision(
        {'has_fine': True, 'fine_code': 'fine_for_nothing'}, ORDER_ID,
    )

    @mockserver.json_handler('/billing-reports/v2/journal/by_tag')
    async def _journal_by_tag(request):
        return billing_response

    response = await taxi_order_fines.post(
        '/driver/v1/order-fines/order/fine',
        headers=order_fines_request_headers,
        params=ORDER_FINE_REQUEST_PARAMS,
        json=ORDER_FINE_REQUEST_BODY,
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'billing_report_response, expected_code',
    [
        (
            {
                'status': 200,
                'content_type': 'application/json',
                'response': json.dumps(BILLING_RESPONSE_OK),
            },
            200,
        ),
        ({'status': 500}, 500),
    ],
)
@pytest.mark.config(
    DRIVER_MONEY_ORDER_FINES_SETTINGS=DRIVER_MONEY_ORDER_FINES_SETTINGS,
)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.now('2021-04-16T23:00:00+00:00')
async def test_order_fine__billing_report_errors(
        mockserver,
        taxi_order_fines,
        order_proc,
        save_decision,
        billing_report_response,
        expected_code,
):
    await save_decision(
        {'has_fine': True, 'fine_code': 'fine_for_nothing'}, ORDER_ID,
    )

    @mockserver.handler('/billing-reports/v2/journal/by_tag')
    async def _journal_by_tag(request):
        assert request.json == BILLING_REQUEST
        return mockserver.make_response(**billing_report_response)

    response = await taxi_order_fines.post(
        '/driver/v1/order-fines/order/fine',
        headers=ORDER_FINE_REQUEST_HEADERS,
        params=ORDER_FINE_REQUEST_PARAMS,
        json=ORDER_FINE_REQUEST_BODY,
    )
    assert response.status_code == expected_code
    if response.status_code == 200:
        assert response.json() == EXPECTED_ORDER_FINE_RESPONSE


@pytest.mark.parametrize(
    'is_429_rethrow_enabled, throw_429, expected_code',
    [(False, False, 200), (False, True, 404), (True, True, 429)],
)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.now('2021-04-16T23:00:00+00:00')
async def test_order_fine__billing_report_too_many_requests(
        mockserver,
        taxi_config,
        taxi_order_fines,
        order_proc,
        is_429_rethrow_enabled,
        throw_429,
        expected_code,
        save_decision,
):
    await save_decision(
        {'has_fine': True, 'fine_code': 'fine_for_nothing'}, ORDER_ID,
    )

    order_fine_settings = {
        'fine_screen_settings': {
            'allow_show_fine_screen': True,
            'is_429_rethrow_enabled': is_429_rethrow_enabled,
            'agreement_id': 'taxi/yandex_ride',
            'sub_account': 'commission/fine_inc_vat',
            'currency': 'RUB',
        },
    }
    taxi_config.set_values(
        dict(DRIVER_MONEY_ORDER_FINES_SETTINGS=order_fine_settings),
    )

    await taxi_order_fines.invalidate_caches()

    @mockserver.json_handler('/billing-reports/v2/journal/by_tag')
    async def _journal_by_tag(request):
        if throw_429:
            return mockserver.make_response(status=429)
        return BILLING_RESPONSE_OK

    response = await taxi_order_fines.post(
        '/driver/v1/order-fines/order/fine',
        headers=ORDER_FINE_REQUEST_HEADERS,
        params=ORDER_FINE_REQUEST_PARAMS,
        json=ORDER_FINE_REQUEST_BODY,
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'order_fine_request_body, billing_response, expected_code',
    [
        (ORDER_FINE_REQUEST_BODY, BILLING_RESPONSE_OK, 200),
        (
            {'fine_identity': {'order_id': 'no_such_alias'}},
            {
                'entries': {
                    'taxi/alias_id/no_such_alias': [
                        {
                            'entry_id': 1473120034,
                            'account': {
                                'account_id': 47110034,
                                'entity_external_id': (
                                    'taximeter_driver_id/'
                                    f'{PARK_ID}/{DRIVER_ID}'
                                ),
                                'agreement_id': 'taxi/yandex_ride',
                                'currency': 'RUB',
                                'sub_account': 'commission/fine_inc_vat',
                            },
                            'amount': '-354.0000',
                            'doc_ref': '6611460226',
                            'event_at': '2021-03-31T15:15:20.270075+00:00',
                            'created': '2021-03-31T15:15:24.316767+00:00',
                            'details': {
                                'alias_id': 'no_such_alias',
                                'fine_code': 'cancel_after_confirm',
                            },
                            'reason': '',
                            'idempotency_key': '47110034',
                        },
                    ],
                },
            },
            404,
        ),
    ],
)
@pytest.mark.config(
    DRIVER_MONEY_ORDER_FINES_SETTINGS=DRIVER_MONEY_ORDER_FINES_SETTINGS,
)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.now('2021-04-16T23:00:00+00:00')
async def test_order_fine__no_order_in_billing_by_alias(
        mockserver,
        taxi_order_fines,
        order_proc,
        save_decision,
        order_fine_request_body,
        billing_response,
        expected_code,
):
    await save_decision(
        {'has_fine': True, 'fine_code': 'fine_for_nothing'}, ORDER_ID,
    )

    @mockserver.json_handler('/billing-reports/v2/journal/by_tag')
    async def _journal_by_tag(request):
        return billing_response

    response = await taxi_order_fines.post(
        '/driver/v1/order-fines/order/fine',
        headers=ORDER_FINE_REQUEST_HEADERS,
        params=ORDER_FINE_REQUEST_PARAMS,
        json=order_fine_request_body,
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'has_fine_code, billing_response, expected_code',
    [
        (True, BILLING_RESPONSE_OK, 200),
        (False, BILLING_RESPONSE_OK, 404),
        (True, BILLING_RESPONSE_EMPTY, 404),
        (False, BILLING_RESPONSE_EMPTY, 404),
        (True, BILLING_RESPONSE_ZERO_SUM, 404),
        (False, BILLING_RESPONSE_ZERO_SUM, 404),
        (True, BILLING_RESPONSE_ANOTHER_ALIAS, 404),
        (False, BILLING_RESPONSE_ANOTHER_ALIAS, 404),
    ],
)
@pytest.mark.config(
    DRIVER_MONEY_ORDER_FINES_SETTINGS={
        'fine_screen_settings': {
            'allow_show_fine_screen': True,
            'is_429_rethrow_enabled': True,
            'agreement_id': 'taxi/yandex_ride',
            'sub_account': 'commission/fine_inc_vat',
            'currency': 'RUB',
        },
    },
)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.now('2021-04-16T23:00:00+00:00')
async def test_order_fine__no_fine_code_or_no_fine_value(
        mockserver,
        taxi_order_fines,
        order_proc,
        has_fine_code,
        billing_response,
        expected_code,
        save_decision,
):
    if has_fine_code:
        await save_decision(
            {'has_fine': True, 'fine_code': 'fine_for_nothing'}, ORDER_ID,
        )

    @mockserver.json_handler('/billing-reports/v2/journal/by_tag')
    async def _journal_by_tag(request):
        assert request.json == BILLING_REQUEST
        return billing_response

    response = await taxi_order_fines.post(
        '/driver/v1/order-fines/order/fine',
        headers=ORDER_FINE_REQUEST_HEADERS,
        params=ORDER_FINE_REQUEST_PARAMS,
        json=ORDER_FINE_REQUEST_BODY,
    )
    assert response.status_code == expected_code


def _get_translations_without_key(key):
    result = copy.deepcopy(TRANSLATIONS)
    assert result['taximeter_backend_driver_messages'].pop(key)
    return result


@pytest.mark.config(
    DRIVER_MONEY_ORDER_FINES_SETTINGS=DRIVER_MONEY_ORDER_FINES_SETTINGS,
)
@pytest.mark.translations(
    taximeter_backend_driver_messages=_get_translations_without_key(
        'OrderFines_FineScreen_ReasonByCode.fine_for_nothing',
    ),
)
@pytest.mark.now('2021-04-16T23:00:00+00:00')
async def test_order_fine__localizations_cases__no_fine_code_reason(
        mockserver, taxi_order_fines, order_proc, save_decision,
):
    await save_decision(
        {'has_fine': True, 'fine_code': 'fine_for_nothing'}, ORDER_ID,
    )

    @mockserver.json_handler('/billing-reports/v2/journal/by_tag')
    async def _journal_by_tag(request):
        assert request.json == BILLING_REQUEST
        return BILLING_RESPONSE_OK

    response = await taxi_order_fines.post(
        '/driver/v1/order-fines/order/fine',
        headers=ORDER_FINE_REQUEST_HEADERS,
        params=ORDER_FINE_REQUEST_PARAMS,
        json=ORDER_FINE_REQUEST_BODY,
    )
    assert response.status_code == 404


@pytest.mark.config(
    DRIVER_MONEY_ORDER_FINES_SETTINGS=DRIVER_MONEY_ORDER_FINES_SETTINGS,
)
@pytest.mark.translations(
    taximeter_backend_driver_messages=_get_translations_without_key(
        'OrderFines_FineScreen_ReasonTitle',
    ),
)
@pytest.mark.now('2021-04-16T23:00:00+00:00')
async def test_order_fine__localizations_cases__no_some_label(
        mockserver, taxi_order_fines, order_proc, save_decision,
):
    await save_decision(
        {'has_fine': True, 'fine_code': 'fine_for_nothing'}, ORDER_ID,
    )

    @mockserver.json_handler('/billing-reports/v2/journal/by_tag')
    async def _journal_by_tag(request):
        assert request.json == BILLING_REQUEST
        return BILLING_RESPONSE_OK

    response = await taxi_order_fines.post(
        '/driver/v1/order-fines/order/fine',
        headers=ORDER_FINE_REQUEST_HEADERS,
        params=ORDER_FINE_REQUEST_PARAMS,
        json=ORDER_FINE_REQUEST_BODY,
    )
    assert response.status_code == 404
