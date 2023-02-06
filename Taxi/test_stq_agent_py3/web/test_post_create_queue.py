# pylint: disable=redefined-outer-name, unused-variable
import pytest

from taxi import settings

from stq_agent_py3.common import stq_maintenance
from test_stq_agent_py3 import util


@pytest.mark.config(DEV_TEAMS={'test_team': {'description': 'Test team'}})
async def test_create_queue_409(web_app_client):
    response = await web_app_client.post(
        '/queue/create/',
        json={
            'queue_name': 'example_queue',
            'dev_team': 'test_team',
            'shards': [
                {
                    'collection': 'example_queue_0',
                    'connection_name': 'stq',
                    'database': 'dbstq',
                    'hostnames': [],
                },
                {
                    'collection': 'example_queue_1',
                    'connection_name': 'stq',
                    'database': 'dbstq',
                    'hostnames': [],
                },
            ],
            'worker_configs': {
                'max_tasks': 2,
                'instances': 1,
                'max_execution_time': 10,
            },
        },
    )
    assert response.status == 409, await response.text()


@pytest.mark.config(DEV_TEAMS={'test_team': {'description': 'Test team'}})
@pytest.mark.parametrize(
    'data, expected_text',
    [
        (
            {
                'queue_name': 'new_example_queue',
                'dev_team': 'test_team',
                'balancing_enabled': True,
                'workers_guarantee': 2,
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
                    'max_tasks': 1,
                    'max_execution_time': 120,
                },
            },
            'max_tasks (1) must be greater than or equal to (2)',
        ),
        (
            {
                'queue_name': 'new_example_queue',
                'dev_team': 'test_team',
                'shards': [
                    {
                        'connection_name': 'stq',
                        'database': 'dbstq',
                        'hostnames': [
                            'taxi-stq-sas-11.taxi.yandex.net',
                            'taxi-stq-sas-12.taxi.yandex.net',
                        ],
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
        (
            {
                'queue_name': 'new_example_queue',
                'is_enabled': False,
                'dev_team': 'test_team',
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
                'task_input_restriction': {
                    'enable_restriction': True,
                    'by_tvm_services': {'source_service_not_in_config': -1},
                },
            },
            'Service name source_service_not_in_config'
            ' not found in TVM_SERVICES config',
        ),
    ],
)
@pytest.mark.config(TVM_SERVICES={'source_service': 10001})
async def test_create_queue_400(
        web_app_client, mock_conductor, data, expected_text, mock_clownductor,
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

    @mock_clownductor('/v1/hosts/')
    def handler(request):
        if request.args['fqdn'] == 'taxi-stq-sas-12.taxi.yandex.net':
            return [
                {
                    'name': 'taxi-stq-sas-12.taxi.yandex.net',
                    'datacenter': 'dc1',
                    'branch_name': 'pre_stable',
                    'branch_id': 1,
                },
            ]
        return []

    response = await web_app_client.post('/queue/create/', json=data)
    assert response.status == 400
    assert (await response.json())['message'] == expected_text


@pytest.mark.config(
    DEV_TEAMS={'test_team': {'description': 'Test team'}},
    STQ_DEFAULT_MONITORING_THRESHOLDS={'total': {'warning': 1, 'critical': 5}},
    TVM_SERVICES={
        'source_service': 10001,
        'source_service_1': 10002,
        'source_service_2': 10003,
    },
)
@util.parametrize_data(
    __file__, 'test_post_create_queue_200.json', ('data', 'expected_config'),
)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_create_queue_200(
        web_app_client,
        mock_conductor,
        data,
        expected_config,
        monkeypatch,
        patch_current_date,
):
    async def _dummy_create(*args, **kwargs):
        pass

    monkeypatch.setattr(stq_maintenance, 'create_stq_indexes', _dummy_create)

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

    response = await web_app_client.post('/queue/create/', json=data)
    assert response.status == 200
    assert await response.json() == expected_config


@pytest.mark.parametrize(
    'data',
    [
        {
            'queue_name': 'new_example_queue',
            'dev_team': 'test_team',
            'shards': [
                {
                    'connection_name': 'stq',
                    'database': 'dbstq',
                    'hostnames': [],
                },
                {
                    'connection_name': 'stq',
                    'database': 'dbstq',
                    'hostnames': [],
                },
            ],
            'write_concern': True,
            'worker_configs': {
                'max_tasks': 2,
                'instances': 1,
                'max_execution_time': 10,
            },
        },
    ],
)
@pytest.mark.config(DEV_TEAMS={'test_team': {'description': 'Test team'}})
async def test_create_queue_500(
        web_app_client, mock_conductor, data, monkeypatch, db,
):
    async def _error_create(*args, **kwargs):
        raise stq_maintenance.CreateIndexesError(
            'Indexes could not be created',
        )

    monkeypatch.setattr(stq_maintenance, 'create_stq_indexes', _error_create)

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

    response = await web_app_client.post('/queue/create/', json=data)
    assert response.status == 500, await response.text()
    assert (await response.json())['code'] == 'INTERNAL_SERVER_ERROR'
    assert await db.stq_config.find_one(data['queue_name']) is None


async def test_create_queue_project_not_found_404(web_app_client, monkeypatch):
    monkeypatch.setattr(settings, 'ENVIRONMENT', settings.PRODUCTION)
    response = await web_app_client.post(
        '/queue/create/',
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
