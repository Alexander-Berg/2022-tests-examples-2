import pytest

TASKS = [
    {
        'id': 1,
        'task_type': 'process_incoming_request',
        'done': False,
        'takeout_id': 111,
        'mapping_id': 111,
    },
    {
        'id': 2,
        'task_type': 'process_incoming_request',
        'done': False,
        'takeout_id': 222,
        'mapping_id': 222,
    },
    {
        'id': 3,
        'task_type': 'process_incoming_request',
        'done': False,
        'takeout_id': 333,
        'mapping_id': 333,
    },
]


async def test_takeout_task(taxi_eats_data_mappings, insert_tasks, testpoint):
    insert_tasks(TASKS)

    @testpoint('get_locked_task')
    def get_locked_task(data):
        pass

    await taxi_eats_data_mappings.run_task('takeout-task')

    locked_task = await get_locked_task.wait_call()
    assert locked_task['data'] == TASKS[0]


async def test_takeout_task_locked(
        taxi_eats_data_mappings, insert_tasks, testpoint, pgsql,
):
    insert_tasks(TASKS)

    @testpoint('get_locked_task')
    def get_locked_task(data):
        pass

    connection = pgsql['eats_data_mappings'].conn
    connection.autocommit = False
    connection.cursor().execute(
        'SELECT * '
        'FROM eats_data_mappings.takeout_tasks '
        'WHERE id = 1 '
        'FOR NO KEY UPDATE SKIP LOCKED;',
    )

    await taxi_eats_data_mappings.run_task('takeout-task')

    connection.rollback()
    connection.autocommit = True

    locked_task = await get_locked_task.wait_call()
    assert locked_task['data'] == TASKS[1]
