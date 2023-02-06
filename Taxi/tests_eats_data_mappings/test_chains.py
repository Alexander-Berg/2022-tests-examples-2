import pytest


async def test_inaccessible_from_outside(taxi_eats_data_mappings):
    response = await taxi_eats_data_mappings.post(
        '/service/v1/chain', json={'name': 'name', 'entities': ['some']},
    )
    assert response.status_code == 404


async def test_parsing_error(taxi_eats_data_mappings_monitor):
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/chain', json={},
    )
    assert response.status_code == 400


CHAINS_TO_WRITE = [
    {'name': 'chain1', 'entities': ['eater_id', 'some1', 'some3']},
    {'name': 'chain2', 'entities': ['yandex_uid', 'eater_id', 'some4']},
    {'name': 'chain3', 'entities': ['some4', 'eater_id', 'yandex_uid']},
]


@pytest.mark.config(TVM_SERVICES={})
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
            'first_entity_type': 'eater_id',
            'second_entity_type': 'some1',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'some1',
            'second_entity_type': 'some3',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'eater_id',
            'second_entity_type': 'some4',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_add_chain_ok(taxi_eats_data_mappings_monitor, get_all_chains):
    for chain in CHAINS_TO_WRITE:
        response = await taxi_eats_data_mappings_monitor.post(
            '/service/v1/chain', json=chain,
        )
        assert response.status_code == 200

    written_chains = get_all_chains()

    assert len(written_chains) == len(CHAINS_TO_WRITE)
    for chain in CHAINS_TO_WRITE:
        assert chain in written_chains


CHAIN_UNKNOWN_ENTITY = {
    'name': 'chain4',
    'entities': ['eater_id', 'some5', 'some1'],
}


@pytest.mark.config(TVM_SERVICES={})
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
            'first_entity_type': 'eater_id',
            'second_entity_type': 'some1',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'some1',
            'second_entity_type': 'some3',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'eater_id',
            'second_entity_type': 'some4',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_add_chain_unknown_entity(
        taxi_eats_data_mappings_monitor, get_all_chains,
):
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/chain', json=CHAIN_UNKNOWN_ENTITY,
    )
    assert response.status_code == 400


@pytest.mark.config(TVM_SERVICES={})
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
            'first_entity_type': 'eater_id',
            'second_entity_type': 'some1',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'some1',
            'second_entity_type': 'some3',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'eater_id',
            'second_entity_type': 'some4',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_add_chain_duplicate(
        taxi_eats_data_mappings_monitor, get_all_chains,
):
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/chain', json=CHAINS_TO_WRITE[0],
    )
    assert response.status_code == 200

    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/chain', json=CHAINS_TO_WRITE[0],
    )
    assert response.status_code == 400


CHAIN_WITH_CYCLE = {
    'name': 'chain5',
    'entities': ['eater_id', 'some1', 'some2', 'some3', 'some1', 'some2'],
}


@pytest.mark.config(TVM_SERVICES={})
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
            'first_entity_type': 'eater_id',
            'second_entity_type': 'some1',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'some1',
            'second_entity_type': 'some2',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'some2',
            'second_entity_type': 'some3',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'some1',
            'second_entity_type': 'some3',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_add_chain_cycle(
        taxi_eats_data_mappings_monitor, get_all_chains,
):
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/chain', json=CHAIN_WITH_CYCLE,
    )
    assert response.status_code == 400


CHAIN_UNKNOWN_MAPPING = {'name': 'chain6', 'entities': ['eater_id', 'some3']}


@pytest.mark.config(TVM_SERVICES={})
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
            'first_entity_type': 'eater_id',
            'second_entity_type': 'some1',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'some1',
            'second_entity_type': 'some3',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'eater_id',
            'second_entity_type': 'some4',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_add_chain_unknown_mapping(
        taxi_eats_data_mappings_monitor, get_all_chains,
):
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/chain', json=CHAIN_UNKNOWN_MAPPING,
    )
    assert response.status_code == 400
