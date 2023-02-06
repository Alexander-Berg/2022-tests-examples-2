import pytest

from tests_eats_order_stats import utils_orders

HANDLE_PATH = '/internal/eats-order-stats/v1/bulk-user-summary-orders'


@pytest.mark.parametrize(
    'next_gen_read_enabled, req_eater_id, req_phone_id, req_device_id, req_card_id, expected',
    [
        (
            False,
            '3456789',
            '000000000000000000000001',
            None,
            None,
            [
                {
                    'stats': {
                        'first_order_at': '2021-05-28T10:12:00+00:00',
                        'last_order_at': '2021-05-29T11:33:00+00:00',
                        'value': 9,
                    },
                    'identity': {'type': 'eater_id', 'value': '3456789'},
                },
                {
                    'stats': {
                        'first_order_at': '2021-05-27T15:32:00+00:00',
                        'last_order_at': '2021-05-31T15:32:00+00:00',
                        'value': 2,
                    },
                    'identity': {
                        'type': 'phone_id',
                        'value': '000000000000000000000001',
                    },
                },
            ],
        ),
        (
            True,
            '3456789',
            '000000000000000000000001',
            None,
            None,
            [
                {
                    'stats': {
                        'first_order_at': '2021-05-28T10:12:00+00:00',
                        'last_order_at': '2021-05-29T11:33:00+00:00',
                        'value': 9,
                    },
                    'identity': {'type': 'eater_id', 'value': '3456789'},
                },
                {
                    'stats': {
                        'first_order_at': '2021-05-27T15:32:00+00:00',
                        'last_order_at': '2021-05-31T15:32:00+00:00',
                        'value': 3,
                    },
                    'identity': {
                        'type': 'phone_id',
                        'value': '000000000000000000000001',
                    },
                },
            ],
        ),
        (
            True,
            None,
            None,
            'device123',
            None,
            [
                {
                    'stats': {
                        'first_order_at': '2021-05-28T10:12:00+00:00',
                        'last_order_at': '2021-05-29T11:33:00+00:00',
                        'value': 2,
                    },
                    'identity': {'type': 'device_id', 'value': 'device123'},
                },
            ],
        ),
        (
            True,
            None,
            None,
            None,
            'card-xa1aaa11a111a111aaa11a11a',
            [
                {
                    'stats': {
                        'first_order_at': '2021-05-28T10:12:00+00:00',
                        'last_order_at': '2021-05-29T11:33:00+00:00',
                        'value': 6,
                    },
                    'identity': {
                        'type': 'card_id',
                        'value': 'card-xa1aaa11a111a111aaa11a11a',
                    },
                },
            ],
        ),
    ],
)
async def test_users_has_orders(
        taxi_eats_order_stats,
        taxi_config,
        next_gen_read_enabled,
        expected,
        req_eater_id,
        req_phone_id,
        req_device_id,
        req_card_id,
):

    utils_orders.set_next_gen_settings(taxi_config, next_gen_read_enabled)

    request = utils_orders.make_request(
        eater_id=req_eater_id,
        phone_id=req_phone_id,
        device_id=req_device_id,
        card_id=req_card_id,
    )

    response = await taxi_eats_order_stats.post(HANDLE_PATH, json=request)

    assert response.status_code == 200

    assert sorted(
        response.json()['data'], key=lambda x: x['identity']['type'],
    ) == sorted(expected, key=lambda x: x['identity']['type'])


async def test_user_has_no_orders(taxi_eats_order_stats):

    request = utils_orders.make_request(eater_id='__fake_user__')

    response = await taxi_eats_order_stats.post(HANDLE_PATH, json=request)

    assert response.status_code == 200

    assert response.json() == {
        'data': [
            {
                'identity': {'type': 'eater_id', 'value': '__fake_user__'},
                'stats': {'value': 0},
            },
        ],
    }


async def test_user_empty_identities(taxi_eats_order_stats):

    response = await taxi_eats_order_stats.post(
        HANDLE_PATH, json={'identities': []},
    )

    assert response.status_code == 200

    assert response.json() == {'data': []}


async def test_wrong_identity_type(taxi_eats_order_stats):

    response = await taxi_eats_order_stats.post(
        HANDLE_PATH,
        json={
            'identities': [
                {
                    'type': 'eda_client_id',
                    'value': 'sdf45wst-ghf5syx-cfghcfye5',
                },
                {'type': 'phone_id', 'value': '000000000000000000000001'},
            ],
        },
    )

    assert response.status_code == 400
