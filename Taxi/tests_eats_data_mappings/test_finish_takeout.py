import pytest

from pprint import pprint

TAKEOUTS = [
    {
        'takeout_id': 111,
        'request_id': 'id1',
        'takeout_policy': 'all',
        'yandex_uid': 'uid1',
        'status': 'ready_to_takeout',
    },
]

TASKS = [
    {
        'id': 1,
        'task_type': 'finish_takeout',
        'done': False,
        'takeout_id': 111,
        'mapping_id': 'NULL',
    },
]

PAIRS = [
    {
        'id': 1,
        'primary_entity_type': 'yandex_uid',
        'primary_entity_value': 'uid1',
        'secondary_entity_type': 'eater_id',
        'secondary_entity_value': 'id1',
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'id': 2,
        'primary_entity_type': 'eater_id',
        'primary_entity_value': 'id1',
        'secondary_entity_type': 'type6',
        'secondary_entity_value': 'value6',
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'id': 3,
        'primary_entity_type': 'eater_id',
        'primary_entity_value': 'id1',
        'secondary_entity_type': 'type1',
        'secondary_entity_value': 'value1',
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'id': 4,
        'primary_entity_type': 'type1',
        'primary_entity_value': 'value1',
        'secondary_entity_type': 'type2',
        'secondary_entity_value': 'value2',
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'id': 5,
        'primary_entity_type': 'type4',
        'primary_entity_value': 'value4',
        'secondary_entity_type': 'type2',
        'secondary_entity_value': 'value2',
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'id': 6,
        'primary_entity_type': 'type2',
        'primary_entity_value': 'value2',
        'secondary_entity_type': 'type3',
        'secondary_entity_value': 'value3',
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'id': 7,
        'primary_entity_type': 'type3',
        'primary_entity_value': 'value3',
        'secondary_entity_type': 'type5',
        'secondary_entity_value': 'value5',
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'id': 8,
        'primary_entity_type': 'type3',
        'primary_entity_value': 'value3',
        'secondary_entity_type': 'type7',
        'secondary_entity_value': 'value7',
        'created_at': '2022-07-01 12:00:00+03:00',
    },
]

TAKEOUT_DATA = [
    {
        'takeout_id': 111,
        'mapping_id': 1,
        'target_link': False,
        'primary_type': 'yandex_uid',
        'primary_value': 'uid1',
        'secondary_type': 'eater_id',
        'secondary_value': 'id1',
        'real_id': 1,
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'takeout_id': 111,
        'mapping_id': 2,
        'target_link': False,
        'primary_type': 'eater_id',
        'primary_value': 'id1',
        'secondary_type': 'type1',
        'secondary_value': 'value1',
        'real_id': 3,
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'takeout_id': 111,
        'mapping_id': 3,
        'target_link': True,
        'primary_type': 'eater_id',
        'primary_value': 'id1',
        'secondary_type': 'type6',
        'secondary_value': 'value6',
        'real_id': 2,
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'takeout_id': 111,
        'mapping_id': 4,
        'target_link': False,
        'primary_type': 'type1',
        'primary_value': 'value1',
        'secondary_type': 'type2',
        'secondary_value': 'value2',
        'real_id': 4,
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'takeout_id': 111,
        'mapping_id': 5,
        'target_link': True,
        'primary_type': 'type4',
        'primary_value': 'value4',
        'secondary_type': 'type2',
        'secondary_value': 'value2',
        'real_id': 5,
        'created_at': '2022-07-01 12:00:00+03:00',
    },
]

EXPECTED_DELETED_PAIRS = [
    ['eater_id', 'id1', 'type6', 'value6'],
    ['type4', 'value4', 'type2', 'value2'],
]


async def test_finish_takeout(
        taxi_eats_data_mappings,
        get_cursor,
        insert_pairs_with_id,
        insert_takeouts,
        insert_tasks,
        insert_takeout_data,
):
    insert_pairs_with_id(PAIRS)
    insert_takeouts(TAKEOUTS)
    insert_tasks(TASKS)
    insert_takeout_data(TAKEOUT_DATA)

    await taxi_eats_data_mappings.run_task('takeout-task')

    cursor = get_cursor()
    query = (
        'SELECT primary_entity_type, primary_entity_value, '
        'secondary_entity_type, secondary_entity_value FROM '
        'eats_data_mappings.entity_pairs WHERE deleted_at '
        'IS NOT NULL'
    )
    cursor.execute(query)

    deleted_pairs = list(cursor)
    assert len(deleted_pairs) == len(EXPECTED_DELETED_PAIRS)
    for pair in EXPECTED_DELETED_PAIRS:
        assert pair in deleted_pairs

    query = (
        'SELECT status FROM eats_data_mappings.takeout '
        'WHERE takeout_id = {0}'
    ).format(TASKS[0]['takeout_id'])
    cursor.execute(query)
    takeouts = list(cursor)
    assert len(takeouts) == 1
    assert takeouts[0][0] == 'finished'


PAIRS_REDUCED = [
    {
        'id': 1,
        'primary_entity_type': 'yandex_uid',
        'primary_entity_value': 'uid1',
        'secondary_entity_type': 'eater_id',
        'secondary_entity_value': 'id1',
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'id': 3,
        'primary_entity_type': 'eater_id',
        'primary_entity_value': 'id1',
        'secondary_entity_type': 'type1',
        'secondary_entity_value': 'value1',
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'id': 4,
        'primary_entity_type': 'type1',
        'primary_entity_value': 'value1',
        'secondary_entity_type': 'type2',
        'secondary_entity_value': 'value2',
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'id': 6,
        'primary_entity_type': 'type2',
        'primary_entity_value': 'value2',
        'secondary_entity_type': 'type3',
        'secondary_entity_value': 'value3',
        'created_at': '2022-07-01 12:00:00+03:00',
    },
]


async def test_finish_takeout_pairs_are_not_in_table(
        taxi_eats_data_mappings,
        get_cursor,
        insert_pairs_with_id,
        insert_takeouts,
        insert_tasks,
        insert_takeout_data,
):
    insert_pairs_with_id(PAIRS_REDUCED)
    insert_takeouts(TAKEOUTS)
    insert_tasks(TASKS)
    insert_takeout_data(TAKEOUT_DATA)

    await taxi_eats_data_mappings.run_task('takeout-task')

    cursor = get_cursor()
    query = (
        'SELECT primary_entity_type, primary_entity_value, '
        'secondary_entity_type, secondary_entity_value FROM '
        'eats_data_mappings.entity_pairs WHERE deleted_at '
        'IS NOT NULL'
    )
    cursor.execute(query)

    deleted_pairs = list(cursor)
    assert len(deleted_pairs) == len(EXPECTED_DELETED_PAIRS)
    for pair in EXPECTED_DELETED_PAIRS:
        assert pair in deleted_pairs

    query = (
        'SELECT status FROM eats_data_mappings.takeout '
        'WHERE takeout_id = {0}'
    ).format(TASKS[0]['takeout_id'])
    cursor.execute(query)
    takeouts = list(cursor)
    assert len(takeouts) == 1
    assert takeouts[0][0] == 'finished'
