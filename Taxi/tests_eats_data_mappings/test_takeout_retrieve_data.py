import pytest
import datetime

from sys import platform

TASK = [
    {
        'id': 1,
        'task_type': 'retrieve_data',
        'done': False,
        'takeout_id': 111,
        'mapping_id': 4,
    },
]

TAKEOUT = [
    {
        'takeout_id': 111,
        'request_id': 'id1',
        'takeout_policy': 'all',
        'yandex_uid': 'uid1',
        'status': 'data_search',
    },
]

PAIRS = [
    {
        'id': 1,
        'primary_entity_type': 'yandex_uid',
        'primary_entity_value': 'uid1',
        'secondary_entity_type': 'eater_id',
        'secondary_entity_value': 'eater_id1',
        'created_at': '2022-07-01 12:00:00+03:00',
    },
    {
        'id': 2,
        'primary_entity_type': 'eater_id',
        'primary_entity_value': 'eater_id1',
        'secondary_entity_type': 'a',
        'secondary_entity_value': 'a_1',
        'created_at': '2022-07-01 12:00:00+03:00',
    },
]


@pytest.mark.skipif(
    'linux' not in platform, reason='yt-local only available for Linux',
)
@pytest.mark.parametrize(
    'tasks_to_insert, takeout_mapping_elements_to_insert, takeouts_to_insert, takeout_data_to_insert, pairs_to_insert, expected_takeout_data',
    [
        pytest.param(
            TASK,
            [
                {
                    'takeout_id': 111,
                    'mapping_id': 4,
                    'ordinal_number': 0,
                    'done': False,
                    'primary_type': 'yandex_uid',
                    'secondary_type': 'eater_id',
                    'yandex_uid': 'uid1',
                    'search_by': 'primary',
                    'search_in': 'pg',
                    'target_link': False,
                },
            ],
            TAKEOUT,
            [],
            PAIRS,
            [
                {
                    'takeout_id': 111,
                    'mapping_id': 4,
                    'target_link': False,
                    'primary_type': 'yandex_uid',
                    'primary_value': 'uid1',
                    'secondary_type': 'eater_id',
                    'secondary_value': 'eater_id1',
                    'real_id': 1,
                    'created_at': datetime.datetime.fromisoformat(
                        '2022-07-01 12:00:00+03:00',
                    ),
                },
            ],
            id='retrieve_data with ordinal_number = 0',
        ),
        pytest.param(
            TASK,
            [
                {
                    'takeout_id': 111,
                    'mapping_id': 4,
                    'ordinal_number': 1,
                    'done': False,
                    'primary_type': 'eater_id',
                    'secondary_type': 'a',
                    'yandex_uid': 'uid1',
                    'search_by': 'primary',
                    'search_in': 'pg',
                    'target_link': False,
                },
            ],
            TAKEOUT,
            [
                {
                    'takeout_id': 111,
                    'mapping_id': 4,
                    'target_link': False,
                    'primary_type': 'yandex_uid',
                    'primary_value': 'uid1',
                    'secondary_type': 'eater_id',
                    'secondary_value': 'eater_id1',
                    'real_id': 1,
                    'created_at': datetime.datetime.fromisoformat(
                        '2022-07-01 12:00:00+03:00',
                    ),
                },
            ],
            PAIRS,
            [
                {
                    'takeout_id': 111,
                    'mapping_id': 4,
                    'target_link': False,
                    'primary_type': 'yandex_uid',
                    'primary_value': 'uid1',
                    'secondary_type': 'eater_id',
                    'secondary_value': 'eater_id1',
                    'real_id': 1,
                    'created_at': datetime.datetime.fromisoformat(
                        '2022-07-01 12:00:00+03:00',
                    ),
                },
                {
                    'takeout_id': 111,
                    'mapping_id': 4,
                    'target_link': False,
                    'primary_type': 'eater_id',
                    'primary_value': 'eater_id1',
                    'secondary_type': 'a',
                    'secondary_value': 'a_1',
                    'real_id': 2,
                    'created_at': datetime.datetime.fromisoformat(
                        '2022-07-01 12:00:00+03:00',
                    ),
                },
            ],
            id='retrieve_data with ordinal_number = 1',
        ),
        pytest.param(
            TASK,
            [
                {
                    'takeout_id': 111,
                    'mapping_id': 4,
                    'ordinal_number': 0,
                    'done': False,
                    'primary_type': 'yandex_uid',
                    'secondary_type': 'eater_id',
                    'yandex_uid': 'wrong_uid',
                    'search_by': 'primary',
                    'search_in': 'pg',
                    'target_link': False,
                },
            ],
            TAKEOUT,
            [],
            PAIRS,
            [],
            id='retrieve_data with wrong_uid',
        ),
        pytest.param(
            TASK,
            [
                {
                    'takeout_id': 111,
                    'mapping_id': 4,
                    'ordinal_number': 1,
                    'done': False,
                    'primary_type': 'eater_id',
                    'secondary_type': 'a',
                    'yandex_uid': 'uid1',
                    'search_by': 'primary',
                    'search_in': 'pg',
                    'target_link': False,
                },
            ],
            TAKEOUT,
            [],
            PAIRS,
            [],
            id='retrieve_data when no takeout_data',
        ),
    ],
)
@pytest.mark.yt(dyn_table_data=['yt_eats_data_mappings_entity_pairs.yaml'])
@pytest.mark.add_extra_settings
async def test_takeout_retrieve_data(
        taxi_eats_data_mappings,
        insert_tasks,
        tasks_to_insert,
        insert_takeouts,
        takeouts_to_insert,
        insert_takeout_mapping_elements,
        takeout_mapping_elements_to_insert,
        insert_pairs_with_id,
        pairs_to_insert,
        insert_takeout_data,
        takeout_data_to_insert,
        get_all_takeout_data,
        get_status_takeout_mapping_element,
        get_status_takeout_task_by_id,
        expected_takeout_data,
        compare_expected_with_found,
        yt_apply,
):
    insert_tasks(tasks_to_insert)
    insert_takeouts(takeouts_to_insert)
    insert_takeout_mapping_elements(takeout_mapping_elements_to_insert)
    insert_pairs_with_id(pairs_to_insert)
    insert_takeout_data(takeout_data_to_insert)

    await taxi_eats_data_mappings.run_task('takeout-task')
    found_takeout_data = get_all_takeout_data()

    # Check that takeout_data was fetched
    assert compare_expected_with_found(
        found_takeout_data, expected_takeout_data,
    )

    # Check that takeout_task still marked as not done
    assert get_status_takeout_task_by_id(tasks_to_insert[0]['id']) == False

    # Check that takeout_mapping_element marked as done
    assert get_status_takeout_mapping_element(
        takeout_mapping_elements_to_insert[0]['takeout_id'],
        takeout_mapping_elements_to_insert[0]['mapping_id'],
        takeout_mapping_elements_to_insert[0]['ordinal_number'],
        takeout_mapping_elements_to_insert[0]['search_in'],
    )

    # Excute takeout-task again and validate that this task marked as done
    # due to no more akeout_mapping_elements marked as not done with current task id
    await taxi_eats_data_mappings.run_task('takeout-task')
    assert get_status_takeout_task_by_id(tasks_to_insert[0]['id']) == True
