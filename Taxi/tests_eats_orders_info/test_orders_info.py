import copy
import math

import pytest

from tests_eats_orders_info import utils

EATER_ID = '3456723'
LIMIT = 100
OFFSET = 0

FALLBACK_FOR_FEEDBACKS_CONFIG = {
    'enabled': True,
    'default_feedback_status': 'wait',
    'default_has_feedback': False,
}
FALLBACK_FEEDBACKS = [
    {'order_nr': 'id1', 'status': 'wait', 'has_feedback': False},
    {'order_nr': 'id1', 'status': 'wait', 'has_feedback': False},
    {'order_nr': 'id2', 'status': 'wait', 'has_feedback': False},
    {'order_nr': 'id3', 'status': 'wait', 'has_feedback': False},
    {'order_nr': 'id4', 'status': 'wait', 'has_feedback': False},
    {'order_nr': 'id5', 'status': 'wait', 'has_feedback': False},
    {'order_nr': 'id6', 'status': 'wait', 'has_feedback': False},
]


def prepare_for_comparing_order(order_incoming):
    order = copy.deepcopy(order_incoming)
    del order['cart']['total_rational']
    del order['cart']['total']
    if 'feedback_status' in order:
        del order['feedback_status']
    if 'has_feedback' in order:
        del order['has_feedback']
    if 'donation' in order:
        del order['donation']
    return order


def generate_orders(services, total, grocery_orders=None):
    if len(services) != len(total):
        return []
    orders = []
    for [i, service] in enumerate(services):
        order = {
            'id': 'id{}'.format(i + 1),
            'service': service,
            'comment': 'comment{}'.format(i + 1),
            'created_at': '2020-12-31 20:00:00',
            'cart': {
                'total': math.ceil(float(total[i])),
                'total_rational': total[i],
                'place_slug': 'place',
            },
        }
        orders.append(order)
    if grocery_orders is not None:
        for grocery_order in grocery_orders:
            orders.append(grocery_order)
    return orders


@pytest.mark.parametrize(
    (
        'services',
        'total',
        'exp_order_ids',  # complemented by an order with grocery order circle
        'amounts',
        'exp_total',
        'feedbacks',
        'feedbacks_code',
    ),
    [
        (
            ['eats', 'grocery', 'shop', 'eats', 'grocery', 'eats'],
            ['9.8', '9.8', '9.8', '9.8', '9.8', '9.8'],
            [['id1', 'id3', 'id4', 'id6'], ['id2', 'id5']],
            {
                'id1': ['1', 'finished'],
                'id2': ['2', 'failed'],
                'id3': ['3', 'finished'],
                'id4': ['4', 'finished'],
                'id6': ['6', 'finished'],
            },
            [
                ['10.8', 11],
                ['9.8', 10],
                ['12.8', 13],
                ['13.8', 14],
                ['9.8', 10],
                ['15.8', 16],
            ],
            [
                {'order_nr': 'id1', 'status': 'noshow', 'has_feedback': True},
                {'order_nr': 'id2', 'status': 'wait', 'has_feedback': False},
                {
                    'order_nr': 'id3',
                    'status': 'cancelled',
                    'has_feedback': False,
                },
                {'order_nr': 'id4', 'status': 'show', 'has_feedback': False},
                {
                    'order_nr': 'id5',
                    'status': 'expired',
                    'has_feedback': False,
                },
                {
                    'order_nr': 'id6',
                    'status': 'cancelled',
                    'has_feedback': False,
                },
            ],
            200,
        ),
        (
            ['eats', 'grocery', 'eats', 'eats', 'grocery', 'eats'],
            ['9.8', '9.8', '9.8', '9.8', '9.8', '9.8'],
            [['id1', 'id3', 'id4', 'id6'], ['id2', 'id5']],
            {},
            [
                ['9.8', 10],
                ['9.8', 10],
                ['9.8', 10],
                ['9.8', 10],
                ['9.8', 10],
                ['9.8', 10],
            ],
            FALLBACK_FEEDBACKS,
            500,
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
            [
                ['10.8', 11],
                ['11.8', 12],
                ['9.8', 10],
                ['13.8', 14],
                ['14.8', 15],
                ['15.8', 16],
            ],
            FALLBACK_FEEDBACKS,
            500,
        ),
        ([], [], [[], []], {}, [], FALLBACK_FEEDBACKS, 500),
    ],
    ids=['greenflow', 'no_amounts', 'non_authorized', 'no_orders'],
)
@pytest.mark.config(
    EATS_ORDERS_INFO_FALLBACK_FOR_FEEDBACKS=FALLBACK_FOR_FEEDBACKS_CONFIG,
)
@pytest.mark.config(EATS_ORDERS_INFO_USE_GROCERY=True)
async def test_orders_info(
        taxi_eats_orders_info,
        services,
        total,
        exp_order_ids,
        amounts,
        exp_total,
        feedbacks,
        feedbacks_code,
        local_services,
        grocery,
):

    utils.add_grocery_info(
        grocery.get_orders(),
        amounts=amounts,
        feedbacks=feedbacks,
        exp_total=exp_total,
    )

    local_services.orders = generate_orders(
        services, total, grocery_orders=grocery.get_orders(),
    )
    local_services.core_headers = utils.get_auth_headers()

    donations = utils.generate_donations(amounts)

    local_services.brands_response = utils.generate_brands_response(
        exp_order_ids, donations, grocery_orders=grocery.get_orders(),
    )
    local_services.exp_order_ids = exp_order_ids
    local_services.feedbacks = feedbacks
    local_services.feedbacks_response_code = feedbacks_code

    response = await taxi_eats_orders_info.get(
        'api/v1/orders',
        json={'eats_user_id': EATER_ID},
        params={'limit': LIMIT, 'offset': OFFSET},
        headers=utils.get_auth_headers(),
    )
    assert response.status_code == 200
    response_body = response.json()
    assert len(response_body) == len(local_services.orders)
    for [i, order] in enumerate(local_services.orders):
        cur_order = copy.deepcopy(response_body[i])
        if response_body[i]['id'] in donations:
            assert 'donation' in response_body[i]
            assert (
                response_body[i]['donation']
                == donations[response_body[i]['id']]
            )
        else:
            assert 'donation' not in response_body[i]
        assert 'cart' in response_body[i]
        assert 'total_rational' in response_body[i]['cart']
        assert response_body[i]['cart']['total_rational'] == exp_total[i][0]
        assert 'total' in response_body[i]['cart']
        assert response_body[i]['cart']['total'] == exp_total[i][1]
        assert response_body[i]['feedback_status'] == feedbacks[i]['status']
        assert response_body[i]['has_feedback'] == feedbacks[i]['has_feedback']
        assert prepare_for_comparing_order(
            cur_order,
        ) == prepare_for_comparing_order(order)


@pytest.mark.parametrize(
    ('exp_code', 'body'),
    [
        (
            403,
            {
                'errors': [
                    {
                        'domain': 'Authorization',
                        'code': 18,
                        'error': 'Invalid session',
                    },
                ],
            },
        ),
        (404, {'message': 'message'}),
        (405, {'message': 'message'}),
        (500, {'message': 'message'}),
    ],
)
async def test_core_orders_fail(
        taxi_eats_orders_info, exp_code, body, local_services, grocery,
):
    local_services.core_response_code = exp_code
    local_services.orders = body

    response = await taxi_eats_orders_info.get(
        'api/v1/orders',
        json={'eats_user_id': EATER_ID},
        params={'limit': LIMIT, 'offset': OFFSET},
        headers=utils.get_auth_headers(),
    )
    assert response.status_code == exp_code
    assert response.json() == body


@pytest.mark.parametrize(
    ('services', 'total', 'exp_total'),
    [
        (
            ['eats', 'grocery', 'eats', 'eats', 'grocery', 'eats'],
            ['9.8', '9.8', '9.8', '9.8', '9.8', '9.8'],
            [
                ['9.8', 10],
                ['9.8', 10],
                ['9.8', 10],
                ['9.8', 10],
                ['9.8', 10],
                ['9.8', 10],
            ],
        ),
    ],
)
@pytest.mark.config(EATS_ORDERS_INFO_USE_GROCERY=True)
async def test_persey_fail(
        taxi_eats_orders_info,
        services,
        total,
        exp_total,
        local_services,
        grocery,
):
    local_services.orders = generate_orders(
        services, total, grocery_orders=grocery.get_orders(),
    )
    utils.add_grocery_info(grocery.get_orders(), exp_total=exp_total)
    local_services.persey_response_code = 500

    response = await taxi_eats_orders_info.get(
        'api/v1/orders',
        json={'eats_user_id': EATER_ID},
        params={'limit': LIMIT, 'offset': OFFSET},
        headers=utils.get_auth_headers(),
    )
    assert response.status_code == 200
    response_body = response.json()
    assert len(response_body) == len(local_services.orders)
    for [i, order] in enumerate(local_services.orders):
        cur_order = copy.deepcopy(response_body[i])
        assert 'cart' in response_body[i]
        assert 'total_rational' in response_body[i]['cart']
        assert response_body[i]['cart']['total_rational'] == exp_total[i][0]
        assert 'total' in response_body[i]['cart']
        assert response_body[i]['cart']['total'] == exp_total[i][1]
        cur_order = prepare_for_comparing_order(cur_order)
        order = prepare_for_comparing_order(order)
        assert cur_order == order


async def test_unauthorized(taxi_eats_orders_info, local_services):
    response = await taxi_eats_orders_info.get(
        'api/v1/orders', params={'limit': LIMIT, 'offset': OFFSET},
    )
    assert local_services.mock_core_orders.times_called == 0
    assert response.status_code == 403
    assert response.json() == {
        'errors': [
            {
                'domain': 'Authorization',
                'code': 18,
                'error': 'Invalid session',
            },
        ],
    }


async def test_no_grocery_request(
        taxi_eats_orders_info, local_services, grocery,
):

    local_services.persey_response_code = 500

    await taxi_eats_orders_info.get(
        'api/v1/orders',
        json={'eats_user_id': EATER_ID},
        params={'limit': LIMIT, 'offset': OFFSET},
        headers=utils.get_auth_headers(),
    )

    assert grocery.times_called_info() == 0
