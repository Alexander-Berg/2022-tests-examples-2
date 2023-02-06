import logging

import pytest

from tests_eats_order_stats import utils_orders


def check_takeout(pgsql, takeout, identity_value):
    cursor = pgsql['eats_order_stats'].cursor()
    cursor.execute(
        'SELECT takeout FROM eats_order_stats_v2.orders_counters '
        f'WHERE identity_value=\'{identity_value}\';',
    )
    logging.info('identity: %s', identity_value)
    assert cursor.fetchone()[0] == takeout


@pytest.mark.config(
    EATS_ORDER_STATS_NEXT_GEN_SETTINGS={
        'next_gen_read_enabled': True,
        'next_gen_write_enabled': True,
    },
)
@pytest.mark.parametrize(
    'request_json, eater_ids',
    [
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [{'uid': 'ya1', 'is_portal': True}],
            },
            ['1'],
            id='one uid',
        ),
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [
                    {'uid': 'ya1', 'is_portal': True},
                    {'uid': 'ya2', 'is_portal': True},
                ],
                'personal_phone_ids': [
                    '000000000000000000000001',
                    '000000000000000000000002',
                ],
            },
            ['1', '2'],
            id='multiple uids',
        ),
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [{'uid': 'ya5', 'is_portal': True}],
            },
            ['5'],
            id='one uid, has takeouted counter',
        ),
    ],
)
async def test_takeout_delete(
        mockserver, taxi_eats_order_stats, pgsql, request_json, eater_ids,
):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uids')
    def _mock_eaters(request):
        assert 'passport_uids' in request.json
        return {
            'eaters': [
                {
                    'personal_phone_id': 'phone_id',
                    'id': eater_id,
                    'uuid': uid,
                    'created_at': '2021-06-01T00:00:00+00:00',
                    'updated_at': '2021-06-01T00:00:00+00:00',
                }
                for eater_id, uid in zip(
                    eater_ids, request.json['passport_uids'],
                )
            ],
            'pagination': {'limit': 1000, 'has_more': False},
        }

    response = await taxi_eats_order_stats.post(
        f'/takeout/v1/delete', json=request_json,
    )
    assert response.status_code == 200

    for eater_id in eater_ids:
        check_takeout(pgsql, True, eater_id)

    if 'personal_phone_ids' in request_json:
        for phone_id in request_json['personal_phone_ids']:
            check_takeout(pgsql, True, phone_id)


@pytest.mark.config(
    EATS_ORDER_STATS_NEXT_GEN_SETTINGS={
        'next_gen_read_enabled': True,
        'next_gen_write_enabled': True,
    },
)
@pytest.mark.parametrize(
    'request_json, response_json, eater_ids',
    [
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [{'uid': 'ya1', 'is_portal': True}],
            },
            {'data_state': 'ready_to_delete'},
            ['1'],
            id='one uid',
        ),
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [
                    {'uid': 'ya1', 'is_portal': True},
                    {'uid': 'ya2', 'is_portal': True},
                ],
            },
            {'data_state': 'ready_to_delete'},
            ['1', '2'],
            id='multiple uids',
        ),
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [
                    {'uid': 'without_orders_1', 'is_portal': True},
                ],
            },
            {'data_state': 'empty'},
            ['6'],
            id='missing uid',
        ),
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [
                    {'uid': 'ya1', 'is_portal': True},
                    {'uid': 'without_orders_2', 'is_portal': True},
                ],
            },
            {'data_state': 'ready_to_delete'},
            ['1', '3'],
            id='multiple uids mixed',
        ),
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [
                    {'uid': 'without_orders_1', 'is_portal': True},
                ],
                'personal_phone_ids': [
                    '000000000000000000000001',
                    '000000000000000000000002',
                ],
            },
            {'data_state': 'ready_to_delete'},
            ['6'],
            id='uid without orders, but phones with orders',
        ),
        pytest.param(
            {
                'request_id': 'request_id',
                'yandex_uids': [
                    {'uid': 'without_orders_1', 'is_portal': True},
                ],
                'personal_phone_ids': [
                    '00000000000000000000000a',
                    '00000000000000000000000b',
                ],
            },
            {'data_state': 'empty'},
            ['6'],
            id='uid and phones with orders',
        ),
    ],
)
async def test_takeout_status(
        mockserver,
        taxi_eats_order_stats,
        request_json,
        response_json,
        eater_ids,
):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uids')
    def _mock_eaters(request):
        assert 'passport_uids' in request.json
        return {
            'eaters': [
                {
                    'personal_phone_id': 'phone_id',
                    'id': eater_id,
                    'uuid': uid,
                    'created_at': '2021-06-01T00:00:00+00:00',
                    'updated_at': '2021-06-01T00:00:00+00:00',
                }
                for eater_id, uid in zip(
                    eater_ids, request.json['passport_uids'],
                )
            ],
            'pagination': {'limit': 1000, 'has_more': False},
        }

    response = await taxi_eats_order_stats.post(
        f'/takeout/v1/status', json=request_json,
    )
    assert response.status_code == 200
    assert response.json() == response_json


EATS_CATALOG_STORAGE_CACHE_SETTINGS = [
    {
        'id': 45678,
        'revision_id': 5,
        'updated_at': '2020-11-26T10:00:00.000000Z',
        'brand': {
            'id': 56789,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
    },
    {
        'id': 234,
        'revision_id': 5,
        'updated_at': '2020-11-26T10:00:00.000000Z',
        'brand': {
            'id': 432,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'store',
    },
    {
        'id': 1000,
        'revision_id': 5,
        'updated_at': '2020-11-26T10:00:00.000000Z',
        'brand': {
            'id': 1000,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
    },
]


def check_counter(counter, pgsql):
    cursor = pgsql['eats_order_stats'].cursor()
    cursor.execute(
        'SELECT counter_value FROM eats_order_stats_v2.orders_counters '
        f'WHERE identity_type=\'{counter.get("identity_type")}\' '
        f'AND identity_value=\'{counter.get("identity")}\' '
        f'AND takeout = FALSE;',
    )
    assert cursor.fetchone()[0] == counter['value']


@pytest.mark.config(
    EATS_ORDER_STATS_NEXT_GEN_SETTINGS={
        'next_gen_read_enabled': True,
        'next_gen_write_enabled': True,
    },
)
@pytest.mark.parametrize(
    'order,db_data',
    [
        # increment
        (
            {
                'eater_id': '6',
                'phone_id': '6',
                'order_nr': '202106-24343',
                'place_id': '234',
                'delivery_type': 'our_delivery',
                'created_at': '2020-11-26T00:00:00.000000Z',
                'payment_method': 'applepay',
            },
            {
                'counters': [
                    {'identity': '6', 'identity_type': 'eater_id', 'value': 1},
                ],
                'processed_orders': [
                    {
                        'order_id': '202106-24343',
                        'identity_type': 'eater_id',
                        'canceled': False,
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.eats_catalog_storage_cache(EATS_CATALOG_STORAGE_CACHE_SETTINGS)
async def test_save_order_counters(stq_runner, pgsql, order, db_data):
    await stq_runner.eats_order_stats_save_order.call(
        task_id='new_counter', kwargs=order,
    )
    for counter in db_data['counters']:
        check_counter(counter, pgsql)


# Generated via `tvmknife unittest service --dst 2345 --src 2345`
MOCK_TMV_TICKET = (
    '3:serv:CBAQ__________9_IgYIqRIQqRI:Hd6zeER-9-'
    'BgGANCsKKkmXLIl3HH92nUUxa6-f8MeUnMXJYMibPxRL6'
    'k0zQHQiGtIhbCFcHZRI5qIW-ZGedzZpDlCvoRrazAmYGr'
    'smP1fPAlrJ14nn5nqOfOSxz6bynl3HimE9o-dgMAxBX0b'
    'otdEjIwoIgF4mw_OZBLEWHUSoQ'
)


@pytest.mark.config(
    EATS_ORDER_STATS_NEXT_GEN_SETTINGS={
        'next_gen_read_enabled': True,
        'next_gen_write_enabled': True,
    },
)
@pytest.mark.config(TVM_SERVICES={'with_takeout': 2345}, TVM_ENABLED=True)
@pytest.mark.parametrize(
    'expected_value, params',
    [
        pytest.param(
            2,
            {'consumer': 'test consumer', 'for_antifraud': True},
            marks=[
                pytest.mark.config(
                    EATS_ORDER_STATS_TVM_TAKEOUT_ACCESS=['with_takeout'],
                ),
            ],
            id='with takeout, antifraud',
        ),
        pytest.param(
            2,
            {'consumer': 'test consumer'},
            marks=[
                pytest.mark.config(
                    EATS_ORDER_STATS_TVM_TAKEOUT_ACCESS=['with_takeout'],
                ),
            ],
            id='with takeout, without antifraud flag',
        ),
        pytest.param(
            1,
            {'consumer': 'test consumer', 'for_antifraud': False},
            marks=[
                pytest.mark.config(
                    EATS_ORDER_STATS_TVM_TAKEOUT_ACCESS=['with_takeout'],
                ),
            ],
            id='with takeout, not antifraud',
        ),
        pytest.param(1, {'consumer': 'test consumer'}, id='without takeout'),
    ],
)
async def test_raw_counters(taxi_eats_order_stats, expected_value, params):
    request = utils_orders.make_request(eater_id='5')

    response = await taxi_eats_order_stats.post(
        '/internal/eats-order-stats/v1/orders',
        json=request,
        headers={'X-Ya-Service-Ticket': MOCK_TMV_TICKET},
        params=params,
    )
    assert response.status_code == 200

    response_json = utils_orders.get_sorted_response(response.json())

    assert response_json['data'][0]['counters'][0]['value'] == expected_value
