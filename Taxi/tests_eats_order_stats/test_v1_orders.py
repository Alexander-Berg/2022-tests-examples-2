import pytest

from tests_eats_order_stats import utils_orders

HANDLE_PATH = '/internal/eats-order-stats/v1/orders'
PARAMS = {'consumer': 'test consumer'}


@pytest.fixture(autouse=True)
def _enable_next_gen_read(taxi_config):
    utils_orders.set_next_gen_settings(taxi_config, next_gen_read_enabled=True)


async def test_raw_counters(taxi_eats_order_stats):
    request = utils_orders.make_request(phone_id='000000000000000000000001')

    response = await taxi_eats_order_stats.post(
        HANDLE_PATH, json=request, params=PARAMS,
    )
    assert response.status_code == 200

    response_json = utils_orders.get_sorted_response(response.json())

    assert response_json == {
        'data': [
            {
                'counters': [
                    {
                        'first_order_at': '2021-05-27T15:32:00+0000',
                        'last_order_at': '2021-05-31T15:32:00+0000',
                        'properties': [],
                        'value': 3,
                    },
                ],
                'identity': {
                    'type': 'phone_id',
                    'value': '000000000000000000000001',
                },
            },
        ],
    }


@pytest.mark.parametrize('next_gen_read_enabled', [True, False])
@pytest.mark.parametrize(
    'group_by, expected',
    [
        (
            None,
            [
                {
                    'first_order_at': '2021-05-28T10:12:00+0000',
                    'last_order_at': '2021-05-29T11:33:00+0000',
                    'properties': [],
                    'value': 9,
                },
            ],
        ),
        (
            None,
            [
                {
                    'first_order_at': '2021-05-28T10:12:00+0000',
                    'last_order_at': '2021-05-29T11:33:00+0000',
                    'properties': [],
                    'value': 9,
                },
            ],
        ),
        (
            ['business_type'],
            [
                {
                    'first_order_at': '2021-05-28T10:12:00+0000',
                    'last_order_at': '2021-05-29T11:33:00+0000',
                    'properties': [
                        {'name': 'business_type', 'value': 'grocery'},
                    ],
                    'value': 4,
                },
                {
                    'first_order_at': '2021-05-28T10:12:00+0000',
                    'last_order_at': '2021-05-29T11:33:00+0000',
                    'properties': [
                        {'name': 'business_type', 'value': 'restaurant'},
                    ],
                    'value': 5,
                },
            ],
        ),
    ],
)
async def test_group_by(
        taxi_eats_order_stats,
        next_gen_read_enabled,
        taxi_config,
        group_by,
        expected,
):
    utils_orders.set_next_gen_settings(taxi_config, next_gen_read_enabled)
    request = utils_orders.make_request(eater_id='3456789', group_by=group_by)

    response = await taxi_eats_order_stats.post(
        HANDLE_PATH, json=request, params=PARAMS,
    )
    assert response.status_code == 200

    response_json = utils_orders.get_sorted_response(response.json())
    assert response_json == {
        'data': [
            {
                'counters': expected,
                'identity': {'type': 'eater_id', 'value': '3456789'},
            },
        ],
    }


async def test_filters(taxi_eats_order_stats):
    request = utils_orders.make_request(
        eater_id='3456789',
        filters=[{'name': 'business_type', 'values': ['restaurant']}],
    )

    response = await taxi_eats_order_stats.post(
        HANDLE_PATH, json=request, params=PARAMS,
    )
    assert response.status_code == 200

    response_json = utils_orders.get_sorted_response(response.json())
    assert response_json == {
        'data': [
            {
                'identity': {'type': 'eater_id', 'value': '3456789'},
                'counters': [
                    {
                        'properties': [],
                        'value': 5,
                        'first_order_at': '2021-05-28T10:12:00+0000',
                        'last_order_at': '2021-05-29T11:33:00+0000',
                    },
                ],
            },
        ],
    }


async def test_filters_not(taxi_eats_order_stats):
    request = utils_orders.make_request(
        eater_id='3456789',
        filters=[{'name': 'business_type', 'values': ['restaurant']}],
        filters_not=[{'name': 'brand_id', 'values': ['374748']}],
    )

    response = await taxi_eats_order_stats.post(
        HANDLE_PATH, json=request, params=PARAMS,
    )
    assert response.status_code == 200

    response_json = utils_orders.get_sorted_response(response.json())
    assert response_json == {
        'data': [
            {
                'identity': {'type': 'eater_id', 'value': '3456789'},
                'counters': [
                    {
                        'properties': [],
                        'value': 2,
                        'first_order_at': '2021-05-28T10:12:00+0000',
                        'last_order_at': '2021-05-29T11:33:00+0000',
                    },
                ],
            },
        ],
    }


@pytest.mark.parametrize(
    'filters,filters_not,expected_value',
    [
        ([], [], 3),
        (utils_orders.make_filters(payment_method=['card']), [], 1),
        ([], utils_orders.make_filters(payment_method=['card']), 2),
    ],
)
async def test_payment_method_filter(
        taxi_eats_order_stats, filters, filters_not, expected_value,
):
    response = await taxi_eats_order_stats.post(
        HANDLE_PATH,
        params=PARAMS,
        json=utils_orders.make_request(
            phone_id='000000000000000000000001',
            group_by=[],
            filters=filters,
            filters_not=filters_not,
        ),
    )
    assert response.status_code == 200
    assert response.json()['data'][0]['counters'][0]['value'] == expected_value


@pytest.mark.parametrize(
    'filters,filters_not,expected_value',
    [
        ([], [], 2),
        (utils_orders.make_filters(payment_method=['card']), [], 1),
        ([], utils_orders.make_filters(payment_method=['card']), 1),
    ],
)
async def test_fetch_device(
        taxi_eats_order_stats, filters, filters_not, expected_value,
):
    response = await taxi_eats_order_stats.post(
        HANDLE_PATH,
        params=PARAMS,
        json=utils_orders.make_request(
            device_id='device123',
            group_by=[],
            filters=filters,
            filters_not=filters_not,
        ),
    )
    assert response.status_code == 200
    assert response.json()['data'][0]['counters'][0]['value'] == expected_value


@pytest.mark.parametrize(
    'filters,filters_not,expected_value',
    [
        ([], [], 6),
        (utils_orders.make_filters(business_type=['shop']), [], 4),
        ([], utils_orders.make_filters(business_type=['shop']), 2),
    ],
)
async def test_fetch_card_id(
        taxi_eats_order_stats, filters, filters_not, expected_value,
):
    response = await taxi_eats_order_stats.post(
        HANDLE_PATH,
        params=PARAMS,
        json=utils_orders.make_request(
            card_id='card-xa1aaa11a111a111aaa11a11a',
            group_by=[],
            filters=filters,
            filters_not=filters_not,
        ),
    )
    assert response.status_code == 200
    assert response.json()['data'][0]['counters'][0]['value'] == expected_value
