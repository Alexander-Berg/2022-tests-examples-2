import copy
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_data_mappings_plugins import *  # noqa: F403 F401

EXTRA_ENTITIES = ['yandex_uid', 'eater_id', 'a', 'b', 'c', 'd', 'e', 'f', 'g']
EXTRA_MAPPINGS = [
    {
        'first_entity_type': 'yandex_uid',
        'second_entity_type': 'eater_id',
        'tvm_write': [],
        'tvm_read': [],
        'takeout_policies': [],
    },
    {
        'first_entity_type': 'eater_id',
        'second_entity_type': 'a',
        'tvm_write': [],
        'tvm_read': [],
        'takeout_policies': [],
    },
    {
        'first_entity_type': 'a',
        'second_entity_type': 'b',
        'tvm_write': [],
        'tvm_read': [],
        'takeout_policies': [],
    },
    {
        'first_entity_type': 'b',
        'second_entity_type': 'c',
        'tvm_write': [],
        'tvm_read': [],
        'takeout_policies': [
            {'takeout_policy': 'all', 'takeout_chain': 'chain1'},
        ],
    },
    {
        'first_entity_type': 'c',
        'second_entity_type': 'e',
        'tvm_write': [],
        'tvm_read': [],
        'takeout_policies': [],
    },
    {
        'first_entity_type': 'c',
        'second_entity_type': 'g',
        'tvm_write': [],
        'tvm_read': [],
        'takeout_policies': [
            {'takeout_policy': 'all', 'takeout_chain': 'chain2'},
        ],
    },
    {
        'first_entity_type': 'eater_id',
        'second_entity_type': 'f',
        'tvm_write': [],
        'tvm_read': [],
        'takeout_policies': [
            {'takeout_policy': 'orders', 'takeout_chain': ''},
        ],
    },
    {
        'first_entity_type': 'd',
        'second_entity_type': 'b',
        'tvm_write': [],
        'tvm_read': [],
        'takeout_policies': [
            {'takeout_policy': 'orders', 'takeout_chain': 'chain1'},
        ],
    },
]
EXTRA_TAKEOUT_POLICIES = ['all', 'orders']
EXTRA_TAKEOUT_CHAINS = [
    {'name': 'chain1', 'entities': ['yandex_uid', 'eater_id', 'a', 'b']},
    {'name': 'chain2', 'entities': ['yandex_uid', 'eater_id', 'a', 'b', 'c']},
]


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'entity(list): mark test to add entities',
    )
    config.addinivalue_line(
        'markers', 'mappings(list): mark test to add mappings',
    )
    config.addinivalue_line(
        'markers', 'takeout_policies(list): mark test to add takeout policies',
    )
    config.addinivalue_line(
        'markers', 'takeout_chains(list): mark test to add takeout chains',
    )
    config.addinivalue_line(
        'markers',
        'add_extra_settings: mark test to add extra entity settings',
    )


# This fixture is triggered before each test (autouse=True). You can use the markers
# described above to configure your tests.
# The mark 'add_extra_settings' adds following configuration:
#
#                     f                 d
#                     |                 |
#                     | orders          | orders
#                     |                 |
#  yandex_uid ---- eater_id ---- a ---- b ------- c ---- e
#                                           all   |
#                                                 | all
#                                                 |
#                                                 g


@pytest.fixture(autouse=True, scope='function')
async def put_entity_settings(
        request, taxi_eats_data_mappings, taxi_eats_data_mappings_monitor,
):
    entities = []
    mappings = []
    takeout_policies = []
    takeout_chains = []
    if request.node.get_closest_marker('add_extra_settings'):
        entities = EXTRA_ENTITIES
        mappings = EXTRA_MAPPINGS
        takeout_policies = EXTRA_TAKEOUT_POLICIES
        takeout_chains = EXTRA_TAKEOUT_CHAINS

    await taxi_eats_data_mappings.invalidate_caches()
    for mark in request.node.iter_markers('entity'):
        entities.extend(mark.args[0])

    if entities:
        response = await taxi_eats_data_mappings_monitor.post(
            '/service/v1/entities', json={'entities': entities},
        )
        assert response.status_code == 200

    for mark in request.node.iter_markers('takeout_policies'):
        takeout_policies.extend(mark.args[0])

    if takeout_policies:
        response = await taxi_eats_data_mappings_monitor.post(
            '/service/v1/takeout_policies',
            json={'takeout_policies': takeout_policies},
        )
        assert response.status_code == 200

    for mark in request.node.iter_markers('mappings'):
        mappings.extend(mark.args[0])
    mappings_without_takeout_policies = copy.deepcopy(mappings)

    for policy in mappings_without_takeout_policies:
        policy['takeout_policies'] = []

    # Add EntityMappings without takeout policies due to possible
    # conflict with takeout chains, adding a chain requires a
    # connected path between the first and last elements in the chain
    for mark in mappings_without_takeout_policies:
        response = await taxi_eats_data_mappings_monitor.post(
            '/service/v1/entity_mapping', json=mark,
        )
        assert response.status_code == 200

    for mark in request.node.iter_markers('takeout_chains'):
        takeout_chains.extend(mark.args[0])

    for mark in takeout_chains:
        response = await taxi_eats_data_mappings_monitor.post(
            '/service/v1/chain', json=mark,
        )
        assert response.status_code == 200

    # Add original EntityMappings (with takeout policies)
    for mark in mappings:
        response = await taxi_eats_data_mappings_monitor.post(
            '/service/v1/entity_mapping', json=mark,
        )
        assert response.status_code == 200

    await taxi_eats_data_mappings.invalidate_caches()


@pytest.fixture
async def eater_id_to_yandex_uid_link(
        request, taxi_eats_data_mappings_monitor,
):
    # put types
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entities', json={'entities': ['eater_id', 'yandex_uid']},
    )
    assert response.status_code == 200

    # put `yandex_uid` - `eater_id` link
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'yandex_uid',
            'second_entity_type': 'eater_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    )
    assert response.status_code == 200
