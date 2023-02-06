import pytest


@pytest.mark.parametrize(
    ['requests_count', 'expected_statuses'],
    [
        pytest.param(1, ['done'], id='success in first request'),
        pytest.param(2, ['queued', 'done'], id='success in second request'),
        pytest.param(2, ['queued', 'queued'], id='fail in requests, timeout'),
    ],
)
@pytest.mark.pgsql('corp_combo_orders', files=['insert_route_tasks.sql'])
@pytest.mark.config(
    CORP_ROUTING_TASKS_SYNC_SETTINGS={
        'sync_seconds_timeout': 0,
        'sync_retries_count': 2,
    },
)
async def test_sample_tasks(
        stq_runner,
        pgsql,
        load_json,
        mock_routing_api,
        requests_count,
        expected_statuses,
):
    routing_api_responses = load_json('routing_api_responses.json')
    mock_routing_api.data.get_mvpr_responses = (
        routing_api_responses[status]['response']
        for status in expected_statuses
    )
    mock_routing_api.data.response_statuses = (
        routing_api_responses[status]['code'] for status in expected_statuses
    )

    await stq_runner.corp_routes_polling_task.call(
        task_id='sample_task',
        kwargs={
            'route_task_id': 'route_task_2',
            'external_route_task_id': 'routing_task_id_2',
        },
    )

    assert mock_routing_api.get_mvpr.times_called == len(expected_statuses)

    is_task_finished = expected_statuses[-1] == 'done'

    cursor = pgsql['corp_combo_orders'].cursor()
    cursor.execute(
        'SELECT id, route_task_id, user_personal_phone_id, point, '
        'route_number, number_in_route '
        'FROM corp_combo_orders.route_task_points '
        'WHERE route_task_id = \'route_task_2\' ORDER BY id;',
    )
    assert list(cursor) == [
        (
            6,
            'route_task_2',
            'personal_6',
            {
                'geopoint': [1.0, 3.0],
                'fullname': 'Россия, Москва, Большая Никитская улица, 13',
            },
            0 if is_task_finished else None,
            0 if is_task_finished else None,
        ),
        (
            7,
            'route_task_2',
            'personal_7',
            {
                'geopoint': [1.0, 3.0],
                'fullname': 'Россия, Москва, Большая Никитская улица, 13',
            },
            1 if is_task_finished else None,
            1 if is_task_finished else None,
        ),
        (
            8,
            'route_task_2',
            'personal_8',
            {
                'geopoint': [1.0, 3.0],
                'fullname': 'Россия, Москва, Большая Никитская улица, 13',
            },
            1 if is_task_finished else None,
            0 if is_task_finished else None,
        ),
    ]

    cursor.execute(
        'SELECT id, client_id, external_route_task_id, route_type, '
        'task_status, common_point '
        'FROM corp_combo_orders.route_tasks WHERE id = \'route_task_2\';',
    )
    assert list(cursor) == [
        (
            'route_task_2',
            'client_id_1',
            'routing_task_id_2',
            'ONE_A_MANY_B',
            'done' if is_task_finished else 'failed',
            {
                'geopoint': [1.0, 2.0],
                'fullname': 'Россия, Москва, Большая Никитская улица, 13',
            },
        ),
    ]
