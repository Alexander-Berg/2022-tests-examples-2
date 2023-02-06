# pylint: disable=redefined-outer-name
import pytest

from taxi import settings

from test_stq_agent_py3 import util


async def test_modify_queue_check_404(web_app_client):
    response = await web_app_client.put(
        '/queue/modify/check/',
        json={
            'queue_name': 'non_existent_queue',
            'write_concern': False,
            'state': 'enabled',
            'shards': [],
            'version': 1,
            'worker_configs': {
                'max_tasks': 1,
                'instances': 1,
                'max_execution_time': 10,
            },
        },
    )
    assert response.status == 404
    assert (await response.json())[
        'message'
    ] == 'Queue non_existent_queue not found'


async def test_modify_queue_check_project_not_found_404(
        web_app_client, monkeypatch,
):
    monkeypatch.setattr(settings, 'ENVIRONMENT', settings.PRODUCTION)
    response = await web_app_client.put(
        '/queue/modify/check/',
        json={
            'queue_name': 'example_queue',
            'version': 1,
            'shards': [
                {
                    'collection': 'example_queue_0',
                    'connection_name': 'stq',
                    'database': 'dbstq',
                },
                {
                    'collection': 'example_queue_1',
                    'connection_name': 'stq',
                    'database': 'dbstq',
                },
            ],
            'department': 'test_project',
            'write_concern': False,
            'state': 'enabled',
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


@pytest.mark.parametrize(
    'data, expected_text',
    [
        (
            {
                'queue_name': 'example_queue',
                'shards': [
                    {
                        'hostnames': ['taxi-stq-sas-50.taxi.yandex.net'],
                        'collection': 'example_queue_0',
                        'connection_name': 'stq',
                        'database': 'dbstq',
                    },
                ],
                'state': 'enabled',
                'worker_configs': {
                    'instances': 1,
                    'max_tasks': 10,
                    'max_execution_time': 120,
                },
                'write_concern': False,
                'version': 3,
            },
            'Invalid shards configuration: shard #0 contains '
            'unknown host taxi-stq-sas-50.taxi.yandex.net',
        ),
        (
            {
                'queue_name': 'example_queue',
                'shards': [
                    {
                        'collection': 'example_queue_0',
                        'connection_name': 'stq',
                        'database': 'dbstq',
                        'hostnames': [
                            'taxi-stq-sas-06.taxi.yandex.net',
                            'taxi-stq-vla-06.taxi.yandex.net',
                        ],
                    },
                ],
                'state': 'enabled',
                'worker_configs': {
                    'instances': 1,
                    'max_tasks': 10,
                    'max_execution_time': 120,
                },
                'write_concern': False,
                'version': 3,
            },
            'Number of shards can not be changed without migration (was 2)',
        ),
    ],
)
async def test_modify_queue_check_400(
        web_app_client,
        mock_conductor,
        data,
        expected_text,
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
    response = await web_app_client.put('/queue/modify/check/', json=data)
    assert response.status == 400
    assert (await response.json())['message'] == expected_text


@pytest.mark.parametrize(
    'data',
    [
        {
            'queue_name': 'queue_with_old_shards',
            'shards': [
                {
                    'collection': 'queue_with_old_shards_0',
                    'connection_name': 'stq1',
                    'database': 'dbstqorder0',
                    'hostnames': [],
                    'state': 'disabled',
                },
                {
                    'collection': 'queue_with_old_shards_1',
                    'connection_name': 'stq1',
                    'database': 'dbstqorder0',
                    'hostnames': [],
                    'state': 'enabled',
                },
                {
                    'collection': 'queue_with_old_shards_2',
                    'connection_name': 'stq1',
                    'database': 'dbstqorder0',
                    'hostnames': [],
                    'state': 'enabled',
                },
            ],
            'state': 'enabled',
            'version': 3,
            'worker_configs': {
                'instances': 10,
                'max_execution_time': 120,
                'max_tasks': 100,
                'polling_interval': 0.5,
            },
            'write_concern': True,
        },
        {
            'queue_name': 'queue_with_old_shards',
            'shards': [
                {
                    'collection': 'queue_with_old_shards_0',
                    'connection_name': 'stq',
                    'database': 'dbstqorder1',
                    'hostnames': [],
                    'state': 'disabled',
                },
                {
                    'collection': 'queue_with_old_shards_1',
                    'connection_name': 'stq',
                    'database': 'dbstqorder1',
                    'hostnames': [],
                    'state': 'enabled',
                },
                {
                    'collection': 'queue_with_old_shards_2',
                    'connection_name': 'stq',
                    'database': 'dbstqorder1',
                    'hostnames': [],
                    'state': 'enabled',
                },
            ],
            'state': 'enabled',
            'version': 3,
            'worker_configs': {
                'instances': 10,
                'max_execution_time': 120,
                'max_tasks': 100,
                'polling_interval': 0.5,
            },
            'write_concern': True,
        },
    ],
)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_modify_queue_check_when_old_shards_exist_400(
        web_app_client, data,
):
    response = await web_app_client.put('/queue/modify/check/', json=data)
    assert response.status == 400
    result = await response.json()
    assert (
        result['message']
        == 'At the moment, tasks of this queue are being moved '
        'between databases, database changes are not available'
    )


@util.parametrize_data(
    __file__, 'test_put_modify_queue_check_200.json', ('data', 'expected_new'),
)
@pytest.mark.config(
    STQ_DEFAULT_MONITORING_THRESHOLDS={'total': {'warning': 1, 'critical': 5}},
)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_modify_queue_check_200(
        web_app_client, mock_conductor, data, expected_new,
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

    response = await web_app_client.put('/queue/modify/check/', json=data)
    assert response.status == 200
    result = await response.json()
    assert result['diff']['new'] == expected_new
    assert result['data'] == data


@util.parametrize_data(
    __file__,
    'test_put_modify_queue_check_with_tplatform.json',
    ('data', 'expected_new', 'tplatform'),
)
@pytest.mark.config(
    STQ_DEFAULT_MONITORING_THRESHOLDS={'total': {'warning': 1, 'critical': 5}},
)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_modify_queue_check_with_tplatform(
        web_app_client, mock_conductor, data, expected_new, tplatform,
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

    response = await web_app_client.put('/queue/modify/check/', json=data)
    assert response.status == 200
    result = await response.json()
    assert result['diff']['new'] == expected_new
    assert result['data'] == data
    assert result['tplatform_namespace'] == tplatform
