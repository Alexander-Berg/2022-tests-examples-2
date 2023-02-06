import pytest


ENTITIES = {'entities': ['some1', 'some2', 'some3', 'some4']}

MAPPINGS = [
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
]

CHAINS = [
    {'name': 'chain1', 'entities': ['some1', 'some2', 'some3']},
    {'name': 'chain2', 'entities': ['some4', 'some2', 'some1']},
]

POLICIES = {'takeout_policies': ['policy1', 'policy2', 'policy3', 'policy4']}

EXPECTED = {
    'entities': {'some1', 'some2', 'some3', 'some4', 'yandex_uid', 'eater_id'},
    'entity_mappings': [
        # this first is added by fixture eater_id_to_yandex_uid_link
        # it always should be exactly one link with yandex_uid
        {
            'first_entity_type': 'yandex_uid',
            'second_entity_type': 'eater_id',
            'tvm_write': set(),
            'tvm_read': set(),
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'some1',
            'second_entity_type': 'some2',
            'tvm_write': {'service1'},
            'tvm_read': {'service1', 'service2'},
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'some2',
            'second_entity_type': 'some3',
            'tvm_write': {'service2'},
            'tvm_read': {'service2', 'service3'},
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'some2',
            'second_entity_type': 'some4',
            'tvm_write': {'service1', 'service2', 'service3'},
            'tvm_read': {'service1', 'service2', 'service3', 'service4'},
            'takeout_policies': [],
        },
    ],
    'chains': [
        {'name': 'chain1', 'entities': ['some1', 'some2', 'some3']},
        {'name': 'chain2', 'entities': ['some4', 'some2', 'some1']},
    ],
    'takeout_policies': {'policy1', 'policy2', 'policy3', 'policy4'},
}


def change_arrays_into_sets(json):
    entity_mappings = json['entity_mappings']
    for mapping in entity_mappings:
        mapping['tvm_write'] = set(mapping['tvm_write'])
        mapping['tvm_read'] = set(mapping['tvm_read'])

    json['entities'] = set(json['entities'])

    return json


@pytest.mark.config(
    TVM_SERVICES={
        'service1': 111,
        'service2': 222,
        'service3': 333,
        'service4': 444,
    },
)
async def test_settings_list(
        taxi_eats_data_mappings,
        taxi_eats_data_mappings_monitor,
        eater_id_to_yandex_uid_link,
):
    await taxi_eats_data_mappings.invalidate_caches()

    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entities', json=ENTITIES,
    )
    assert response.status_code == 200

    for mapping in MAPPINGS:
        response = await taxi_eats_data_mappings_monitor.post(
            '/service/v1/entity_mapping', json=mapping,
        )
        assert response.status_code == 200

    for chain in CHAINS:
        response = await taxi_eats_data_mappings_monitor.post(
            '/service/v1/chain', json=chain,
        )
        assert response.status_code == 200

    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/takeout_policies', json=POLICIES,
    )
    assert response.status_code == 200

    response = await taxi_eats_data_mappings.get('/service/v1/settings')
    assert response.status_code == 200

    response = change_arrays_into_sets(response.json())
    assert set(response.keys()) == set(EXPECTED.keys())

    assert sorted(response['entities']) == sorted(EXPECTED['entities'])

    assert len(response['entity_mappings']) == len(EXPECTED['entity_mappings'])
    for mapping in EXPECTED['entity_mappings']:
        assert mapping in response['entity_mappings']

    assert len(response['chains']) == len(EXPECTED['chains'])
    for mapping in EXPECTED['chains']:
        assert mapping in response['chains']

    assert sorted(response['takeout_policies']) == sorted(
        EXPECTED['takeout_policies'],
    )
