import json
import typing

import pytest

from personal_goals import const
from personal_goals.api.modules import personal_goals_import as module


TABLE_PATH = '//home/taxi/personal-goals/foo-table'
GOOD_SCHEMA = [
    {'name': 'selection_id', 'type': 'string'},
    {'name': 'bonus', 'type': 'string'},
    {'name': 'conditions', 'type': 'string'},
    {'name': 'application', 'type': 'string'},
    {'name': 'yandex_uid', 'type': 'string'},
]


@pytest.fixture
def _do_import(taxi_personal_goals_web):
    async def _internal(path: str, expected_code: int = 200):
        response = await taxi_personal_goals_web.post(
            '/internal/admin/import', data=json.dumps({'yt_table_path': path}),
        )
        assert response.status == expected_code
        return response

    return _internal


@pytest.fixture
def _add_table(yt_client):
    def _internal(path: str, schema: typing.List[dict], rows_count: int = 0):
        yt_client.create_table(
            path,
            attributes={module.common.SCHEMA_ATTRIBUTE: schema},
            recursive=True,
        )
        yt_client.write_table(
            path, [{column['name']: '' for column in schema}] * rows_count,
        )

    return _internal


async def test_path_validation(
        _do_import, _add_table, yt_client, yt_apply_force,
):
    # init mock before any assertions to make checks on not existent path
    node_path = '//home/taxi/personal-goals/bad-path'
    yt_client.create('map_node', node_path, recursive=True)

    _add_table(TABLE_PATH, [])

    async def _check_fail(path, code):
        response = await _do_import(path, expected_code=400)
        response_json = await response.json()
        assert response_json['code'] == code

    await _check_fail('//bad/path', 'YT_PATH_NOT_FOUND')
    await _check_fail(node_path, 'NO_TABLE_AT_PATH')
    await _check_fail(TABLE_PATH, 'INVALID_TABLE_SCHEMA')


@pytest.mark.parametrize(
    'schema, expected_code',
    [
        # exact scheme
        (GOOD_SCHEMA, 200),
        # missed field (selection_id)
        (
            [
                {'name': 'bonus', 'type': 'string'},
                {'name': 'conditions', 'type': 'string'},
                {'name': 'application', 'type': 'string'},
                {'name': 'yandex_uid', 'type': 'string'},
            ],
            400,
        ),
        # extra field -> won't fail
        (
            GOOD_SCHEMA + [{'name': 'IM_ADDITIONAL_FIELD', 'type': 'string'}],
            200,
        ),
    ],
)
async def test_schema_validation(
        schema, expected_code, _do_import, _add_table, yt_apply_force,
):
    rows_count = 10
    _add_table(TABLE_PATH, schema, rows_count)

    response = await _do_import(TABLE_PATH, expected_code=expected_code)
    if response.status == 400:
        response_json = await response.json()
        assert response_json['code'] == 'INVALID_TABLE_SCHEMA'


async def test_registering_task(
        pg_goals, _do_import, _add_table, yt_apply_force,
):
    # create some tables
    rows_count = 10
    _add_table(TABLE_PATH, GOOD_SCHEMA, rows_count)

    new_table_path = '//another/table'
    new_table_rows_count = 15
    _add_table(new_table_path, GOOD_SCHEMA, new_table_rows_count)

    async def _import(path):
        response = await _do_import(path)
        response_json = await response.json()
        return response_json['data']['import_task_id']

    # start import from first table
    task_id = await _import(TABLE_PATH)

    import_tasks = await pg_goals.import_tasks.all()
    assert len(import_tasks) == 1
    task = import_tasks[0]
    assert task['import_task_id'].hex == task_id
    assert task['yt_table_path'] == TABLE_PATH
    assert task['rows_count'] == rows_count
    assert task['failed_count'] == 0
    assert task['status'] == const.IMPORT_TASK_STATUS_PENDING

    # second attempt to add same path -> nothing changed, same task_id returned
    new_task_id = await _import(TABLE_PATH)
    assert task_id == new_task_id
    new_tasks = await pg_goals.import_tasks.all()
    assert import_tasks == new_tasks

    # add another table -> success
    new_task_id = await _import(new_table_path)

    import_tasks = await pg_goals.import_tasks.all()
    assert all(
        [
            task['status'] == const.IMPORT_TASK_STATUS_PENDING
            for task in import_tasks
        ],
    )
    assert set(task['yt_table_path'] for task in import_tasks) == {
        TABLE_PATH,
        new_table_path,
    }
    assert set(task['import_task_id'].hex for task in import_tasks) == {
        task_id,
        new_task_id,
    }


@pytest.mark.pgsql('personal_goals', files=['completed_tasks.sql'])
async def test_completed_tasks_not_prevent_import(
        pg_goals, _do_import, _add_table, yt_apply_force,
):
    rows_count = 10

    # create some tables in YT
    table_1 = '//path/to/table/1'  # has pending import task
    table_2 = '//path/to/table/2'
    table_3 = '//path/to/table/3'  # in progress now first time
    for table in (table_1, table_2, table_3):
        _add_table(table, GOOD_SCHEMA, rows_count)

    current_tasks = await pg_goals.import_tasks.all()
    assert len(current_tasks) == 4

    table_tasks = {
        task['yt_table_path']: task['import_task_id'].hex
        for task in current_tasks
    }

    # no fails
    for table in (table_1, table_3):
        response = await _do_import(table)
        response_json = await response.json()
        assert table_tasks[table] == response_json['data']['import_task_id']

    current_tasks = await pg_goals.import_tasks.all()
    assert len(current_tasks) == 4

    # has only completed task
    response = await _do_import(table_2)
    response_json = await response.json()
    task_id = response_json['data']['import_task_id']

    updated_tasks = await pg_goals.import_tasks.all()
    assert len(updated_tasks) == 5
    added_task = next(
        task for task in updated_tasks if task['import_task_id'].hex == task_id
    )
    assert added_task['yt_table_path'] == table_2
    assert added_task['rows_count'] == rows_count
    assert added_task['status'] == const.IMPORT_TASK_STATUS_PENDING
