from integration_procaas.generated import models


async def test_task_start(mock_processing, library_context, load_json):
    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        assert request.query['item_id'] == 'task_uuid'
        assert request.json['phase'] == 'start'
        assert request.headers['X-Idempotency-Token'] == 'epgr_task_uuid'

        start_task_data = load_json('start_task_data.json')
        start_task_data['phase'] = request.json['phase']
        assert request.json == start_task_data

        return {'event_id': 'task_uuid'}

    await library_context.integration_procaas.task_start(
        'task_uuid',
        models.StartTaskData.deserialize(load_json('start_task_data.json')),
    )

    assert create_event.times_called == 1


async def test_task_parsed(mock_processing, library_context):
    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        assert request.query['item_id'] == 'task_uuid'
        assert request.json['phase'] == 'parsed'
        assert request.headers['X-Idempotency-Token'] == 'parser_task_uuid'

        assert request.json['s3_link'] == 's3_link'
        assert request.json['log_uuid'] == 'log_uuid__1'

        return {'event_id': 'task_uuid'}

    await library_context.integration_procaas.task_parsed(
        'task_uuid',
        models.ParsedTaskData(s3_link='s3_link', log_uuid='log_uuid__1'),
    )

    assert create_event.times_called == 1


async def test_task_processed(mock_processing, library_context):
    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        assert request.query['item_id'] == 'task_uuid'
        assert request.json['phase'] == 'processed'
        assert request.headers['X-Idempotency-Token'] == 'emp_task_uuid'

        assert request.json['s3_link'] == 's3_link'
        assert request.json['log_uuid'] == 'log_uuid'

        return {'event_id': 'task_uuid'}

    await library_context.integration_procaas.task_processed(
        'task_uuid',
        models.ProcessedTaskData(s3_link='s3_link', log_uuid='log_uuid'),
    )

    assert create_event.times_called == 1


async def test_task_fallback(mock_processing, library_context):
    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        assert request.query['item_id'] == 'task_uuid'
        assert request.json['phase'] == 'fallback'
        assert request.headers['X-Idempotency-Token'] == 'fallback_task_uuid'

        assert request.json['error_code'] == 200
        assert request.json['error_text'] == 'error_text'
        assert request.json['log_uuid'] == 'log_uuid'
        assert request.json['exception_message'] == 'exception_message'

        return {'event_id': 'task_uuid'}

    await library_context.integration_procaas.task_fallback(
        'task_uuid',
        models.FallbackTaskData(
            error_code=200,
            error_text='error_text',
            log_uuid='log_uuid',
            exception_message='exception_message',
        ),
    )

    assert create_event.times_called == 1
