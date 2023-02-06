import json

from aiohttp import web
import pytest

from personal_goals import const


@pytest.mark.config(PERSONAL_GOALS_GOALS_IMPORT_CHUNK=5)
@pytest.mark.yt(
    schemas=['yt_personal_goals_schema.yaml'],
    static_table_data=['yt_personal_goals.yaml'],
)
async def test_goals_importing(
        stq_runner, stq, mock_personal_goals, yt_apply_force, yt_client,
):
    _table_path = '//some/path'
    _table_size = int(yt_client.get_attribute(_table_path, 'row_count'))

    import_task_id = 'some-id'

    @mock_personal_goals('/internal/admin/import_tasks')
    def _mock_get_import_task(request):
        assert request.query['import_task_id'] == import_task_id
        import_task = {
            'import_task_id': import_task_id,
            'yt_table_path': _table_path,
            'rows_count': _table_size,
            'last_row_index': 4,
            'failed_count': 3,
            'status': const.IMPORT_TASK_STATUS_IN_PROGRESS,
        }
        return import_task

    @mock_personal_goals('/internal/admin/add_bulk')
    def _mock_add_bulk(request):
        body = request.json
        return {'excluded_goals': body[:3]}

    @mock_personal_goals('/internal/admin/import_tasks/progress')
    def _mock_update_progress(request):
        body = request.json
        assert body['last_row_index'] == 9
        assert body['failed_count'] == 6
        assert body['failed_details'] == {
            'Goals were excluded': [
                'msc_2019-09-055',
                'msc_2019-09-056',
                'msc_2019-09-057',
            ],
        }
        return web.Response()

    await stq_runner.goals_importing.call(
        task_id=import_task_id, args=(import_task_id,),
    )

    # task must be rescheduled
    assert not stq.is_empty

    task_in_queue = stq.goals_importing.next_call()
    assert task_in_queue['id'] == import_task_id
    assert task_in_queue['args'] == [import_task_id]


@pytest.mark.config(PERSONAL_GOALS_GOALS_IMPORT_CHUNK=5)
@pytest.mark.yt(
    schemas=['yt_personal_goals_schema.yaml'],
    static_table_data=['yt_personal_goals.yaml'],
)
async def test_goals_importing_failure(
        stq_runner, stq, mock_personal_goals, yt_apply_force, yt_client,
):
    _table_path = '//some/path'
    _table_size = int(yt_client.get_attribute(_table_path, 'row_count'))

    import_task_id = 'some-id'

    @mock_personal_goals('/internal/admin/import_tasks')
    def _mock_get_import_task(request):
        assert request.query['import_task_id'] == import_task_id
        import_task = {
            'import_task_id': import_task_id,
            'yt_table_path': _table_path,
            'rows_count': _table_size,
            'last_row_index': 4,
            'failed_count': 3,
            'status': const.IMPORT_TASK_STATUS_IN_PROGRESS,
        }
        return import_task

    @mock_personal_goals('/internal/admin/add_bulk')
    def _mock_add_bulk(request):
        return web.HTTPBadRequest(
            body=json.dumps(
                {
                    'code': 'REQUEST_VALIDATION_ERROR',
                    'details': {'reason': 'date_finish is required property'},
                    'message': 'Some parameters are invalid',
                },
            ),
        )

    @mock_personal_goals('/internal/admin/import_tasks/progress')
    def _mock_update_progress(request):
        body = request.json
        assert body['failed_count'] == 4
        assert body['failed_details'] == {
            'Some parameters are invalid '
            '(date_finish is required property)': [],
        }
        return web.Response()

    await stq_runner.goals_importing.call(
        task_id=import_task_id, args=(import_task_id,),
    )

    # task must be completed
    assert stq.is_empty


@pytest.mark.parametrize(
    'row_index, failed_details',
    [
        (0, {'Unexpected fields: [\'date_fin\']': []}),
        (1, {'date_start is required property': []}),
        (2, {'Invalid value for count: \'3\' is not instance of int': []}),
        (3, {'Expecting \',\' delimiter: line 1 column 32 (char 31)': []}),
    ],
)
@pytest.mark.config(PERSONAL_GOALS_GOALS_IMPORT_CHUNK=1)
@pytest.mark.yt(
    schemas=['yt_personal_goals_schema.yaml'],
    static_table_data=['yt_personal_goals-errors.yaml'],
)
async def test_goals_importing_read_failure(
        stq_runner,
        stq,
        mock_personal_goals,
        row_index,
        failed_details,
        yt_apply_force,
        yt_client,
):
    _table_path = '//some/path'

    import_task_id = 'some-id-unexpected'

    @mock_personal_goals('/internal/admin/import_tasks')
    def _mock_get_import_task(request):
        assert request.query['import_task_id'] == import_task_id
        import_task = {
            'import_task_id': import_task_id,
            'yt_table_path': _table_path,
            'rows_count': row_index + 1,
            'last_row_index': row_index,
            'failed_count': 0,
            'status': const.IMPORT_TASK_STATUS_IN_PROGRESS,
        }
        return import_task

    @mock_personal_goals('/internal/admin/import_tasks/progress')
    def _mock_update_progress(request):
        body = request.json
        assert body == {
            'last_row_index': row_index + 1,
            'failed_count': 1,
            'failed_details': failed_details,
        }
        return web.Response()

    await stq_runner.goals_importing.call(
        task_id=import_task_id, args=(import_task_id,),
    )

    # task must be completed
    assert stq.is_empty
