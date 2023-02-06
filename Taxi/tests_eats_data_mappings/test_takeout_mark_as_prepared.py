import pytest

TAKEOUTS = [
    {
        'takeout_id': 111,
        'request_id': 'id1',
        'takeout_policy': 'all',
        'yandex_uid': 'uid1',
        'status': 'data_search',
    },
    {
        'takeout_id': 222,
        'request_id': 'id1',
        'takeout_policy': 'all',
        'yandex_uid': 'uid2',
        'status': 'data_search',
    },
]

TASKS = [
    {
        'id': 1,
        'task_type': 'mark_as_prepared',
        'done': False,
        'takeout_id': 111,
        'mapping_id': 'NULL',
    },
    {
        'id': 2,
        'task_type': 'process_incoming_request',
        'done': False,
        'takeout_id': 111,
        'mapping_id': 'NULL',
    },
    {
        'id': 3,
        'task_type': 'retrieve_data',
        'done': False,
        'takeout_id': 222,
        'mapping_id': 'NULL',
    },
    {
        'id': 4,
        'task_type': 'retrieve_data',
        'done': True,
        'takeout_id': 111,
        'mapping_id': 'NULL',
    },
]


async def test_takeout_mark_as_prepared_done(
        taxi_eats_data_mappings, insert_tasks, insert_takeouts, get_cursor,
):
    insert_tasks(TASKS)
    insert_takeouts(TAKEOUTS)

    await taxi_eats_data_mappings.run_task('takeout-task')

    # checking that task is marked as done
    cursor = get_cursor()
    query = (
        'SELECT done FROM eats_data_mappings.takeout_tasks WHERE id = {0}'
    ).format(TASKS[0]['id'])
    cursor.execute(query)
    assert list(cursor)[0][0]

    # checking that a new task with type 'finish_takeout'
    # and same takeout_id is created
    query = (
        'SELECT takeout_id, done FROM eats_data_mappings.takeout_tasks '
        'WHERE task_type = \'finish_takeout\''
    )
    cursor.execute(query)
    tasks = list(cursor)
    assert len(tasks) == 1
    assert tasks[0][0] == TASKS2[1]['takeout_id']
    assert not tasks[0][1]

    # checking that status with that takeout_id is changed
    query = (
        'SELECT status FROM eats_data_mappings.takeout '
        'WHERE takeout_id = {0}'
    ).format(TASKS2[1]['takeout_id'])
    cursor.execute(query)
    takeouts = list(cursor)
    assert len(takeouts) == 1
    assert takeouts[0][0] == 'ready_to_takeout'


TASKS2 = [
    {
        'id': 1,
        'task_type': 'mark_as_prepared',
        'done': False,
        'takeout_id': 111,
        'mapping_id': 'NULL',
    },
    {
        'id': 2,
        'task_type': 'retrieve_data',
        'done': False,
        'takeout_id': 111,
        'mapping_id': 'NULL',
    },
]


async def test_takeout_mark_as_prepared_not_done(
        taxi_eats_data_mappings, insert_tasks, insert_takeouts, get_cursor,
):
    insert_tasks(TASKS2)
    insert_takeouts(TAKEOUTS)

    await taxi_eats_data_mappings.run_task('takeout-task')

    # checking that task is still marked as undone
    cursor = get_cursor()
    query = (
        'SELECT done FROM eats_data_mappings.takeout_tasks WHERE id = {0}'
    ).format(TASKS2[0]['id'])
    cursor.execute(query)
    assert not list(cursor)[0][0]

    # checking that a task with type 'finish_takeout'
    # and same takeout_id is NOT created
    query = (
        'SELECT takeout_id, done FROM eats_data_mappings.takeout_tasks '
        'WHERE task_type = \'finish_takeout\''
    )
    cursor.execute(query)
    tasks = list(cursor)
    assert len(tasks) == 0

    # checking that status with that takeout_id is the same
    query = (
        'SELECT status FROM eats_data_mappings.takeout '
        'WHERE takeout_id = {0}'
    ).format(TASKS2[1]['takeout_id'])
    cursor.execute(query)
    takeouts = list(cursor)
    assert len(takeouts) == 1
    assert takeouts[0][0] == 'data_search'
