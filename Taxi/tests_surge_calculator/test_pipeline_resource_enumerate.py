# pylint: disable=E1101,W0612
import collections

import pytest  # noqa: F401

INVALID_CONSUMER_ERROR_CODE = 'invalid_consumer'

ResourceDesc = collections.namedtuple(
    'ResourceDesc', 'name instance_schema params_schema',
)


def _name_sorter(resource_desc):
    return resource_desc.name


EXPECTED_RESPONSE = sorted(
    [
        ResourceDesc('count_by_categories', True, True),
        ResourceDesc('free_drivers_graph', True, True),
        ResourceDesc('pin_stats', True, True),
        ResourceDesc('subventions', True, True),
        ResourceDesc('surge_value_map', True, True),
        ResourceDesc('surge_map', True, True),
        ResourceDesc('time', True, True),
        ResourceDesc('zone', True, False),
        ResourceDesc('config', True, False),
        ResourceDesc('experiments3', True, False),
        ResourceDesc('surge_statistics', True, True),
        ResourceDesc('dynamic_config', True, False),
        ResourceDesc('airport_queue', True, True),
        ResourceDesc('nearest_point', True, True),
        ResourceDesc('nearest_points', True, True),
        ResourceDesc('surge_value_polygon_map', True, True),
        ResourceDesc('surge_value_graph_map', True, True),
    ],
    key=_name_sorter,
)


def collect_short_description(data):
    result = []
    for element in data:
        has_instance = 'instance_schema' in element
        has_params = 'params_schema' in element
        result.append(ResourceDesc(element['name'], has_instance, has_params))
    result.sort(key=_name_sorter)
    return result


async def test_resource_enumerate(taxi_surge_calculator):
    response = await taxi_surge_calculator.get(
        'v1/js/pipeline/resource/enumerate',
    )
    assert response.status_code == 200
    data = response.json()

    assert collect_short_description(data) == EXPECTED_RESPONSE


async def test_unknown_consumer(taxi_surge_calculator):
    response = await taxi_surge_calculator.get(
        'v1/js/pipeline/resource/enumerate',
        params={'consumer': 'something-not-existing'},
    )
    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == INVALID_CONSUMER_ERROR_CODE


async def test_valid_consumer(taxi_surge_calculator):
    response = await taxi_surge_calculator.get(
        'v1/js/pipeline/resource/enumerate', params={'consumer': 'taxi-surge'},
    )
    assert response.status_code == 200

    data = response.json()
    assert collect_short_description(data) == EXPECTED_RESPONSE
