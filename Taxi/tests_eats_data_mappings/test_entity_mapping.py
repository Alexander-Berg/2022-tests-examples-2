import pytest

from tests_eats_data_mappings import utils


async def test_inaccessible_from_outside(taxi_eats_data_mappings):
    response = await taxi_eats_data_mappings.post(
        '/service/v1/entity_mapping',
        json={
            'first_entity_type': 'eater_id',
            'second_entity_type': 'order_nr',
            'tvm_write': [],
            'tvm_read': [],
            'takeout_policies': [],
        },
    )
    assert response.status_code == 404


async def test_parsing_error(taxi_eats_data_mappings_monitor):
    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping', json={},
    )
    assert response.status_code == 400


@pytest.mark.config(TVM_SERVICES={'some1': 111})
async def test_no_tvm_in_config(
        taxi_eats_data_mappings, taxi_eats_data_mappings_monitor, pgsql,
):
    await taxi_eats_data_mappings.invalidate_caches()

    request_json = {
        'first_entity_type': 'eater_id',
        'second_entity_type': 'order_nr',
        'tvm_write': ['some1', 'some4'],
        'tvm_read': ['some3', 'some4'],
        'takeout_policies': [],
    }

    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping', json=request_json,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'pre_insert, request_json, db_expected',
    [
        pytest.param(
            None,
            {
                'first_entity_type': 'eater_id',
                'second_entity_type': 'order_nr',
                'tvm_write': [],
                'tvm_read': [],
                'takeout_policies': [],
            },
            [
                # this first is added by fixture eater_id_to_yandex_uid_link
                # it always must be exactly one link with yandex_uid
                {
                    'primary_entity_type': 'yandex_uid',
                    'secondary_entity_type': 'eater_id',
                    'tvm_write': set(),
                    'tvm_read': set(),
                    'takeout_policies': '{}',
                },
                {
                    'primary_entity_type': 'eater_id',
                    'secondary_entity_type': 'order_nr',
                    'tvm_write': set(),
                    'tvm_read': set(),
                    'takeout_policies': '{}',
                },
            ],
            id='add single w/o tvm',
        ),
        pytest.param(
            None,
            {
                'first_entity_type': 'eater_id',
                'second_entity_type': 'order_nr',
                'tvm_write': ['some1', 'some2'],
                'tvm_read': ['some3'],
                'takeout_policies': [],
            },
            [
                # this first is added by fixture eater_id_to_yandex_uid_link
                # it always must be exactly one link with yandex_uid
                {
                    'primary_entity_type': 'yandex_uid',
                    'secondary_entity_type': 'eater_id',
                    'tvm_write': set(),
                    'tvm_read': set(),
                    'takeout_policies': '{}',
                },
                {
                    'primary_entity_type': 'eater_id',
                    'secondary_entity_type': 'order_nr',
                    'tvm_write': {111, 222},
                    'tvm_read': {333},
                    'takeout_policies': '{}',
                },
            ],
            id='add single with tvm',
        ),
        pytest.param(
            {
                'first_entity_type': 'eater_id',
                'second_entity_type': 'order_nr',
                'tvm_write': ['some1', 'some2'],
                'tvm_read': ['some3'],
                'takeout_policies': [],
            },
            {
                'first_entity_type': 'eater_id',
                'second_entity_type': 'order_nr',
                'tvm_write': ['some1', 'some4'],
                'tvm_read': ['some3', 'some4'],
                'takeout_policies': [],
            },
            [
                # this first is added by fixture eater_id_to_yandex_uid_link
                # it always must be exactly one link with yandex_uid
                {
                    'primary_entity_type': 'yandex_uid',
                    'secondary_entity_type': 'eater_id',
                    'tvm_write': set(),
                    'tvm_read': set(),
                    'takeout_policies': '{}',
                },
                {
                    'primary_entity_type': 'eater_id',
                    'secondary_entity_type': 'order_nr',
                    'tvm_write': {111, 444},
                    'tvm_read': {333, 444},
                    'takeout_policies': '{}',
                },
            ],
            id='add existing',
        ),
    ],
)
@pytest.mark.config(
    TVM_SERVICES={'some1': 111, 'some2': 222, 'some3': 333, 'some4': 444},
)
@pytest.mark.entity(['order_nr', 'yandex_uid', 'some1', 'some2'])
async def test_add_entity_mapping(
        taxi_eats_data_mappings,
        taxi_eats_data_mappings_monitor,
        pgsql,
        pre_insert,
        request_json,
        db_expected,
        eater_id_to_yandex_uid_link,
):
    await taxi_eats_data_mappings.invalidate_caches()

    if pre_insert:
        response = await taxi_eats_data_mappings_monitor.post(
            '/service/v1/entity_mapping', json=pre_insert,
        )
        assert response.status_code == 200

    response = await taxi_eats_data_mappings_monitor.post(
        '/service/v1/entity_mapping', json=request_json,
    )
    assert response.status_code == 200

    mappings = utils.get_all_entity_mappings_from_db(pgsql)

    assert len(db_expected) == len(mappings)

    for expected in db_expected:
        assert expected in mappings
