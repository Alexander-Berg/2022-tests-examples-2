# pylint: disable=W0612
import pytest


@pytest.mark.parametrize(
    'is_parsed, task_uuid, data_request',
    [
        (
            True,
            'task_uuid',
            {
                's3_link': 'file_url',
                'is_identical': False,
                'phase': 'parsed',
                'log_uuid': 'log_uuid__1',
            },
        ),
        (
            False,
            'task_uuid',
            {
                'error_code': 300,
                'error_text': 'error_text',
                'phase': 'fallback',
                'exception_message': 'exception_message',
            },
        ),
    ],
)
async def test_retries_stq_workres(
        stq3_context,
        stq_runner,
        mock_processing,
        is_parsed,
        task_uuid,
        data_request,
):
    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        assert request.json == data_request
        return {'event_id': 'task_uuid'}

    await stq_runner.eats_retail_procaas_task.call(
        task_id='task_id',
        args=(),
        kwargs={
            'procaas_data': {
                'is_parsed': is_parsed,
                'task_uuid': task_uuid,
                'file_url': data_request.get('s3_link'),
                'error_code': data_request.get('error_code'),
                'error_text': data_request.get('error_text'),
                'log_uuid': data_request.get('log_uuid'),
                'exception_message': data_request.get('exception_message'),
            },
        },
    )
