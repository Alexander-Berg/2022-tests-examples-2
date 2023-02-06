import base64

import pytest

URL = '/driver/v1/driver-money/orders/search/v3'
PAGE_LIMIT = 3
NOW = '2019-05-11T00:00:00+04'


def sort_filters(filters):
    filters.sort(key=lambda dct: dct['id'])
    for filter_ in filters:
        filter_['values'].sort(key=lambda dct: dct['filter_id'])


def load_expected_post(
        load_json,
        expected_json,
        expected_filters_json='expected_filter_groups.json',
):
    expected_filters = load_json(expected_filters_json)
    expected_response = {**load_json(expected_json), **expected_filters}
    sort_filters(expected_response['filter_groups'])
    return expected_response


@pytest.mark.config(DRIVER_MONEY_ORDERS_PAGE_LIMIT=3)
@pytest.mark.now(NOW)
@pytest.mark.pgsql('orders', files=['pg_orders.sql'])
@pytest.mark.parametrize(
    'expected_status_code,expected_json,filters_map,before',
    [
        (200, 'expected_response_day_post.json', None, None),
        (
            200,
            'expected_response_day_post_before.json',
            None,
            '2019-05-09T00:00:00',
        ),
        (400, None, {'driver_modes_but_wrong': ['orders']}, None),
        (
            200,
            'expected_response_day_post_online.json',
            {'driver_modes': ['orders'], 'payment_types': ['online']},
            None,
        ),
        (
            200,
            'expected_response_day_post_cash.json',
            {'driver_modes': ['orders'], 'payment_types': ['cash']},
            None,
        ),
        (
            200,
            'expected_response_day_post_cash_online.json',
            {'driver_modes': ['orders'], 'payment_types': ['cash', 'online']},
            None,
        ),
        (
            200,
            'expected_response_day_post_business.json',
            {'driver_modes': ['orders'], 'tariffs': ['business']},
            None,
        ),
        (
            200,
            'expected_response_day_post_econom.json',
            {'driver_modes': ['orders'], 'tariffs': ['econom']},
            None,
        ),
        (
            200,
            'expected_response_day_post_econom_business.json',
            {'driver_modes': ['orders'], 'tariffs': ['econom', 'business']},
            None,
        ),
        (
            200,
            'expected_response_day_post_online_business.json',
            {
                'driver_modes': ['orders'],
                'tariffs': ['business'],
                'payment_types': ['online'],
            },
            None,
        ),
    ],
)
async def test_filtered_orders_post(
        taxi_driver_money,
        mockserver,
        billing_reports,
        load_json,
        billing_subventions_x,
        expected_status_code,
        expected_json,
        filters_map,
        before,
):
    billing_reports.set_journal_select(
        load_json('billing_journal_select_entries.json'),
    )

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/orders')
    def _mock_payments(request):
        return load_json('billing_parks_payments_orders_response.json')

    if not filters_map:
        filters_map = {'driver_modes': ['orders']}

    filters = [
        {'filter_group': group, 'filter_id': id}
        for group, ids in filters_map.items()
        for id in ids
    ]

    data = {'filters': filters, 'period': {'type': 'day'}}
    if before:
        data['before'] = before
    response = await taxi_driver_money.post(
        URL,
        params={'tz': 'Europe/Moscow'},
        json=data,
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )

    assert response.status_code == expected_status_code

    if expected_json:
        response_data = response.json()
        sort_filters(response_data['filter_groups'])
        assert response_data == load_expected_post(load_json, expected_json)


@pytest.mark.now(NOW)
@pytest.mark.config(DRIVER_MONEY_ORDERS_PAGE_LIMIT=3)
@pytest.mark.pgsql('orders', files=['pg_orders.sql'])
@pytest.mark.parametrize(
    'expected_status_code,expected_json,cursor',
    [
        (
            200,
            'expected_response_day_get.json',
            b"""{
                "before": "2019-05-08T12:26:00+03:00",
                "id": "order4",
                "period": {
                    "type": "day"
                },
                "filters": [
                    {
                        "filter_group": "driver_modes",
                        "filter_id": "orders"
                    }
                ]
            }""",
        ),
        (
            200,
            'expected_response_day_get_business.json',
            b"""{
                "before": "2019-05-08T13:26:00+03:00",
                "id": "order5",
                "period": {
                    "type": "day"
                },
                "filters": [
                    {
                        "filter_group": "driver_modes",
                        "filter_id": "orders"
                    },
                    {
                        "filter_group": "tariffs",
                        "filter_id": "business"
                    }
                ]
            }""",
        ),
        pytest.param(
            200,
            'expected_response_day_get_with_bad_filters.json',
            b"""{
                "before": "2019-05-08T12:26:00+03:00",
                "id": "order4",
                "period": {
                    "type": "day"
                },
                "filters": [
                    {
                        "filter_group": "driver_modes",
                        "filter_id": "orders"
                    },
                    {
                        "filter_group": "wrong_group",
                        "filter_id": "wrong_id"
                    }
                ]
            }""",
            id='ignore-bad-filters',
        ),
        pytest.param(
            400,
            None,
            b"""{
                "before": "2019-05-08T12:26:00+03:00",
                "id": "order4",
                "period": {
                    "type": "day"
                },
                "filters": [
                    {
                        "filter_group": "driver_modes_but_wrong",
                        "filter_id": "orders"
                    }
                ]
            }""",
            id='fall-on-no-driver-modes-filter',
        ),
        pytest.param(
            200,
            'expected_response_day_get_end_of_pagination.json',
            b"""{
                "before": "2019-05-08T10:26:00+03:00",
                "id": "order1",
                "period": {
                    "type": "day"
                },
                "filters": [
                    {
                        "filter_group": "driver_modes",
                        "filter_id": "orders"
                    }
                ]
            }""",
            id='end-of-pagination',
        ),
    ],
)
async def test_filtered_orders_get(
        taxi_driver_money,
        mockserver,
        billing_reports,
        load_json,
        billing_subventions_x,
        expected_status_code,
        expected_json,
        cursor,
):
    billing_reports.set_journal_select(
        load_json('billing_journal_select_entries.json'),
    )

    @mockserver.json_handler('/billing-reports/v1/journal/select')
    def _mock_billing(request):
        return {
            'entries': load_json('billing_journal_select_entries.json'),
            'cursor': {},
        }

    encoded_cursor = base64.b64encode(cursor).decode()
    response = await taxi_driver_money.get(
        URL,
        params={
            'group_by': 'day',
            'tz': 'Europe/Moscow',
            'cursor': encoded_cursor,
        },
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )

    assert response.status_code == expected_status_code
    if expected_json:
        assert response.json() == load_json(expected_json)


@pytest.mark.now(NOW)
@pytest.mark.config(DRIVER_MONEY_ORDERS_PAGE_LIMIT=3)
@pytest.mark.pgsql('orders', files=['pg_orders.sql'])
async def test_filtered_orders_by_week_post(
        taxi_driver_money,
        mockserver,
        billing_reports,
        load_json,
        billing_subventions_x,
):
    billing_reports.set_journal_select(
        load_json('billing_journal_select_entries.json'),
    )

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/orders')
    def _mock_payments(request):
        return load_json('billing_parks_payments_orders_response.json')

    filters = [{'filter_group': 'driver_modes', 'filter_id': 'orders'}]
    data = {'filters': filters, 'period': {'type': 'week'}}
    response = await taxi_driver_money.post(
        URL,
        params={'tz': 'Europe/Moscow'},
        json=data,
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )

    assert response.status_code == 200
    response_data = response.json()
    sort_filters(response_data['filter_groups'])
    assert response_data == load_expected_post(
        load_json, 'expected_response_week_post.json',
    )


@pytest.mark.now(NOW)
@pytest.mark.config(DRIVER_MONEY_ORDERS_PAGE_LIMIT=3)
@pytest.mark.pgsql('orders', files=['pg_orders_by_week.sql'])
@pytest.mark.parametrize(
    'expected_status_code,expected_json,cursor',
    [
        (
            200,
            'expected_response_week_get.json',
            b"""{
                "before": "2019-05-10T16:18:00+03:00",
                "id": "order6",
                "period": {
                    "type": "week"
                },
                "filters": [
                    {
                        "filter_group": "driver_modes",
                        "filter_id": "orders"
                    }
                ]
            }""",
        ),
        pytest.param(
            200,
            'expected_response_week_get_period_start.json',
            b"""{
                "before": "2019-05-08T13:26:00+03:00",
                "id": "order5",
                "period": {
                    "type": "week"
                },
                "filters": [
                    {
                        "filter_group": "driver_modes",
                        "filter_id": "orders"
                    }
                ]
            }""",
            id='period-start',
        ),
    ],
)
async def test_filtered_orders_by_week_get(
        taxi_driver_money,
        mockserver,
        billing_reports,
        load_json,
        billing_subventions_x,
        expected_status_code,
        expected_json,
        cursor,
):
    billing_reports.set_journal_select(
        load_json('billing_journal_select_entries.json'),
    )

    @mockserver.json_handler('/billing-reports/v1/journal/select')
    def _mock_billing(request):
        return {
            'entries': load_json('billing_journal_select_entries.json'),
            'cursor': {},
        }

    encoded_cursor = base64.b64encode(cursor).decode()
    response = await taxi_driver_money.get(
        URL,
        params={'tz': 'Europe/Moscow', 'cursor': encoded_cursor},
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )

    assert response.status_code == expected_status_code
    if expected_json:
        assert response.json() == load_json(expected_json)


@pytest.mark.now(NOW)
@pytest.mark.config(DRIVER_MONEY_ORDERS_PAGE_LIMIT=3)
@pytest.mark.pgsql('orders', files=['pg_orders.sql'])
async def test_filtered_orders_by_month_post(
        taxi_driver_money,
        mockserver,
        billing_reports,
        load_json,
        billing_subventions_x,
):
    billing_reports.set_journal_select(
        load_json('billing_journal_select_entries.json'),
    )

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/orders')
    def _mock_payments(request):
        return load_json('billing_parks_payments_orders_response.json')

    filters = [{'filter_group': 'driver_modes', 'filter_id': 'orders'}]
    data = {'filters': filters, 'period': {'type': 'month'}}
    response = await taxi_driver_money.post(
        URL,
        params={'tz': 'Europe/Moscow'},
        json=data,
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )

    assert response.status_code == 200
    response_data = response.json()
    sort_filters(response_data['filter_groups'])
    assert response_data == load_expected_post(
        load_json, 'expected_response_month_post.json',
    )


@pytest.mark.now(NOW)
@pytest.mark.config(DRIVER_MONEY_ORDERS_PAGE_LIMIT=3)
@pytest.mark.pgsql('orders', files=['pg_orders_by_month.sql'])
@pytest.mark.parametrize(
    'expected_status_code,expected_json,cursor',
    [
        (
            200,
            'expected_response_month_get.json',
            b"""{
                "before": "2019-05-10T16:18:00+03:00",
                "id": "order6",
                "period": {
                    "type": "month"
                },
                "filters": [
                    {
                        "filter_group": "driver_modes",
                        "filter_id": "orders"
                    }
                ]
            }""",
        ),
        pytest.param(
            200,
            'expected_response_month_get_period_start.json',
            b"""{
                "before": "2019-05-08T13:26:00+03:00",
                "id": "order5",
                "period": {
                    "type": "month"
                },
                "filters": [
                    {
                        "filter_group": "driver_modes",
                        "filter_id": "orders"
                    }
                ]
            }""",
            id='period-start',
        ),
    ],
)
async def test_filtered_orders_by_month_get(
        taxi_driver_money,
        mockserver,
        billing_reports,
        load_json,
        billing_subventions_x,
        expected_status_code,
        expected_json,
        cursor,
):
    billing_reports.set_journal_select(
        load_json('billing_journal_select_entries.json'),
    )

    @mockserver.json_handler('/billing-reports/v1/journal/select')
    def _mock_billing(request):
        return {
            'entries': load_json('billing_journal_select_entries.json'),
            'cursor': {},
        }

    encoded_cursor = base64.b64encode(cursor).decode()
    response = await taxi_driver_money.get(
        URL,
        params={
            'group_by': 'day',
            'tz': 'Europe/Moscow',
            'cursor': encoded_cursor,
        },
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )

    assert response.status_code == expected_status_code
    if expected_json:
        assert response.json() == load_json(expected_json)


@pytest.mark.now(NOW)
@pytest.mark.config(DRIVER_MONEY_ORDERS_PAGE_LIMIT=3)
@pytest.mark.pgsql('orders', files=['pg_orders_one_page_one_day.sql'])
async def test_one_page_one_day_post(
        taxi_driver_money,
        mockserver,
        billing_reports,
        load_json,
        billing_subventions_x,
):
    billing_reports.set_journal_select(
        load_json('billing_journal_select_entries_one_page_one_day.json'),
    )

    @mockserver.json_handler('/billing-reports/v1/journal/select')
    def _mock_billing(request):
        return {
            'entries': load_json(
                'billing_journal_select_entries_one_page_one_day.json',
            ),
            'cursor': {},
        }

    response = await taxi_driver_money.post(
        URL,
        params={'tz': 'Europe/Moscow'},
        json={
            'filters': [
                {'filter_group': 'driver_modes', 'filter_id': 'orders'},
            ],
            'period': {'type': 'day'},
        },
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )

    assert response.status_code == 200
    response_data = response.json()
    sort_filters(response_data['filter_groups'])
    assert response_data == load_expected_post(
        load_json, 'expected_response_one_page_one_day_post.json',
    )


@pytest.mark.now(NOW)
@pytest.mark.config(DRIVER_MONEY_ORDERS_PAGE_LIMIT=3)
@pytest.mark.pgsql('orders', files=['pg_orders_one_page_one_day.sql'])
async def test_one_page_one_day_get(
        taxi_driver_money,
        mockserver,
        billing_reports,
        load_json,
        billing_subventions_x,
):
    billing_reports.set_journal_select(
        load_json('billing_journal_select_entries_one_page_one_day.json'),
    )

    @mockserver.json_handler('/billing-reports/v1/journal/select')
    def _mock_billing(request):
        return {
            'entries': load_json(
                'billing_journal_select_entries_one_page_one_day.json',
            ),
            'cursor': {},
        }

    encoded_cursor = base64.b64encode(
        b"""{
                "before": "2019-05-10T12:26:00+03:00",
                "id": "order4",
                "period": {
                    "type": "day"
                },
                "filters": [
                    {
                        "filter_group": "driver_modes",
                        "filter_id": "orders"
                    }
                ]
            }""",
    ).decode()

    response = await taxi_driver_money.get(
        URL,
        params={
            'group_by': 'day',
            'tz': 'Europe/Moscow',
            'cursor': encoded_cursor,
        },
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )

    assert response.status_code == 200
    assert response.json() == load_json(
        'expected_response_one_page_one_day_get.json',
    )


@pytest.mark.now('2018-05-08T23:59:59')
@pytest.mark.config(DRIVER_MONEY_ORDERS_PAGE_LIMIT=3)
@pytest.mark.pgsql('orders', files=['pg_orders.sql'])
@pytest.mark.parametrize(
    'expected_filters,period_type,before',
    [
        ({'tariffs': ['econom'], 'payment_types': ['cash']}, 'day', None),
        (
            {'tariffs': ['econom', 'business'], 'payment_types': ['cash']},
            'week',
            None,
        ),
        (
            {
                'tariffs': ['econom', 'business'],
                'payment_types': ['cash', 'online'],
            },
            'month',
            None,
        ),
        ({}, 'day', '2017-04-08T00:00:00'),
    ],
)
async def test_relevant_filters(
        taxi_driver_money,
        load_json,
        expected_filters,
        period_type,
        before,
        mockserver,
        billing_reports,
        billing_subventions_x,
):
    def create_from_filter_group(filter_group, filter_ids):
        new_filter_values = []
        for val in filter_group['values']:
            if val['filter_id'] in filter_ids:
                new_filter_values.append(val)
        return {**filter_group, 'values': new_filter_values}

    def get_expected_filter_groups(filters_to_include):
        all_filter_groups = load_json('expected_filter_groups.json')[
            'filter_groups'
        ]
        result = []
        for group in all_filter_groups:
            if group['id'] == 'driver_modes':
                result.append(group)
                continue
            filter_ids = filters_to_include.get(group['id'])
            if filter_ids:
                result.append(create_from_filter_group(group, filter_ids))
        return result

    billing_reports.set_journal_select(
        load_json('billing_journal_select_entries.json'),
    )

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/orders')
    def _mock_payments(request):
        return load_json('billing_parks_payments_orders_response.json')

    data = {
        'period': {'type': period_type},
        'filters': [{'filter_group': 'driver_modes', 'filter_id': 'orders'}],
    }
    if before:
        data['before'] = before
    response = await taxi_driver_money.post(
        URL,
        params={'tz': 'Europe/Moscow'},
        json=data,
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )

    expected_filter_groups = get_expected_filter_groups(expected_filters)

    assert response.status_code == 200

    filters = response.json()['filter_groups']
    sort_filters(filters)
    sort_filters(expected_filter_groups)
    assert filters == expected_filter_groups
