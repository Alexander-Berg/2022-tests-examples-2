import pytest


@pytest.mark.parametrize(
    'params,expected_data,expected_launch_ids',
    [
        ({'task_name': 'test'}, None, ['1']),
        (
            {
                'task_name': 'logs_errors_filters-crontasks-disabler',
                'limit': 1,
            },
            [
                {
                    'id': '3',
                    'launch_status': 'in_progress',
                    'hostname': 'logserrors-sas-02.taxi.yandex.net',
                    'start_time': '2020-09-28T19:01:00+03:00',
                    'checks': {'can_be_killed': True},
                },
            ],
            None,
        ),
        (
            {
                'task_name': 'logs_errors_filters-crontasks-disabler',
                'start_to': '2020-09-28T19:00:30+03:00',
                'limit': 1,
            },
            None,
            ['2'],
        ),
        (
            {
                'task_name': 'logs_errors_filters-crontasks-disabler',
                'start_from': '2020-09-28T19:00:30+03:00',
                'limit': 1,
            },
            None,
            ['3'],
        ),
        (
            {
                'task_name': 'logs_errors_filters-crontasks-disabler',
                'hostname': 'logserrors-sas-02.taxi.yandex.net',
            },
            None,
            ['3'],
        ),
        (
            {
                'task_name': 'logs_errors_filters-crontasks-disabler',
                'launch_status': 'finished',
            },
            None,
            ['2'],
        ),
        (
            {
                'task_name': 'logs_errors_filters-crontasks-disabler',
                'launch_status': 'finished',
            },
            None,
            ['2'],
        ),
    ],
)
async def test_launches_list_get(
        web_app_client, params, expected_data, expected_launch_ids,
):
    response = await web_app_client.get('/v1/launches/list/', params=params)
    assert response.status == 200
    data = (await response.json())['launches']
    if expected_data is not None:
        assert data == expected_data
    if expected_launch_ids is not None:
        assert [launch['id'] for launch in data] == expected_launch_ids
