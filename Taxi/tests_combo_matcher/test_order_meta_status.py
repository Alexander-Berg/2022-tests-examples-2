import functools
import json

import pytest


DRIVER = {
    'orders': ['order_id_1', 'order_id_2'],
    'path': [
        [37.642686, 55.740843],
        [37.642697, 55.740854],
        [37.642608, 55.740865],
        [37.642619, 55.740876],
    ],
}

SQL_INSERT_TEMPLATE = functools.partial(
    'WITH new_matching AS ('
    '   INSERT INTO combo_matcher.matchings (id,orders,driver, combo_info)'
    '   VALUES (1, \'{{ '
    'order_id_1'
    ', '
    'order_id_2'
    ' }}\', \'{driver}\', \'{{}}\')'
    '   RETURNING id )'
    ' INSERT INTO combo_matcher.order_meta'
    ' (order_id, zone, created, due, point, point_b,'
    'status, matching_id, allowed_classes, user_id)'
    ' VALUES (\'order_id_1\', \'moscow\', now(), now(),'
    ' point(0, 0), point(0, 0),'
    ' \'{order_status}\', (SELECT id FROM new_matching), \'{{""}}\', \'{user_id}\')'.format,
    driver=json.dumps(DRIVER),
)


@pytest.mark.parametrize(
    'dd_request,expected_response_code,expected_response_data,register',
    [
        # matched with config
        (
            {'order_id': 'order_id_1'},
            200,
            {
                'eta_mins_from': 7,
                'eta_mins_to': 10,
                'multiorder_info': {'subtitle': 'Найдем за 7-10 минут'},
                'status': 'matching',
            },
            SQL_INSERT_TEMPLATE(order_status='idle', user_id='user_id_1'),
        ),
        # key does not exist
        (
            {'order_id': 'order_id_1'},
            500,
            {},
            SQL_INSERT_TEMPLATE(order_status='matching', user_id='user_id_2'),
        ),
        # no key
        (
            {'order_id': 'order_id_1'},
            200,
            {'eta_mins_from': 2, 'eta_mins_to': 6, 'status': 'matching'},
            SQL_INSERT_TEMPLATE(order_status='matched', user_id='user_id_3'),
        ),
        # default value, no user_id
        (
            {'order_id': 'order_id_1'},
            200,
            {'eta_mins_from': 1, 'eta_mins_to': 5, 'status': 'matching'},
            SQL_INSERT_TEMPLATE(order_status='performer_found', user_id=None),
        ),
        (
            {'order_id': 'order_id_1'},
            200,
            {'eta_mins_from': 1, 'eta_mins_to': 5, 'status': 'assigned'},
            SQL_INSERT_TEMPLATE(order_status='dispatched', user_id=None),
        ),
        (
            {'order_id': 'order_id_1'},
            200,
            {'eta_mins_from': 1, 'eta_mins_to': 5, 'status': 'assigned'},
            SQL_INSERT_TEMPLATE(order_status='assigned', user_id=None),
        ),
        (
            {'order_id': 'order_id_1'},
            200,
            {'eta_mins_from': 1, 'eta_mins_to': 5, 'status': 'expired'},
            SQL_INSERT_TEMPLATE(order_status='removed', user_id=None),
        ),
        (
            {'order_id': 'non_existent_order_id'},
            404,
            {},
            SQL_INSERT_TEMPLATE(order_status='matched', user_id=None),
        ),
    ],
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='combo_matcher_client_search_limits',
    consumers=['combo_matcher/client_search_limits'],
    clauses=[
        {
            'title': '1',
            'value': {
                'enabled': True,
                'eta_mins_to': 10,
                'eta_mins_from': 7,
                'matching_message_key': 'combo_matcher.client_search_key',
            },
            'enabled': True,
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'user_id',
                    'arg_type': 'string',
                    'value': 'user_id_1',
                },
            },
        },
        {
            'title': '2',
            'value': {
                'enabled': True,
                'eta_mins_to': 10,
                'eta_mins_from': 7,
                'matching_message_key': (
                    'combo_matcher.nonexistent_client_search_key'
                ),
            },
            'enabled': True,
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'user_id',
                    'arg_type': 'string',
                    'value': 'user_id_2',
                },
            },
        },
        {
            'title': '3',
            'value': {'enabled': True, 'eta_mins_to': 6, 'eta_mins_from': 2},
            'enabled': True,
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'user_id',
                    'arg_type': 'string',
                    'value': 'user_id_3',
                },
            },
        },
    ],
)
@pytest.mark.translations(
    client_messages={
        'combo_matcher.client_search_key': {
            'ru': 'Найдем за %(eta_from)d-%(eta_to)d минут',
        },
    },
)
async def test_order_meta_status(
        taxi_combo_matcher,
        dd_request,
        expected_response_code,
        expected_response_data,
        register,
        pgsql,
):
    await taxi_combo_matcher.invalidate_caches()

    if register:
        cursor = pgsql['combo_matcher'].cursor()
        cursor.execute(register)

    response = await taxi_combo_matcher.post(
        'v1/order-meta/status', json=dd_request,
    )
    # assert response.status_code == expected_response_code
    # if response.status_code == 200:
    #     assert response.json() == expected_response_data
