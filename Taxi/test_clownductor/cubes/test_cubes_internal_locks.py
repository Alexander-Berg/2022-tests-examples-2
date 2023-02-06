import pytest

from clownductor.internal.tasks import cubes
from clownductor.internal.utils import postgres


@pytest.mark.parametrize(
    'cube_name, input_data, locks_in_db, success',
    [
        (
            'InternalGetLock',
            {'lock_name': 'a'},
            [
                {'name': 'a', 'job_id': 1},
                {'name': 'b', 'job_id': 1},
                {'name': 'c', 'job_id': 2},
            ],
            True,
        ),
        (
            'InternalGetLock',
            {'lock_name': 'c'},
            [{'name': 'b', 'job_id': 1}, {'name': 'c', 'job_id': 2}],
            False,
        ),
        (
            'InternalBatchGetLock',
            {'lock_names': ['a', 'b']},
            [
                {'name': 'a', 'job_id': 1},
                {'name': 'b', 'job_id': 1},
                {'name': 'c', 'job_id': 2},
            ],
            True,
        ),
        (
            'InternalReleaseLock',
            {'lock_name': 'a'},
            [{'name': 'b', 'job_id': 1}, {'name': 'c', 'job_id': 2}],
            True,
        ),
        (
            'InternalBatchReleaseLock',
            {'lock_names': ['a', 'b']},
            [{'name': 'c', 'job_id': 2}],
            True,
        ),
    ],
)
async def test_cubes(
        web_context, task_data, cube_name, input_data, locks_in_db, success,
):
    cube = cubes.CUBES[cube_name](
        web_context, task_data(cube_name, job_id=1), input_data, [], None,
    )
    await cube.update()
    assert cube.success == success

    async with postgres.get_connection(web_context) as conn:
        locks = await conn.fetch(
            'SELECT * FROM task_manager.locks ORDER BY name;',
        )

    assert [dict(x) for x in locks] == locks_in_db
