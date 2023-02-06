import pytest

from datetime import datetime

TAKEOUTS = [
    {
        'takeout_id': 1,
        'request_id': 'id1',
        'takeout_policy': 'all',
        'yandex_uid': 'uid1',
        'status': 'finished',
    },
    {
        'takeout_id': 2,
        'request_id': 'id2',
        'takeout_policy': 'all',
        'yandex_uid': 'uid2',
        'status': 'ready_to_takeout',
    },
]

TASKS = [
    {
        'id': 1,
        'task_type': 'process_incoming_request',
        'done': True,
        'takeout_id': 1,
        'mapping_id': None,
    },
    {
        'id': 2,
        'task_type': 'retrieve_data',
        'done': True,
        'takeout_id': 1,
        'mapping_id': 1,
    },
    {
        'id': 3,
        'task_type': 'retrieve_data',
        'done': True,
        'takeout_id': 1,
        'mapping_id': 2,
    },
    {
        'id': 4,
        'task_type': 'retrieve_data',
        'done': True,
        'takeout_id': 1,
        'mapping_id': 4,
    },
    {
        'id': 5,
        'task_type': 'mark_as_prepared',
        'done': True,
        'takeout_id': 1,
        'mapping_id': None,
    },
    {
        'id': 6,
        'task_type': 'process_incoming_request',
        'done': True,
        'takeout_id': 2,
        'mapping_id': None,
    },
    {
        'id': 7,
        'task_type': 'finish_takeout',
        'done': True,
        'takeout_id': 1,
        'mapping_id': None,
    },
    {
        'id': 8,
        'task_type': 'retrieve_data',
        'done': True,
        'takeout_id': 2,
        'mapping_id': 1,
    },
    {
        'id': 9,
        'task_type': 'retrieve_data',
        'done': True,
        'takeout_id': 2,
        'mapping_id': 3,
    },
    {
        'id': 10,
        'task_type': 'mark_as_prepared',
        'done': True,
        'takeout_id': 2,
        'mapping_id': None,
    },
    {
        'id': 11,
        'task_type': 'delete_temporary_data',
        'done': False,
        'takeout_id': 1,
        'mapping_id': None,
    },
    {
        'id': 12,
        'task_type': 'finish_takeout',
        'done': False,
        'takeout_id': 2,
        'mapping_id': None,
    },
]

MAPPING_ELEMENTS = [
    {
        'takeout_id': 1,
        'mapping_id': 1,
        'ordinal_number': 1,
        'done': True,
        'primary_type': 'yandex_uid',
        'secondary_type': 'eater_id',
        'yandex_uid': 'uid1',
        'search_in': 'pg',
        'search_by': 'primary',
        'target_link': False,
    },
    {
        'takeout_id': 1,
        'mapping_id': 1,
        'ordinal_number': 1,
        'done': True,
        'primary_type': 'yandex_uid',
        'secondary_type': 'eater_id',
        'yandex_uid': 'uid1',
        'search_in': 'yt',
        'search_by': 'primary',
        'target_link': False,
    },
    {
        'takeout_id': 1,
        'mapping_id': 2,
        'ordinal_number': 2,
        'done': True,
        'primary_type': 'eater_id',
        'secondary_type': 'type1',
        'yandex_uid': 'uid1',
        'search_in': 'pg',
        'search_by': 'primary',
        'target_link': False,
    },
    {
        'takeout_id': 1,
        'mapping_id': 2,
        'ordinal_number': 2,
        'done': True,
        'primary_type': 'eater_id',
        'secondary_type': 'type1',
        'yandex_uid': 'uid1',
        'search_in': 'pg',
        'search_by': 'primary',
        'target_link': False,
    },
    {
        'takeout_id': 1,
        'mapping_id': 3,
        'ordinal_number': 4,
        'done': True,
        'primary_type': 'type3',
        'secondary_type': 'type1',
        'yandex_uid': 'uid1',
        'search_in': 'pg',
        'search_by': 'secondary',
        'target_link': True,
    },
    {
        'takeout_id': 1,
        'mapping_id': 3,
        'ordinal_number': 4,
        'done': True,
        'primary_type': 'type3',
        'secondary_type': 'type1',
        'yandex_uid': 'uid1',
        'search_in': 'yt',
        'search_by': 'secondary',
        'target_link': True,
    },
    {
        'takeout_id': 2,
        'mapping_id': 1,
        'ordinal_number': 1,
        'done': True,
        'primary_type': 'yandex_uid',
        'secondary_type': 'eater_id',
        'yandex_uid': 'uid2',
        'search_in': 'pg',
        'search_by': 'primary',
        'target_link': False,
    },
    {
        'takeout_id': 2,
        'mapping_id': 1,
        'ordinal_number': 1,
        'done': True,
        'primary_type': 'yandex_uid',
        'secondary_type': 'eater_id',
        'yandex_uid': 'uid2',
        'search_in': 'yt',
        'search_by': 'primary',
        'target_link': False,
    },
    {
        'takeout_id': 2,
        'mapping_id': 3,
        'ordinal_number': 2,
        'done': True,
        'primary_type': 'eater_id',
        'secondary_type': 'type2',
        'yandex_uid': 'uid2',
        'search_in': 'pg',
        'search_by': 'primary',
        'target_link': False,
    },
    {
        'takeout_id': 2,
        'mapping_id': 3,
        'ordinal_number': 2,
        'done': True,
        'primary_type': 'eater_id',
        'secondary_type': 'type2',
        'yandex_uid': 'uid2',
        'search_in': 'pg',
        'search_by': 'primary',
        'target_link': False,
    },
]

DATA = [
    {
        'takeout_id': 1,
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
        'takeout_id': 1,
        'mapping_id': 2,
        'target_link': False,
        'primary_type': 'eater_id',
        'primary_value': 'id1',
        'secondary_type': 'type1',
        'secondary_value': 'value1',
        'real_id': 2,
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'takeout_id': 1,
        'mapping_id': 4,
        'target_link': True,
        'primary_type': 'type3',
        'primary_value': 'value3',
        'secondary_type': 'type1',
        'secondary_value': 'value1',
        'real_id': 4,
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'takeout_id': 2,
        'mapping_id': 1,
        'target_link': False,
        'primary_type': 'yandex_uid',
        'primary_value': 'uid2',
        'secondary_type': 'eater_id',
        'secondary_value': 'id2',
        'real_id': 5,
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'takeout_id': 1,
        'mapping_id': 3,
        'target_link': False,
        'primary_type': 'eater_id',
        'primary_value': 'id2',
        'secondary_type': 'type2',
        'secondary_value': 'value2',
        'real_id': 7,
        'created_at': '2022-07-01 12:00:00+03:00',
    },
]


async def test_delete_temporary_data(
        taxi_eats_data_mappings,
        get_cursor,
        insert_takeouts,
        insert_tasks,
        insert_takeout_mapping_elements,
        insert_takeout_data,
        get_all_takeout_tasks,
        get_all_takeouts,
        get_all_takeout_mapping_elements,
        get_all_takeout_data,
):
    insert_takeouts(TAKEOUTS)
    insert_tasks(TASKS)
    insert_takeout_data(DATA)
    insert_takeout_mapping_elements(MAPPING_ELEMENTS)

    await taxi_eats_data_mappings.run_task('takeout-task')

    cursor = get_cursor()
    target_id = [
        task['takeout_id']
        for task in TASKS
        if task['task_type'] == 'delete_temporary_data'
    ][0]

    # We're checking that all tasks/mapping elements/data entries with
    # target takeout id are deleted and all others are unchanged
    tasks = get_all_takeout_tasks()
    expected_tasks = [
        task for task in TASKS if task['takeout_id'] != target_id
    ]
    assert len(tasks) == len(expected_tasks)
    for task in expected_tasks:
        assert task in tasks

    mapping_elements = get_all_takeout_mapping_elements(True)
    expected_mapping_elements = [
        element
        for element in MAPPING_ELEMENTS
        if element['takeout_id'] != target_id
    ]
    assert len(mapping_elements) == len(expected_mapping_elements)
    for element in expected_mapping_elements:
        assert element in mapping_elements

    data = get_all_takeout_data()
    expected_data = [
        entry for entry in DATA if entry['takeout_id'] != target_id
    ]
    for entry in data:
        entry['created_at'] = entry['created_at'].isoformat(sep=' ')
    assert len(data) == len(expected_data)
    for entry in expected_data:
        assert entry in data

    # No takeouts should be either deleted or changed
    takeouts = get_all_takeouts()
    expected_takeouts = TAKEOUTS
    assert len(takeouts) == len(expected_takeouts)
    for takeout in expected_takeouts:
        assert takeout in takeouts
