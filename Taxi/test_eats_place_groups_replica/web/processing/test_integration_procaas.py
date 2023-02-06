from integration_procaas.generated import models


async def test_library(mock_processing, web_context):
    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        assert request.query['item_id'] == 'task_uuid'
        return {'event_id': 'task_uuid'}

    client = web_context.integration_procaas
    await client.task_start(
        'task_uuid',
        models.StartTaskData(
            parser_name='parser_name',
            task_type='task_type',
            place_id='place_id',
            place_group_id='place_group_id',
            forwarded_data=models.ForwardedData(
                origin_place_id='origin_place_id', stock_reset_limit=1,
            ),
        ),
    )

    assert create_event.has_calls
