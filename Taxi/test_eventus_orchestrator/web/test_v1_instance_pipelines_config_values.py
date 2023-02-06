# flake8: noqa: E501
import pytest

from eventus_orchestrator_fbs.fbs.v1_instance_pipelines_config_values_response import (
    InstancePipelinesConfigValuesResponse,
)
from taxi.util import hash as hash_util

import eventus_orchestrator.common.configuration.remove_named_groups as remove_named_groups
import eventus_orchestrator.generated.service.swagger.models.api as gen_api
from . import fbs_to_json
from .. import pipeline_tools

ResponseClass = (
    InstancePipelinesConfigValuesResponse.InstancePipelinesConfigValuesResponse
)

URI = '/v1/instance/pipelines/config/values'


async def _parse_response(response):
    data = ResponseClass.GetRootAsInstancePipelinesConfigValuesResponse(
        bytearray(await response.read()), 0,
    )

    return fbs_to_json.fbs_instance_pipelines_to_json(data)


async def _make_request_and_get_result(
        taxi_eventus_orchestrator_web, cursor=None,
):
    req_json = {'host': {'name': 'asd', 'instance': 'order-events-producer'}}
    if cursor is not None:
        req_json['cursor'] = cursor
    response = await taxi_eventus_orchestrator_web.post(URI, json=req_json)
    assert response.status == 200
    json_resp = await _parse_response(response)
    return json_resp, json_resp['cursor']


def _add_default_policy_action(policy):
    if 'action_after_erroneous_execution' not in policy:
        policy['action_after_erroneous_execution'] = 'propagate'


def _add_disabled(config):
    if 'root' in config or 'operation_variant' in config:
        if 'is_disabled' not in config:
            config['is_disabled'] = False


def _add_number_of_threads(config):
    if 'root' in config:
        if 'number_of_threads' not in config:
            config['number_of_threads'] = 3


def _add_empty_args(config):
    if 'operation_name' in config and 'options' not in config:
        if 'arguments' not in config:
            config['arguments'] = {}

    if 'sink_name' in config:
        if 'arguments' not in config:
            config['arguments'] = {}

    if 'options' in config:
        for opt in config['options']:
            if 'arguments' not in opt:
                opt['arguments'] = {}

    if 'source' in config:
        if 'arguments' not in config['source']:
            config['source']['arguments'] = {}


def _add_default_fields_and_fix_args(config):
    if isinstance(config, list):
        for elem in config:
            _add_default_fields_and_fix_args(elem)
    elif isinstance(config, dict):
        _add_disabled(config)
        _add_number_of_threads(config)
        _add_empty_args(config)

        for key, val in config.items():
            if key == 'error_handling_policy':
                _add_default_policy_action(val)
            else:
                _add_default_fields_and_fix_args(val)


async def test_v1_instance_pipelines_config_values(
        taxi_eventus_orchestrator_web, load_json,
):
    json_resp, _ = await _make_request_and_get_result(
        taxi_eventus_orchestrator_web,
    )

    exp_cursor = str(
        hash_util.fnv0_64(
            'communal-events=aasdasdthr6r6ryry,order-events=asdasse545t5',
        ),
    )
    expected_result = {'cursor': exp_cursor, 'pipelines': []}
    json_for_mongo = load_json('db_eventus_pipelines.json')
    for pipeline_info in json_for_mongo:
        if pipeline_info['instance'] != 'order-events-producer':
            continue

        if not pipeline_info['versions']:
            continue

        name = pipeline_info['pipeline']
        pipeline_json = pipeline_info['versions'][-1]['pipeline']
        pipeline = gen_api.PipelineConfiguration.deserialize(pipeline_json)
        remove_named_groups.remove_named_groups(pipeline)
        ser_pipeline = pipeline.serialize()
        ser_pipeline['name'] = name
        if 'st_ticket' in ser_pipeline:
            del ser_pipeline['st_ticket']
        if 'description' in ser_pipeline:
            del ser_pipeline['description']
        _add_default_fields_and_fix_args(ser_pipeline)
        expected_result['pipelines'].append(ser_pipeline)

    json_resp['pipelines'].sort(key=lambda p: p['name'])
    expected_result['pipelines'].sort(key=lambda p: p['name'])

    assert json_resp == expected_result


async def _put_pipeline(
        taxi_eventus_orchestrator_web,
        i,
        description,
        ticket,
        number_of_threads=None,
):
    await pipeline_tools.update_schema_for_test(
        i, taxi_eventus_orchestrator_web,
    )

    pipeline_json = {
        'new_value': {
            'description': description,
            'st_ticket': ticket,
            'is_disabled': False,
            'source': {'name': f'source_name_{i}', 'arguments': {}},
            'root': {
                'sink_name': f'sink_{i}',
                'arguments': {},
                'error_handling_policy': {
                    'action_after_erroneous_execution': 'propagate',
                    'retry_policy': {
                        'attempts': 1,
                        'min_delay_ms': 1,
                        'max_delay_ms': 10,
                        'delay_factor': 1,
                    },
                },
            },
        },
        'for_prestable': False,
        'action': 'update',
    }

    if number_of_threads is not None:
        pipeline_json['new_value']['number_of_threads'] = number_of_threads

    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/update',
        params={
            'instance_name': 'order-events-producer',
            'pipeline_name': 'order-events',
        },
        json=pipeline_json,
        headers={'X-YaTaxi-Draft-Id': 'draft_id'},
    )

    assert response.status == 200


async def _rename_pipeline(
        taxi_eventus_orchestrator_web, current_name, new_name,
):
    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/rename',
        params={
            'instance_name': 'order-events-producer',
            'pipeline_name': current_name,
        },
        json={'new_name': new_name},
        headers={'X-YaTaxi-Draft-Id': 'draft_id'},
    )

    assert response.status == 200


async def test_v1_pipelines_config_values_with_put(
        taxi_eventus_orchestrator_web, load_json,
):
    json_resp, cursor = await _make_request_and_get_result(
        taxi_eventus_orchestrator_web,
    )
    assert len(json_resp['pipelines']) == 2

    for i in range(3):
        json_resp, cursor = await _make_request_and_get_result(
            taxi_eventus_orchestrator_web, cursor,
        )
        assert not json_resp['pipelines']
        assert json_resp['cursor'] == cursor

    await _put_pipeline(taxi_eventus_orchestrator_web, 0, 'asad', 'asdaw')

    json_resp, cursor = await _make_request_and_get_result(
        taxi_eventus_orchestrator_web, cursor,
    )
    assert len(json_resp['pipelines']) == 2

    await _put_pipeline(taxi_eventus_orchestrator_web, 0, 'asddddd', '45rth')
    json_resp, cursor = await _make_request_and_get_result(
        taxi_eventus_orchestrator_web, cursor,
    )
    assert not json_resp['pipelines']

    for i in range(5, 8):
        await _put_pipeline(
            taxi_eventus_orchestrator_web, i, 'asddddd', '45rth',
        )
        json_resp, cursor = await _make_request_and_get_result(
            taxi_eventus_orchestrator_web, cursor,
        )
        assert len(json_resp['pipelines']) == 2

    json_resp, cursor = await _make_request_and_get_result(
        taxi_eventus_orchestrator_web, cursor,
    )
    assert not json_resp['pipelines']

    await _rename_pipeline(
        taxi_eventus_orchestrator_web, 'order-events', 'order-events-0',
    )
    json_resp, cursor = await _make_request_and_get_result(
        taxi_eventus_orchestrator_web, cursor,
    )
    assert len(json_resp['pipelines']) == 2

    for i in range(2):
        await _rename_pipeline(
            taxi_eventus_orchestrator_web,
            f'order-events-{i}',
            f'order-events-{i+1}',
        )
        json_resp, cursor = await _make_request_and_get_result(
            taxi_eventus_orchestrator_web, cursor,
        )
        assert len(json_resp['pipelines']) == 2

    json_resp, cursor = await _make_request_and_get_result(
        taxi_eventus_orchestrator_web, cursor,
    )
    assert not json_resp['pipelines']


@pytest.mark.parametrize('number_of_threads', [1, 3, 5, 7, 100])
async def test_config_values_with_put_number_of_threads(
        taxi_eventus_orchestrator_web, number_of_threads,
):
    await _put_pipeline(
        taxi_eventus_orchestrator_web, 0, 'asad', 'asdaw', number_of_threads,
    )
    json_resp, _ = await _make_request_and_get_result(
        taxi_eventus_orchestrator_web,
    )
    order_events = None
    for pipeline in json_resp['pipelines']:
        if pipeline['name'] == 'order-events':
            order_events = pipeline

    assert order_events['number_of_threads'] == number_of_threads
