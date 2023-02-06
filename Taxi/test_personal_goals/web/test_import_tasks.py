import uuid

import pytest

from personal_goals import const


PENDING_TASK = 'fdedcdd5-57fe-43c4-bc00-a394f23ac7e7'
IN_PROGRESS_TASK = 'df795752-1801-4715-ba07-8fe25b73c016'
COMPLETED_TASK = '88db6b2e-dc06-4a3c-af6d-192846860227'
ABSENT_TASK = '00000000-0000-0000-0000-a394f23ac7e7'


@pytest.mark.pgsql('personal_goals', files=['completed_tasks.sql'])
@pytest.mark.parametrize(
    'import_task_id, expected',
    [
        # tasks from completed_tasks.sql
        (
            PENDING_TASK,
            {
                'yt_table_path': '//path/to/table/1',
                'rows_count': 10,
                'last_row_index': 0,
                'failed_count': 0,
                'status': 'pending',
            },
        ),
        (
            IN_PROGRESS_TASK,
            {
                'yt_table_path': '//path/to/table/3',
                'rows_count': 20,
                'last_row_index': 2,
                'failed_count': 1,
                'status': 'in_progress',
            },
        ),
    ],
)
async def test_get_import_task(
        taxi_personal_goals_web, import_task_id, expected,
):
    response = await taxi_personal_goals_web.get(
        '/internal/admin/import_tasks',
        params={'import_task_id': import_task_id},
    )

    assert response.status == 200
    response_body = await response.json()
    expected['import_task_id'] = uuid.UUID(import_task_id, version=4).hex
    assert response_body == expected


@pytest.mark.pgsql('personal_goals', files=['completed_tasks.sql'])
async def test_get_absent_import_task(taxi_personal_goals_web):
    bad_import_task_id = ABSENT_TASK
    response = await taxi_personal_goals_web.get(
        '/internal/admin/import_tasks',
        params={'import_task_id': bad_import_task_id},
    )

    assert response.status == 404


@pytest.fixture
def _make_progress_request(taxi_personal_goals_web):
    async def _do(import_task_id, last_row_index, failed_count):
        response = await taxi_personal_goals_web.post(
            '/internal/admin/import_tasks/progress',
            params={'import_task_id': import_task_id},
            json={
                'last_row_index': last_row_index,
                'failed_count': failed_count,
            },
        )
        return response

    return _do


@pytest.fixture
def _fetch_task(pg_goals):
    async def _do(import_task_id):
        return (await pg_goals.import_tasks.by_ids([import_task_id]))[0]

    return _do


@pytest.mark.parametrize(
    'last_row_index, failed_count, expected_status',
    [
        # status not changed
        (10, 3, const.IMPORT_TASK_STATUS_IN_PROGRESS),
        # status not changed (on last index)
        (19, 1, const.IMPORT_TASK_STATUS_IN_PROGRESS),
        # status changed to completed (corner case)
        (20, 5, const.IMPORT_TASK_STATUS_COMPLETED),
        # status changed to completed
        (23, 5, const.IMPORT_TASK_STATUS_COMPLETED),
        # status not changed (same values)
        (2, 1, const.IMPORT_TASK_STATUS_IN_PROGRESS),
    ],
)
@pytest.mark.pgsql('personal_goals', files=['completed_tasks.sql'])
async def test_update_in_progress_task(
        _make_progress_request,
        _fetch_task,
        last_row_index,
        failed_count,
        expected_status,
):
    import_task_id = IN_PROGRESS_TASK

    response = await _make_progress_request(
        import_task_id, last_row_index, failed_count,
    )

    assert response.status == 200

    updated_task = await _fetch_task(import_task_id)
    assert str(updated_task['import_task_id']) == import_task_id
    assert updated_task['status'] == expected_status
    assert updated_task['last_row_index'] == last_row_index
    assert updated_task['failed_count'] == failed_count


@pytest.mark.parametrize(
    'last_row_index, failed_count',
    [
        (1, 1),  # last_row_index is less than current
        (5, 0),  # failed_count is less than current
        (5, 10),  # failed_count is more than last_row_index
    ],
)
@pytest.mark.pgsql('personal_goals', files=['completed_tasks.sql'])
async def test_validation_failures(
        _make_progress_request, last_row_index, failed_count,
):
    import_task_id = IN_PROGRESS_TASK

    response = await _make_progress_request(
        import_task_id, last_row_index, failed_count,
    )

    assert response.status == 400
    response_json = await response.json()
    assert response_json['code'] == 'COULD_NOT_UPDATE_IMPORT_TASK_PROGRESS'


@pytest.mark.parametrize(
    'import_task_id, expected_status',
    [
        (PENDING_TASK, const.IMPORT_TASK_STATUS_PENDING),
        (COMPLETED_TASK, const.IMPORT_TASK_STATUS_COMPLETED),
    ],
)
@pytest.mark.pgsql('personal_goals', files=['completed_tasks.sql'])
async def test_update_invalid_task(
        _make_progress_request, _fetch_task, import_task_id, expected_status,
):
    goals_processed = 15
    failed_count = 3

    initial_task = await _fetch_task(import_task_id)

    response = await _make_progress_request(
        import_task_id, goals_processed, failed_count,
    )

    assert response.status == 409

    # nothing changed
    updated_task = await _fetch_task(import_task_id)
    assert initial_task == updated_task


@pytest.mark.pgsql('personal_goals', files=['completed_tasks.sql'])
async def test_update_absent_task(_make_progress_request):
    import_task_id = ABSENT_TASK
    goals_processed = 10
    failed_count = 3

    response = await _make_progress_request(
        import_task_id, goals_processed, failed_count,
    )

    assert response.status == 200
