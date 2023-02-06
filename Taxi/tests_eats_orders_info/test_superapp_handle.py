import copy

import pytest

from tests_eats_orders_info import utils

REQUEST_BODY = {
    'range': {'results': 10},
    'services': ['eats'],
    'user_identity': {
        'yandex_uid': 'uid',
        'bound_yandex_uids': [],
        'eater_ids': [],
    },
    'include_service_metadata': True,
}
EXPECTED_REQUEST_BODY = {
    'range': {'results': 20},
    'services': ['eats'],
    'user_identity': {
        'yandex_uid': 'uid',
        'bound_yandex_uids': [],
        'eater_ids': [],
    },
    'include_service_metadata': True,
}


def add_sign_currency(price):
    return price.replace('.', ',') + '\u202f$SIGN$$CURRENCY$'


def prepare_for_comparing_order(order):
    del order['calculation']['final_cost']
    if 'final_cost_decimal' in order['calculation']:
        del order['calculation']['final_cost_decimal']
    if 'donation' in order['calculation']:
        del order['calculation']['donation']
    return order


def generate_orders(services, total):
    if len(services) != len(total):
        return []
    orders = []
    for [i, service] in enumerate(services):
        order = {
            'order_id': 'id{}'.format(i + 1),
            'service': service,
            'comment': 'comment{}'.format(i + 1),
            'created_at': '2017-01-01T12:00:27.87+00:00',
            'calculation': {
                'final_cost_decimal': total[i],
                'final_cost': add_sign_currency(total[i]),
                'message': 'message',
            },
        }
        orders.append(order)
    return orders


@pytest.mark.parametrize(
    ('services', 'total', 'exp_order_ids', 'amounts', 'exp_total'),
    [
        (
            ['eats', 'grocery', 'eats', 'eats', 'grocery', 'eats', 'eats'],
            ['9.8', '9.8', '9.8', '9.8', '9.8', '9.8', '10'],
            [['id1', 'id3', 'id4', 'id6', 'id7'], ['id2', 'id5']],
            {
                'id1': ['1', 'finished'],
                'id2': ['2', 'failed'],
                'id3': ['3', 'finished'],
                'id4': ['4', 'finished'],
                'id6': ['6', 'finished'],
                'id7': ['7', 'finished'],
            },
            ['10.8', '9.8', '12.8', '13.8', '9.8', '15.8', '17'],
        ),
        (
            ['eats', 'grocery', 'eats', 'eats', 'grocery', 'eats'],
            ['9.8', '9.8', '9.8', '9.8', '9.8', '9.8'],
            [['id1', 'id3', 'id4', 'id6'], ['id2', 'id5']],
            {},
            ['9.8', '9.8', '9.8', '9.8', '9.8', '9.8'],
        ),
        (
            ['eats', 'eats', 'eats', 'eats', 'eats', 'eats'],
            ['9.8', '9.8', '9.8', '9.8', '9.8', '9.8'],
            [['id1', 'id2', 'id3', 'id4', 'id5', 'id6'], []],
            {
                'id1': ['1', 'finished'],
                'id2': ['2', 'finished'],
                'id3': ['3', 'non_authorized'],
                'id4': ['4', 'finished'],
                'id5': ['5', 'finished'],
                'id6': ['6', 'finished'],
            },
            ['10.8', '11.8', '9.8', '13.8', '14.8', '15.8'],
        ),
        ([], [], [[], []], {}, []),
    ],
)
async def test_logic(
        taxi_eats_orders_info,
        services,
        total,
        exp_order_ids,
        amounts,
        exp_total,
        local_services,
):
    service_metadata = [
        {'service': 'eats', 'last_order_id': 'id1', 'name': 'Eats'},
    ]
    local_services.superapp_response = {
        'orders': generate_orders(services, total),
        'service_metadata': service_metadata,
    }
    local_services.exp_superapp_request_body = EXPECTED_REQUEST_BODY
    donations = utils.generate_donations(amounts)
    local_services.brands_response = utils.generate_brands_response(
        exp_order_ids, donations,
    )
    local_services.exp_order_ids = exp_order_ids

    response = await taxi_eats_orders_info.post(
        '/internal/eats-orders-info/v1/retrieve',
        json=REQUEST_BODY,
        headers={'Accept-Language': 'rus'},
    )

    assert response.status_code == 200
    assert 'orders' in response.json()
    assert 'service_metadata' in response.json()
    if local_services.superapp_response['orders']:
        assert response.json()['service_metadata'] == service_metadata
    response_orders = response.json()['orders']
    assert len(response_orders) == len(
        local_services.superapp_response['orders'],
    )
    for [i, order] in enumerate(local_services.superapp_response['orders']):
        cur_order = copy.deepcopy(response_orders[i])
        if (
                response_orders[i]['order_id'] in donations
                and donations[response_orders[i]['order_id']]['status']
                == 'finished'
        ):
            assert 'donation' in response_orders[i]['calculation']
            assert (
                response_orders[i]['calculation']['donation']
                == donations[response_orders[i]['order_id']]['amount_info'][
                    'amount'
                ]
                + '\u202f$SIGN$$CURRENCY$'
            )
        else:
            assert 'donation' not in response_orders[i]['calculation']
        assert 'calculation' in response_orders[i]
        assert 'final_cost' in response_orders[i]['calculation']
        assert response_orders[i]['calculation'][
            'final_cost'
        ] == add_sign_currency(exp_total[i])
        cur_order = prepare_for_comparing_order(cur_order)
        order = prepare_for_comparing_order(order)
        assert cur_order == order


@pytest.mark.parametrize('exp_code', [401, 400, 500])
async def test_superapp_orders_fail(
        taxi_eats_orders_info, exp_code, local_services,
):
    local_services.superapp_response_code = exp_code
    local_services.superapp_response = {}
    local_services.exp_superapp_request_body = EXPECTED_REQUEST_BODY

    response = await taxi_eats_orders_info.post(
        '/internal/eats-orders-info/v1/retrieve',
        json=REQUEST_BODY,
        headers={'Accept-Language': 'rus'},
    )

    assert response.status_code == exp_code


@pytest.mark.parametrize(
    ('services', 'total', 'exp_total'),
    [
        (
            ['eats', 'grocery', 'eats', 'eats', 'grocery', 'eats'],
            ['9.8', '9.8', '9.8', '9.8', '9.8', '9.8'],
            ['9.8', '9.8', '9.8', '9.8', '9.8', '9.8'],
        ),
    ],
)
async def test_persey_fail(
        taxi_eats_orders_info, services, total, exp_total, local_services,
):
    local_services.superapp_response = {
        'orders': generate_orders(services, total),
    }
    local_services.persey_response_code = 500
    local_services.exp_superapp_request_body = EXPECTED_REQUEST_BODY

    response = await taxi_eats_orders_info.post(
        '/internal/eats-orders-info/v1/retrieve',
        json=REQUEST_BODY,
        headers={'Accept-Language': 'rus'},
    )

    assert response.status_code == 200
    assert 'orders' in response.json()
    response_orders = response.json()['orders']
    assert len(response_orders) == len(
        local_services.superapp_response['orders'],
    )
    for [i, order] in enumerate(local_services.superapp_response['orders']):
        cur_order = copy.deepcopy(response_orders[i])
        assert 'donation' not in response_orders[i]['calculation']
        assert 'calculation' in response_orders[i]
        assert 'final_cost' in response_orders[i]['calculation']
        assert response_orders[i]['calculation'][
            'final_cost'
        ] == add_sign_currency(exp_total[i])
        cur_order = prepare_for_comparing_order(cur_order)
        order = prepare_for_comparing_order(order)
        assert cur_order == order
