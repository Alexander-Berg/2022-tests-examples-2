import pytest


TAKEOUTS = [
    {
        'takeout_id': 111,
        'request_id': 'id1',
        'takeout_policy': 'all',
        'yandex_uid': 'uid1',
        'status': 'new',
    },
    {
        'takeout_id': 222,
        'request_id': 'id2',
        'takeout_policy': 'orders',
        'yandex_uid': 'uid2',
        'status': 'new',
    },
]

TASK_ALL = [
    {
        'id': 1,
        'task_type': 'process_incoming_request',
        'done': False,
        'takeout_id': 111,
        'mapping_id': 'NULL',
    },
]

TASK_ORDERS = [
    {
        'id': 1,
        'task_type': 'process_incoming_request',
        'done': False,
        'takeout_id': 222,
        'mapping_id': 'NULL',
    },
]

EXPECTED_TAKEOUT_MAPPING_ELEMENTS_ALL = [
    {
        'ordinal_number': 0,
        'primary_type': 'yandex_uid',
        'secondary_type': 'eater_id',
        'search_by': 'primary',
        'search_in': 'pg',
        'target_link': False,
    },
    {
        'ordinal_number': 1,
        'primary_type': 'eater_id',
        'secondary_type': 'a',
        'search_by': 'primary',
        'search_in': 'pg',
        'target_link': False,
    },
    {
        'ordinal_number': 2,
        'primary_type': 'a',
        'secondary_type': 'b',
        'search_by': 'primary',
        'search_in': 'pg',
        'target_link': False,
    },
    {
        'ordinal_number': 3,
        'primary_type': 'b',
        'secondary_type': 'c',
        'search_by': 'primary',
        'search_in': 'pg',
        'target_link': True,
    },
    {
        'ordinal_number': 0,
        'primary_type': 'yandex_uid',
        'secondary_type': 'eater_id',
        'search_by': 'primary',
        'search_in': 'pg',
        'target_link': False,
    },
    {
        'ordinal_number': 1,
        'primary_type': 'eater_id',
        'secondary_type': 'a',
        'search_by': 'primary',
        'search_in': 'pg',
        'target_link': False,
    },
    {
        'ordinal_number': 2,
        'primary_type': 'a',
        'secondary_type': 'b',
        'search_by': 'primary',
        'search_in': 'pg',
        'target_link': False,
    },
    {
        'ordinal_number': 3,
        'primary_type': 'b',
        'secondary_type': 'c',
        'search_by': 'primary',
        'search_in': 'pg',
        'target_link': False,
    },
    {
        'ordinal_number': 4,
        'primary_type': 'c',
        'secondary_type': 'g',
        'search_by': 'primary',
        'search_in': 'pg',
        'target_link': True,
    },
    {
        'ordinal_number': 0,
        'primary_type': 'yandex_uid',
        'secondary_type': 'eater_id',
        'search_by': 'primary',
        'search_in': 'yt',
        'target_link': False,
    },
    {
        'ordinal_number': 1,
        'primary_type': 'eater_id',
        'secondary_type': 'a',
        'search_by': 'primary',
        'search_in': 'yt',
        'target_link': False,
    },
    {
        'ordinal_number': 2,
        'primary_type': 'a',
        'secondary_type': 'b',
        'search_by': 'primary',
        'search_in': 'yt',
        'target_link': False,
    },
    {
        'ordinal_number': 3,
        'primary_type': 'b',
        'secondary_type': 'c',
        'search_by': 'primary',
        'search_in': 'yt',
        'target_link': True,
    },
    {
        'ordinal_number': 0,
        'primary_type': 'yandex_uid',
        'secondary_type': 'eater_id',
        'search_by': 'primary',
        'search_in': 'yt',
        'target_link': False,
    },
    {
        'ordinal_number': 1,
        'primary_type': 'eater_id',
        'secondary_type': 'a',
        'search_by': 'primary',
        'search_in': 'yt',
        'target_link': False,
    },
    {
        'ordinal_number': 2,
        'primary_type': 'a',
        'secondary_type': 'b',
        'search_by': 'primary',
        'search_in': 'yt',
        'target_link': False,
    },
    {
        'ordinal_number': 3,
        'primary_type': 'b',
        'secondary_type': 'c',
        'search_by': 'primary',
        'search_in': 'yt',
        'target_link': False,
    },
    {
        'ordinal_number': 4,
        'primary_type': 'c',
        'secondary_type': 'g',
        'search_by': 'primary',
        'search_in': 'yt',
        'target_link': True,
    },
]

EXPECTED_TAKEOUT_MAPPING_ELEMENTS_ORDERS = [
    {
        'ordinal_number': 0,
        'primary_type': 'yandex_uid',
        'secondary_type': 'eater_id',
        'search_by': 'primary',
        'search_in': 'pg',
        'target_link': False,
    },
    {
        'ordinal_number': 1,
        'primary_type': 'eater_id',
        'secondary_type': 'f',
        'search_by': 'primary',
        'search_in': 'pg',
        'target_link': True,
    },
    {
        'ordinal_number': 0,
        'primary_type': 'yandex_uid',
        'secondary_type': 'eater_id',
        'search_by': 'primary',
        'search_in': 'pg',
        'target_link': False,
    },
    {
        'ordinal_number': 1,
        'primary_type': 'eater_id',
        'secondary_type': 'a',
        'search_by': 'primary',
        'search_in': 'pg',
        'target_link': False,
    },
    {
        'ordinal_number': 2,
        'primary_type': 'a',
        'secondary_type': 'b',
        'search_by': 'primary',
        'search_in': 'pg',
        'target_link': False,
    },
    {
        'ordinal_number': 3,
        'primary_type': 'b',
        'secondary_type': 'd',
        'search_by': 'secondary',
        'search_in': 'pg',
        'target_link': True,
    },
    {
        'ordinal_number': 0,
        'primary_type': 'yandex_uid',
        'secondary_type': 'eater_id',
        'search_by': 'primary',
        'search_in': 'yt',
        'target_link': False,
    },
    {
        'ordinal_number': 1,
        'primary_type': 'eater_id',
        'secondary_type': 'f',
        'search_by': 'primary',
        'search_in': 'yt',
        'target_link': True,
    },
    {
        'ordinal_number': 0,
        'primary_type': 'yandex_uid',
        'secondary_type': 'eater_id',
        'search_by': 'primary',
        'search_in': 'yt',
        'target_link': False,
    },
    {
        'ordinal_number': 1,
        'primary_type': 'eater_id',
        'secondary_type': 'a',
        'search_by': 'primary',
        'search_in': 'yt',
        'target_link': False,
    },
    {
        'ordinal_number': 2,
        'primary_type': 'a',
        'secondary_type': 'b',
        'search_by': 'primary',
        'search_in': 'yt',
        'target_link': False,
    },
    {
        'ordinal_number': 3,
        'primary_type': 'b',
        'secondary_type': 'd',
        'search_by': 'secondary',
        'search_in': 'yt',
        'target_link': True,
    },
]

EXPECTED_TAKEOUT_TASKS_ALL = [
    {
        'task_type': 'retrieve_data',
        'done': False,
        'takeout_id': 111,
        'mapping_id': 4,
    },
    {
        'task_type': 'retrieve_data',
        'done': False,
        'takeout_id': 111,
        'mapping_id': 6,
    },
]

EXPECTED_TAKEOUT_TASKS_ORDERS = [
    {
        'task_type': 'retrieve_data',
        'done': False,
        'takeout_id': 222,
        'mapping_id': 7,
    },
    {
        'task_type': 'retrieve_data',
        'done': False,
        'takeout_id': 222,
        'mapping_id': 8,
    },
]


@pytest.mark.parametrize(
    'insert_task, expected_takeout_mapping_elements, expected_takeout_tasks',
    [
        pytest.param(
            TASK_ALL,
            EXPECTED_TAKEOUT_MAPPING_ELEMENTS_ALL,
            EXPECTED_TAKEOUT_TASKS_ALL,
            id='takeout all',
        ),
        pytest.param(
            TASK_ORDERS,
            EXPECTED_TAKEOUT_MAPPING_ELEMENTS_ORDERS,
            EXPECTED_TAKEOUT_TASKS_ORDERS,
            id='takeout orders',
        ),
    ],
)
@pytest.mark.add_extra_settings
async def test_takeout_process_incomming_request(
        taxi_eats_data_mappings,
        insert_tasks,
        insert_takeouts,
        insert_task,
        expected_takeout_mapping_elements,
        expected_takeout_tasks,
        get_all_takeout_mapping_elements,
        get_status_takeout_task_by_id,
        get_takeout_tasks_retrieve_data_by_takeout_id,
        get_takeout_tasks_mark_as_prepared_by_takeout_id,
        compare_expected_with_found,
):
    insert_tasks(insert_task)
    insert_takeouts(TAKEOUTS)
    await taxi_eats_data_mappings.run_task('takeout-task')

    found_takeout_mapping_elements = get_all_takeout_mapping_elements()
    assert compare_expected_with_found(
        expected_takeout_mapping_elements, found_takeout_mapping_elements,
    )

    # checking that status of task marked as done
    assert get_status_takeout_task_by_id(insert_task[0]['id'])

    # checking that all necessary tasks was created with status 'retrieve_data'
    found_takeout_tasks = get_takeout_tasks_retrieve_data_by_takeout_id(
        insert_task[0]['takeout_id'],
    )
    assert compare_expected_with_found(
        expected_takeout_tasks, found_takeout_tasks,
    )

    # checking that one task was created with status 'mark_as_prepared'
    assert (
        len(
            get_takeout_tasks_mark_as_prepared_by_takeout_id(
                insert_task[0]['takeout_id'],
            ),
        )
        == 1
    )
