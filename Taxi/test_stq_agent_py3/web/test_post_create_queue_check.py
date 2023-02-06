# pylint: disable=redefined-outer-name
import pytest

from taxi import settings

from test_stq_agent_py3 import util


@pytest.mark.config(
    DEV_TEAMS={'test_team': {'description': 'Test team'}},
    STQ_DEFAULT_MONITORING_THRESHOLDS={'total': {'warning': 1, 'critical': 5}},
)
@util.parametrize_data(
    __file__,
    'test_post_create_queue_check_200.json',
    ('data', 'expected_new'),
)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_create_queue_check_200(
        web_app_client, mock_conductor, data, expected_new, monkeypatch,
):
    mock_conductor(
        hosts_info=[
            {
                'group': 'taxi_stq',
                'hostname': 'taxi-stq-sas-06.taxi.yandex.net',
                'datacenter': 'dc1',
            },
            {
                'group': 'taxi_stq',
                'hostname': 'taxi-stq-vla-06.taxi.yandex.net',
                'datacenter': 'dc2',
            },
            {
                'group': 'test_prestable_stq',
                'hostname': 'taxi-stq-sas-06.taxi.yandex.net',
                'datacenter': 'dc1',
            },
        ],
    )
    response = await web_app_client.post('/queue/create/check/', json=data)
    assert response.status == 200
    result = await response.json()
    assert result['data'] == data


@pytest.mark.config(
    DEV_TEAMS={'test_team': {'description': 'Test team'}},
    STQ_DEFAULT_MONITORING_THRESHOLDS={'total': {'warning': 1, 'critical': 5}},
)
@util.parametrize_data(
    __file__,
    'test_post_create_queue_check_with_tplatform.json',
    ('data', 'expected_new', 'tplatform'),
)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_create_queue_check_with_tplatform(
        web_app_client,
        mock_conductor,
        data,
        expected_new,
        tplatform,
        monkeypatch,
):
    mock_conductor(
        hosts_info=[
            {
                'group': 'taxi_stq',
                'hostname': 'taxi-stq-sas-06.taxi.yandex.net',
                'datacenter': 'dc1',
            },
            {
                'group': 'taxi_stq',
                'hostname': 'taxi-stq-vla-06.taxi.yandex.net',
                'datacenter': 'dc2',
            },
            {
                'group': 'test_prestable_stq',
                'hostname': 'taxi-stq-sas-06.taxi.yandex.net',
                'datacenter': 'dc1',
            },
        ],
    )
    response = await web_app_client.post('/queue/create/check/', json=data)
    assert response.status == 200
    result = await response.json()
    assert result['data'] == data
    assert result['tplatform_namespace'] == tplatform


@pytest.mark.config(DEV_TEAMS={'test_team': {'description': 'Test team'}})
@pytest.mark.parametrize(
    'data, expected_error',
    [
        (
            {
                'queue_name': 'new_example_queue',
                'dev_team': 'test_team',
                'shards': [
                    {
                        'connection_name': 'stq',
                        'database': 'dbstq',
                        'hostnames': ['taxi-stq-sas-11.taxi.yandex.net'],
                    },
                ],
                'worker_configs': {
                    'instances': 1,
                    'max_tasks': 10,
                    'max_execution_time': 120,
                },
            },
            'Invalid shards configuration: shard #0 contains unknown '
            'host taxi-stq-sas-11.taxi.yandex.net',
        ),
        (
            {
                'queue_name': 'new_example_queue',
                'description': 'Образцовая очередь',
                'is_enabled': False,
                'dev_team': 'test_team',
                'shards': [
                    {
                        'collection': 'new_example_queue_shard_0',
                        'connection_name': 'stq',
                        'database': 'dbstq',
                        'hostnames': [
                            'taxi-stq-sas-06.taxi.yandex.net',
                            'taxi-stq-vla-06.taxi.yandex.net',
                        ],
                    },
                    {
                        'collection': 'new_example_queue_shard_0',
                        'connection_name': 'stq',
                        'database': 'dbstq',
                        'hostnames': [
                            'taxi-stq-sas-06.taxi.yandex.net',
                            'taxi-stq-vla-06.taxi.yandex.net',
                        ],
                    },
                ],
                'worker_configs': {
                    'instances': 1,
                    'max_tasks': 10,
                    'max_execution_time': 120,
                },
            },
            'Invalid shards configuration: collection '
            'dbstq.new_example_queue_shard_0 specified for multiple shards',
        ),
        (
            {
                'queue_name': 'new_example_queue',
                'description': 'Образцовая очередь',
                'dev_team': 'test_team',
                'balancing_enabled': True,
                'is_enabled': False,
                'shards': [
                    {
                        'connection_name': 'stq',
                        'database': 'dbstq',
                        'hostnames': [
                            'taxi-stq-sas-06.taxi.yandex.net',
                            'taxi-stq-vla-06.taxi.yandex.net',
                        ],
                    },
                    {
                        'connection_name': 'stq',
                        'database': 'dbstq',
                        'hostnames': [
                            'taxi-stq-sas-06.taxi.yandex.net',
                            'taxi-stq-vla-06.taxi.yandex.net',
                        ],
                    },
                ],
                'worker_configs': {
                    'instances': 1,
                    'max_tasks': 10,
                    'max_execution_time': 120,
                },
            },
            'Balancing cannot be enabled without guarantee specified',
        ),
        (
            {
                'queue_name': 'new_example_queue',
                'is_enabled': False,
                'dev_team': 'non_existent_team',
                'shards': [
                    {
                        'connection_name': 'stq',
                        'database': 'dbstq',
                        'hostnames': [
                            'taxi-stq-sas-06.taxi.yandex.net',
                            'taxi-stq-vla-06.taxi.yandex.net',
                        ],
                    },
                ],
                'worker_configs': {
                    'instances': 1,
                    'max_tasks': 10,
                    'max_execution_time': 120,
                },
            },
            'Team non_existent_team not found in DEV_TEAMS config',
        ),
    ],
)
async def test_create_queue_check_400(
        web_app_client,
        mock_conductor,
        data,
        expected_error,
        mock_clownductor_empty,
):
    mock_conductor(
        hosts_info=[
            {
                'group': 'taxi_stq',
                'hostname': 'taxi-stq-sas-06.taxi.yandex.net',
                'datacenter': 'dc1',
            },
            {
                'group': 'taxi_stq',
                'hostname': 'taxi-stq-vla-06.taxi.yandex.net',
                'datacenter': 'dc2',
            },
            {
                'group': 'test_prestable_stq',
                'hostname': 'taxi-stq-sas-06.taxi.yandex.net',
                'datacenter': 'dc1',
            },
        ],
    )
    response = await web_app_client.post('/queue/create/check/', json=data)
    assert response.status == 400
    assert (await response.json())['message'] == expected_error


async def test_create_queue_check_project_not_found_404(
        web_app_client, monkeypatch,
):
    monkeypatch.setattr(settings, 'ENVIRONMENT', settings.PRODUCTION)
    response = await web_app_client.post(
        '/queue/create/check',
        json={
            'queue_name': 'new_example_queue',
            'dev_team': 'some_team',
            'write_concern': False,
            'state': 'enabled',
            'version': 1,
            'shards': [
                {
                    'collection': 'new_example_queue_0',
                    'connection_name': 'stq',
                    'database': 'dbstq',
                },
            ],
            'department': 'test_project',
            'worker_configs': {
                'max_tasks': 3,
                'instances': 1,
                'max_execution_time': 10,
            },
        },
    )
    assert response.status == 404
    assert (await response.json())[
        'message'
    ] == 'Project test_project was not found in clownductor cache'
