# pylint: disable=redefined-outer-name
import pytest

from taxi import settings

from stq_agent_py3.common import stq_shards
from test_stq_agent_py3 import util


async def test_modify_queue_404(web_app_client):
    response = await web_app_client.put(
        '/queue/modify/',
        json={
            'queue_name': 'non_existent_queue',
            'shards': [],
            'version': 1,
            'write_concern': False,
            'state': 'enabled',
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


async def test_modify_queue_project_not_found_404(web_app_client, monkeypatch):
    monkeypatch.setattr(settings, 'ENVIRONMENT', settings.PRODUCTION)
    response = await web_app_client.put(
        '/queue/modify/',
        json={
            'queue_name': 'example_queue',
            'version': 1,
            'dev_team': 'some_team',
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
            'write_concern': False,
            'state': 'enabled',
            'department': 'test_project',
            'worker_configs': {
                'max_tasks': 10,
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
                        'hostnames': [
                            'taxi-stq-sas-06.taxi.yandex.net',
                            'taxi-stq-vla-06.taxi.yandex.net',
                        ],
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
            'Number of shards can not be changed without migration (was 2)',
        ),
        (
            {
                'queue_name': 'example_queue',
                'shards': [
                    {
                        'hostnames': [
                            'taxi-stq-sas-06.taxi.yandex.net',
                            'taxi-stq-vla-06.taxi.yandex.net',
                        ],
                        'collection': 'example_queue_0',
                        'connection_name': 'stq',
                        'database': 'dbstq',
                    },
                    {
                        'hostnames': [
                            'taxi-stq-sas-06.taxi.yandex.net',
                            'taxi-stq-vla-06.taxi.yandex.net',
                        ],
                        'collection': 'example_queue_1',
                        'connection_name': 'stq',
                        'database': 'dbstq',
                    },
                ],
                'state': 'enabled',
                'task_input_restriction': {
                    'enable_restriction': True,
                    'by_tvm_services': {'source_service_not_in_config': -1},
                },
                'worker_configs': {
                    'instances': 1,
                    'max_tasks': 10,
                    'max_execution_time': 120,
                },
                'write_concern': False,
                'version': 3,
            },
            'Service name source_service_not_in_config '
            'not found in TVM_SERVICES config',
        ),
    ],
)
@pytest.mark.config(TVM_SERVICES={'source_service': 10001})
async def test_modify_queue_400(
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
    response = await web_app_client.put('/queue/modify/', json=data)
    assert response.status == 400
    assert (await response.json())['message'] == expected_text


@pytest.mark.parametrize(
    'data, expected_text',
    [
        (
            {
                'queue_name': 'example_queue',
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
                'state': 'enabled',
                'version': 2,
                'worker_configs': {
                    'max_tasks': 2,
                    'instances': 1,
                    'max_execution_time': 10,
                },
                'write_concern': False,
            },
            'Update failed, possibly version conflict',
        ),
    ],
)
async def test_modify_queue_409(web_app_client, data, expected_text):
    response = await web_app_client.put('/queue/modify/', json=data)
    assert response.status == 409
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
async def test_modify_queue_when_old_shards_exist_400(web_app_client, data):
    response = await web_app_client.put('/queue/modify/check/', json=data)
    assert response.status == 400
    result = await response.json()
    assert (
        result['message']
        == 'At the moment, tasks of this queue are being moved '
        'between databases, database changes are not available'
    )


@util.parametrize_data(
    __file__,
    'test_put_modify_queue_200.json',
    ('data', 'expected_config', 'expected_db_fields'),
)
@pytest.mark.config(
    STQ_DEFAULT_MONITORING_THRESHOLDS={'total': {'warning': 1, 'critical': 5}},
    TVM_SERVICES={
        'source_service': 10001,
        'source_service_1': 10002,
        'source_service_2': 10003,
    },
)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_modify_queue_200(
        web_app_client,
        mock_conductor,
        data,
        expected_config,
        web_context,
        patch_current_date,
        expected_db_fields,
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

    response = await web_app_client.put('/queue/modify/', json=data)
    assert response.status == 200
    for database, fields in expected_db_fields.items():
        config_info = 'stq_config' if database == 'main' else 'stq_meta_data'
        config = getattr(web_context.mongo, config_info)
        doc = await config.find_one({'_id': expected_config['queue_name']})
        for field in fields:
            current_doc = doc
            for current_field in field['path']:
                assert current_field in current_doc
                current_doc = current_doc[current_field]
            assert current_doc == field['value']

    assert await response.json() == expected_config


@pytest.mark.parametrize(
    'data',
    [
        {
            'queue_name': 'queue_to_check_indexes',
            'shards': [
                {
                    'collection': 'queue_to_check_indexes_0',
                    'connection_name': 'stq',
                    'database': 'dbstqorder0',
                    'hostnames': [],
                    'state': 'disabled',
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
async def test_indexes_creation_after_changing_database(
        web_app_client, data, web_context,
):
    response = await web_app_client.put('/queue/modify/', json=data)
    assert response.status == 200
    shard_info = {
        'collection': 'queue_to_check_indexes_0',
        'connection': 'stq',
        'database': 'dbstqorder0',
    }
    stq_mongo = stq_shards.StqMongoWrapper([shard_info], web_context.secdist)
    shard = stq_mongo.get_shard_collection(shard_info)
    assert {
        index['key'].keys()[0] async for index in shard.list_indexes()
    } == {'_id', 'e', 'x', 'f', 'm', 'ff'}
