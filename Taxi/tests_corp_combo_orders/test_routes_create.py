import datetime

import pytest


NOW = datetime.datetime(2021, 10, 5, 17, 10)

BASE_REQUEST = {
    'client_id': 'client_id_1',
    'route_type': 'ONE_A_MANY_B',
    'common_point': {
        'country': 'Россия',
        'geopoint': [37, 55],
        'fullname': 'Россия, Москва, Большая Никитская улица, 13',
    },
    'user_points': [
        {
            'user_personal_phone_id': '+79998887766',
            'point': {
                'country': 'Россия',
                'geopoint': [37, 55],
                'fullname': 'Россия, Москва, Большая Никитская улица, 13',
            },
        },
        {
            'user_personal_phone_id': '+79998887755',
            'point': {
                'country': 'Россия',
                'geopoint': [37, 55],
                'fullname': 'Россия, Москва, Большая Никитская улица, 13',
            },
        },
    ],
}


@pytest.mark.parametrize(
    [
        'idempotency_token',
        'request_body',
        'expected_status',
        'expected_response',
    ],
    [
        pytest.param(
            'new_idempotency_token',
            BASE_REQUEST,
            200,
            {'route_task_id': 5},
            id='successful request',
        ),
        pytest.param(
            'e98858cb-d778-4d76-89e2-635728334138',
            BASE_REQUEST,
            409,
            {
                'code': 'ROUTE_TASK_ALREADY_CREATED',
                'message': (
                    'Route task with '
                    'e98858cb-d778-4d76-89e2-635728334138 already created'
                ),
            },
            id='route task already created',
        ),
        pytest.param(
            'new_idempotency_token',
            {**BASE_REQUEST, **{'user_points': []}},
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 390, path \'user_points\': '
                    'incorrect size, must be 1 '
                    '(limit) <= 0 (value)'
                ),
            },
            id='empty points, 400',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('corp_combo_orders', files=['insert_route_tasks.sql'])
async def test_create(
        taxi_corp_combo_orders,
        stq,
        load_json,
        pgsql,
        mock_routing_api,
        mock_taxi_tariffs,
        mock_protocol,
        idempotency_token,
        request_body,
        expected_status,
        expected_response,
):
    mock_routing_api.data.add_mvpr_response = {
        'id': '1',
        'status': {'queued': 1633592047.65473},
    }
    mock_taxi_tariffs.data.current_tariff_response = load_json(
        'taxi_tariffs_response.json',
    )
    mock_protocol.data.nearest_zone_response = {'nearest_zone': 'moscow'}

    response = await taxi_corp_combo_orders.post(
        '/v1/routes/create',
        json=request_body,
        headers={'X-Idempotency-Token': idempotency_token},
    )

    response_data = response.json()
    assert response.status == expected_status, response_data

    if response.status != 200:
        assert response_data == expected_response
    else:
        assert isinstance(response_data['route_task_id'], str)
        assert len(response_data['route_task_id']) == 32

        routing_request = mock_routing_api.add_mvpr.next_call()['request']
        assert routing_request.query['apikey'] == 'test_routing_api_key'
        assert routing_request.json == load_json('routing_api_request.json')

        assert stq.corp_routes_polling_task.times_called == 1
        stq_call_request = stq.corp_routes_polling_task.next_call()
        stq_call_request['kwargs'].pop('log_extra')
        assert stq_call_request == {
            'args': [],
            'eta': NOW,
            'id': f'{response_data["route_task_id"]}_1',
            'kwargs': {
                'route_task_id': response_data['route_task_id'],
                'external_route_task_id': '1',
            },
            'queue': 'corp_routes_polling_task',
        }

        cursor = pgsql['corp_combo_orders'].cursor()
        cursor.execute(
            'SELECT id, idempotency_token, client_id, '
            'external_route_task_id, route_type, task_status, '
            'common_point '
            'FROM corp_combo_orders.route_tasks WHERE id = %s;',
            (response_data['route_task_id'],),
        )
        assert list(cursor) == [
            (
                response_data['route_task_id'],
                'new_idempotency_token',
                'client_id_1',
                None,
                'ONE_A_MANY_B',
                'queued',
                {
                    'geopoint': [37.0, 55.0],
                    'fullname': 'Россия, Москва, Большая Никитская улица, 13',
                },
            ),
        ]

        cursor.execute(
            'SELECT id, route_task_id, user_personal_phone_id, point, '
            'route_number, number_in_route '
            'FROM corp_combo_orders.route_task_points '
            'WHERE route_task_id = %s ORDER BY id;',
            (response_data['route_task_id'],),
        )
        assert list(cursor) == [
            (
                11,
                response_data['route_task_id'],
                '+79998887766',
                {
                    'geopoint': [37.0, 55.0],
                    'fullname': 'Россия, Москва, Большая Никитская улица, 13',
                },
                None,
                None,
            ),
            (
                12,
                response_data['route_task_id'],
                '+79998887755',
                {
                    'geopoint': [37.0, 55.0],
                    'fullname': 'Россия, Москва, Большая Никитская улица, 13',
                },
                None,
                None,
            ),
        ]
