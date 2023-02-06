import json
import logging

import pytest

CACHE_NAME = 'entity-mappings-cache'

EXPECTED = [
    {
        'primary_entity_type': 'yandex_uid',
        'secondary_entity_type': 'eater_id',
        'tvm_write': [],
        'tvm_read': [],
    },
    {
        'primary_entity_type': 'some1',
        'secondary_entity_type': 'some2',
        'tvm_write': [111],
        'tvm_read': [111, 222],
    },
    {
        'primary_entity_type': 'some2',
        'secondary_entity_type': 'some3',
        'tvm_write': [222],
        'tvm_read': [222, 333],
    },
    {
        'primary_entity_type': 'some2',
        'secondary_entity_type': 'some4',
        'tvm_write': [111, 222, 333],
        'tvm_read': [111, 222, 333, 444],
    },
]


def compare_sorted_mappings(list1, list2):
    list1.sort(key=json.dumps)
    list2.sort(key=json.dumps)
    return list1 == list2


@pytest.mark.config(
    TVM_SERVICES={
        'service1': 111,
        'service2': 222,
        'service3': 333,
        'service4': 444,
    },
)
@pytest.mark.entity(
    ['yandex_uid', 'eater_id', 'some1', 'some2', 'some3', 'some4'],
)
@pytest.mark.mappings(
    [
        {
            'first_entity_type': 'yandex_uid',
            'second_entity_type': 'eater_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'some1',
            'second_entity_type': 'some2',
            'tvm_write': ['service1'],
            'tvm_read': ['service1', 'service2'],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'some2',
            'second_entity_type': 'some3',
            'tvm_write': ['service2'],
            'tvm_read': ['service2', 'service3'],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'some2',
            'second_entity_type': 'some4',
            'tvm_write': ['service1', 'service2', 'service3'],
            'tvm_read': ['service1', 'service2', 'service3', 'service4'],
            'takeout_policies': [],
        },
    ],
)
async def test_entity_mappings_cache(
        taxi_eats_data_mappings, taxi_eats_data_mappings_monitor, testpoint,
):
    @testpoint('get_entity_mappings_cache')
    def get_entity_mappings_cache_tp(data):
        pass

    response = await taxi_eats_data_mappings.get('/service/v1/settings')
    assert response.status_code == 200

    cache = await get_entity_mappings_cache_tp.wait_call()
    logging.info(
        'cache data: %s', json.dumps(list(cache['data'].values()), indent=4),
    )
    logging.info('expected data: %s', json.dumps(EXPECTED, indent=4))
    assert compare_sorted_mappings(list(cache['data'].values()), EXPECTED)
