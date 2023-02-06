import freezegun
import pytest

from clownductor.internal.tasks import cubes


def task_data(name):
    return {
        'id': 123,
        'job_id': 456,
        'name': name,
        'sleep_until': 0,
        'input_mapping': {},
        'output_mapping': {},
        'payload': {},
        'retries': 0,
        'status': 'in_progress',
        'error_message': None,
        'created_at': 0,
        'updated_at': 0,
    }


@pytest.mark.parametrize(
    'input_data, expected_views',
    [
        pytest.param(
            {
                'name': 'taxi_admin-front_testing',
                'state': 1,
                'project_names': ['test_project'],
                'st_key': 'TAXIREL-1',
            },
            ['__all__'],
        ),
        pytest.param(
            {
                'name': 'taxi_admin-front_testing',
                'state': 1,
                'st_key': 'TAXIREL-1',
            },
            ['__all__'],
        ),
        pytest.param(
            {
                'name': 'taxi_admin-front_testing',
                'state': 1,
                'st_key': 'TAXIREL-1',
                'service_id': 1,
            },
            ['taxi'],
            marks=pytest.mark.features_on('enable_namespace_notification'),
        ),
        pytest.param(
            {
                'name': 'taxi_admin-front_testing',
                'state': 1,
                'st_key': 'TAXIREL-1',
            },
            ['__all__'],
            marks=pytest.mark.features_on('enable_namespace_notification'),
        ),
    ],
)
@pytest.mark.features_on('enable_lenta_notifications')
@pytest.mark.pgsql('clownductor', files=['init.sql'])
@freezegun.freeze_time('2022-05-26T12:00:00')
async def test_notifications_cube_lenta(
        web_context, patch, input_data, expected_views, mockserver,
):
    @mockserver.json_handler('/lenta-api/events/submit')
    async def _post_to_lenta(request):
        return mockserver.make_response(json={})

    @mockserver.json_handler('/infra-events/v1/events')
    async def _v1_events_post(request):
        return mockserver.make_response(json={'events_ids': ['1']})

    cube = cubes.CUBES['NotificationsCubeLenta'](
        web_context, task_data('NotificationsCubeLenta'), input_data, [], None,
    )

    await cube.update()
    assert cube.success

    assert _post_to_lenta.times_called == 1
    # pylint: disable=protected-access
    case_request_old_lenta = _post_to_lenta._queue._queue[0][0][0]
    assert case_request_old_lenta.json == [
        {
            'timestamp': 1653566400000,
            'header': 'Завершилась выкладка на taxi_admin-front_testing',
            'source': 'clownductor',
            'body': (
                '((https://st.yandex-team.ru/TAXIREL-1 '
                'https://st.yandex-team.ru/TAXIREL-1))'
            ),
        },
    ]
    assert _v1_events_post.times_called == 1
    # pylint: disable=protected-access
    case_request_infra_events = _v1_events_post._queue._queue[0][0][0]
    assert case_request_infra_events.json == {
        'events': [
            {
                'header': 'Завершилась выкладка на taxi_admin-front_testing',
                'views': expected_views,
                'body': (
                    '((https://st.yandex-team.ru/TAXIREL-1 '
                    'https://st.yandex-team.ru/TAXIREL-1))'
                ),
            },
        ],
    }
