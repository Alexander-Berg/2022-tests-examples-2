import pytest


from tests_eats_data_mappings import utils


async def test_unknown_types(taxi_eats_data_mappings_monitor):
    # unknown types
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'yandex_uid',
            'second_entity_type': 'order_nr',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    )
    assert response.status_code == 400


@pytest.mark.entity(['eater_id', 'order_nr', 'yandex_uid'])
async def test_yandex_uid_is_necessary(taxi_eats_data_mappings_monitor):
    # `yandex_uid` should be first
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'eater_id',
            'second_entity_type': 'order_nr',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    )
    assert response.status_code == 400

    # link with yandex_uid` - OK
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'yandex_uid',
            'second_entity_type': 'order_nr',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    )
    assert response.status_code == 200


@pytest.mark.entity(['eater_id', 'order_nr', 'yandex_uid'])
async def test_double_yandex_uid(taxi_eats_data_mappings_monitor):
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'yandex_uid',
            'second_entity_type': 'order_nr',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    )
    assert response.status_code == 200

    # check if same if allowed
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'yandex_uid',
            'second_entity_type': 'order_nr',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    )
    assert response.status_code == 200

    # check if second link with yandex_uid is not allowed
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
    assert response.status_code == 400

    # check that order matters
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'order_nr',
            'second_entity_type': 'yandex_uid',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    )
    assert response.status_code == 400


@pytest.mark.entity(['eater_id', 'order_nr', 'yandex_uid'])
async def test_order_matters(
        taxi_eats_data_mappings_monitor, eater_id_to_yandex_uid_link,
):
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'eater_id',
            'second_entity_type': 'order_nr',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    )
    assert response.status_code == 200

    # check if same if allowed
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'eater_id',
            'second_entity_type': 'order_nr',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    )
    assert response.status_code == 200

    # check that order matters
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'order_nr',
            'second_entity_type': 'eater_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    )
    assert response.status_code == 400


@pytest.mark.entity(['eater_id'])
async def test_equal_entity_types(
        taxi_eats_data_mappings_monitor, eater_id_to_yandex_uid_link,
):
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'eater_id',
            'second_entity_type': 'eater_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    )
    assert response.status_code == 400


@pytest.mark.entity(['eater_id', 'order_nr', 'yandex_uid', 'cart_id'])
@pytest.mark.takeout_policies(['policy1', 'policy2', 'policy3'])
@pytest.mark.takeout_chains(
    [
        {'name': 'chain1', 'entities': ['yandex_uid', 'eater_id', 'order_nr']},
        {
            'name': 'chain2',
            'entities': ['yandex_uid', 'eater_id', 'order_nr', 'cart_id'],
        },
    ],
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
            'second_entity_type': 'order_nr',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'order_nr',
            'second_entity_type': 'cart_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_takeout_policy_values(
        taxi_eats_data_mappings_monitor, eater_id_to_yandex_uid_link,
):
    # check that takeout_policy should present,
    # but takeout_chain name can be absent or be any value
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'eater_id',
            'second_entity_type': 'order_nr',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [
                {'takeout_policy': 'policy1'},
                {'takeout_policy': 'policy2', 'takeout_chain': ''},
                {'takeout_policy': 'policy3', 'takeout_chain': 'chain1'},
            ],
        },
    )
    assert response.status_code == 200

    # check that takeout_policy cannot be absent
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'eater_id',
            'second_entity_type': 'order_nr',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [{'takeout_chain': 'chain1'}],
        },
    )
    assert response.status_code == 400

    # check that takeout_policy cannot be empty string
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'eater_id',
            'second_entity_type': 'order_nr',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [
                {'takeout_policy': '', 'takeout_chain': 'chain1'},
            ],
        },
    )
    assert response.status_code == 400


@pytest.mark.config(TVM_SERVICES={'some1': 111})
@pytest.mark.entity(['order_nr', 'yandex_uid'])
async def test_same_with_yandex_uid(
        taxi_eats_data_mappings, taxi_eats_data_mappings_monitor, pgsql,
):
    await taxi_eats_data_mappings.invalidate_caches()

    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'yandex_uid',
            'second_entity_type': 'order_nr',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    )
    assert response.status_code == 200

    # check if same if allowed
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'yandex_uid',
            'second_entity_type': 'order_nr',
            'tvm_write': ['some1'],
            'tvm_read': ['some1'],
            'takeout_policies': [],
        },
    )
    assert response.status_code == 200

    mappings = utils.get_all_entity_mappings_from_db(pgsql)

    assert len(mappings) == 1
    assert mappings[0] == {
        'primary_entity_type': 'yandex_uid',
        'secondary_entity_type': 'order_nr',
        'tvm_write': {111},
        'tvm_read': {111},
        'takeout_policies': '{}',
    }


@pytest.mark.entity(
    [
        'eater_id',
        'order_nr',
        'yandex_uid',
        'cart_id',
        'address_id',
        'personal_phone_id',
    ],
)
@pytest.mark.takeout_policies(['policy1', 'policy2', 'policy3'])
@pytest.mark.takeout_chains(
    [
        {'name': 'chain1', 'entities': ['yandex_uid', 'eater_id', 'order_nr']},
        {
            'name': 'chain2',
            'entities': ['yandex_uid', 'eater_id', 'order_nr', 'cart_id'],
        },
    ],
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
            'second_entity_type': 'order_nr',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'order_nr',
            'second_entity_type': 'cart_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'order_nr',
            'second_entity_type': 'address_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'order_nr',
            'second_entity_type': 'personal_phone_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_takeout_policy_without_chain(
        taxi_eats_data_mappings_monitor, eater_id_to_yandex_uid_link,
):
    # first_entity_type or second_entity_type should be connected
    # with 'yandex_uid' when takeout_chain absent/empty
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'eater_id',
            'second_entity_type': 'order_nr',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [
                {'takeout_policy': 'policy1'},
                {'takeout_policy': 'policy2', 'takeout_chain': ''},
            ],
        },
    )
    assert response.status_code == 200

    # first_entity_type or second_entity_type should be 'yandex_uid'
    # when takeout_chain absent/empty
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'yandex_uid',
            'second_entity_type': 'eater_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [
                {'takeout_policy': 'policy1'},
                {'takeout_policy': 'policy2', 'takeout_chain': ''},
            ],
        },
    )
    assert response.status_code == 200

    # no connection with 'yandex_uid' when takeout_chain absent/empty
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'order_nr',
            'second_entity_type': 'personal_phone_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [
                {'takeout_policy': 'policy1'},
                {'takeout_policy': 'policy2', 'takeout_chain': ''},
            ],
        },
    )
    assert response.status_code == 400


@pytest.mark.entity(
    [
        'eater_id',
        'order_nr',
        'yandex_uid',
        'cart_id',
        'address_id',
        'personal_phone_id',
    ],
)
@pytest.mark.takeout_policies(['policy1', 'policy2', 'policy3'])
@pytest.mark.takeout_chains(
    [
        {'name': 'chain1', 'entities': ['yandex_uid', 'eater_id', 'order_nr']},
        {
            'name': 'chain2',
            'entities': ['yandex_uid', 'eater_id', 'order_nr', 'cart_id'],
        },
        {'name': 'chain3', 'entities': ['eater_id', 'order_nr', 'cart_id']},
    ],
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
            'second_entity_type': 'order_nr',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'order_nr',
            'second_entity_type': 'cart_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'order_nr',
            'second_entity_type': 'address_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
        {
            'first_entity_type': 'order_nr',
            'second_entity_type': 'personal_phone_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    ],
)
async def test_takeout_policy_with_chain(
        taxi_eats_data_mappings_monitor, eater_id_to_yandex_uid_link,
):
    # cannot to connect first_entity_type or second_entity_type with chain1
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'cart_id',
            'second_entity_type': 'personal_phone_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [
                {'takeout_policy': 'policy1', 'takeout_chain': 'chain1'},
            ],
        },
    )
    assert response.status_code == 400

    # chain3 should starts with 'yandex_uid'
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'cart_id',
            'second_entity_type': 'personal_phone_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [
                {'takeout_policy': 'policy1', 'takeout_chain': 'chain3'},
            ],
        },
    )
    assert response.status_code == 400

    # Unknown chain name 'chain4'
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'cart_id',
            'second_entity_type': 'personal_phone_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [
                {'takeout_policy': 'policy1', 'takeout_chain': 'chain4'},
            ],
        },
    )
    assert response.status_code == 400

    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'order_nr',
            'second_entity_type': 'cart_id',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [
                {'takeout_policy': 'policy1', 'takeout_chain': 'chain1'},
                {'takeout_policy': 'policy2', 'takeout_chain': 'chain2'},
            ],
        },
    )
    assert response.status_code == 200
