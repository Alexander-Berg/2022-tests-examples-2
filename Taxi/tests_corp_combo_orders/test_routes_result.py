import datetime

import pytest


NOW = datetime.datetime(2021, 10, 5, 17, 10)


@pytest.mark.parametrize(
    ['route_task_id', 'expected_status', 'expected_response'],
    [
        pytest.param(
            'route_task_1',
            200,
            {
                'route_task_id': 'route_task_1',
                'task_status': 'done',
                'client_id': 'client_id_1',
                'result': {
                    'common_point': {
                        'fullname': (
                            'Россия, Москва, Большая Никитская улица, 13'
                        ),
                        'geopoint': [1.0, 2.0],
                    },
                    'route_type': 'ONE_A_MANY_B',
                    'routes': [
                        {
                            'user_points': [
                                {
                                    'point': {
                                        'fullname': (
                                            'Россия, Москва, Большая '
                                            'Никитская улица, 13'
                                        ),
                                        'geopoint': [1.0, 3.0],
                                    },
                                    'user_personal_phone_id': 'personal_2',
                                },
                                {
                                    'point': {
                                        'fullname': (
                                            'Россия, Москва, Большая '
                                            'Никитская улица, 13'
                                        ),
                                        'geopoint': [1.0, 3.0],
                                    },
                                    'user_personal_phone_id': 'personal_1',
                                },
                            ],
                        },
                        {
                            'user_points': [
                                {
                                    'point': {
                                        'fullname': (
                                            'Россия, Москва, Большая '
                                            'Никитская улица, 13'
                                        ),
                                        'geopoint': [1.0, 3.0],
                                    },
                                    'user_personal_phone_id': 'personal_3',
                                },
                                {
                                    'point': {
                                        'fullname': (
                                            'Россия, Москва, Большая '
                                            'Никитская улица, 13'
                                        ),
                                        'geopoint': [1.0, 3.0],
                                    },
                                    'user_personal_phone_id': 'personal_5',
                                },
                                {
                                    'point': {
                                        'fullname': (
                                            'Россия, Москва, Большая '
                                            'Никитская улица, 13'
                                        ),
                                        'geopoint': [1.0, 3.0],
                                    },
                                    'user_personal_phone_id': 'personal_4',
                                },
                            ],
                        },
                    ],
                },
            },
            id='solved task',
        ),
        pytest.param(
            'route_task_2',
            200,
            {
                'route_task_id': 'route_task_2',
                'task_status': 'queued',
                'client_id': 'client_id_1',
            },
            id='not yet solved task',
        ),
        pytest.param(
            'route_task_3',
            200,
            {
                'route_task_id': 'route_task_3',
                'task_status': 'failed',
                'client_id': 'client_id_1',
            },
            id='failed task',
        ),
        pytest.param(
            'route_task_20',
            404,
            {
                'code': 'ROUTE_TASK_NOT_FOUND',
                'message': 'Route task route_task_20 not found',
            },
            id='idempotency token does not exist',
        ),
    ],
)
@pytest.mark.pgsql('corp_combo_orders', files=['insert_route_tasks.sql'])
async def test_get_result(
        taxi_corp_combo_orders,
        route_task_id,
        expected_status,
        expected_response,
):
    response = await taxi_corp_combo_orders.post(
        '/v1/routes/result', params={'route_task_id': route_task_id},
    )

    assert response.status == expected_status
    assert response.json() == expected_response
