import pytest

from taxi.clients import startrack

from test_taxi_config_schemas.configs import common


@pytest.mark.parametrize(
    'name,data,status',
    [
        (
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
            {
                'current_value': 100,
                'comment': 'test_comment_1',
                'related_ticket': 'GOOD_TICKET',
            },
            200,
        ),
        (
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
            {
                'current_value': 100,
                'comment': 'test_comment_1',
                'related_ticket': 'BAD_TICKET',
            },
            400,
        ),
        (
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
            {
                'current_value': 200,
                'comment': 'test_comment_1',
                'related_ticket': 'GOOD_TICKET',
            },
            409,
        ),
        (
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT_2',
            {
                'current_value': 100,
                'comment': 'test_comment_1',
                'related_ticket': 'GOOD_TICKET',
            },
            404,
        ),
    ],
)
@pytest.mark.custom_patch_configs_by_group(configs=common.CONFIGS)
@pytest.mark.usefixtures('patch_call_command', 'update_schemas_cache')
async def test_save_comment_or_ticket(
        patch,
        web_context,
        web_app_client,
        name,
        data,
        status,
        patcher_tvm_ticket_check,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket, *args, **kwargs):
        if ticket == 'BAD_TICKET':
            raise startrack.BaseError

    patcher_tvm_ticket_check('config-schemas')
    response = await web_app_client.post(
        f'/v1/configs/{name}/comment_or_ticket/',
        headers={'X-Ya-Service-Ticket': 'good'},
        json=data,
    )
    assert response.status == status, await response.text()
    if status == 200:
        doc = await web_context.mongo.config.find_one({'_id': name})
        if 'comment' in data:
            assert doc.get('c') == data['comment']
        if 'related_ticket' in data:
            assert doc.get('t') == data['related_ticket']
        if 'team' in data:
            assert doc.get('tm') == data['team']
