import pytest

from crm_hub.logic import state
from crm_hub.repositories import batch_sending


@pytest.mark.parametrize(
    'campaign_id, sending_id, status, result',
    [
        (1, '00000000000000000000000000000001', 'CANCELED', 200),
        (1, '00000000000000000000000000000002', 'CANCELED', 200),
        (1, '00000000000000000000000000000003', 'FINISHED', 200),
        (1, '00000000000000000000000000000004', 'ERROR', 200),
        (200, None, None, 404),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['init.sql'])
async def test_cancel(
        web_context,
        mockserver,
        web_app_client,
        campaign_id,
        sending_id,
        status,
        result,
):
    @mockserver.json_handler('/crm-scheduler/v1/stop_sending')
    async def _stop_scheduler(request):
        return mockserver.make_response(status=result, json={})

    response = await web_app_client.post(
        '/v1/communication/bulk/cancel', params={'campaign_id': campaign_id},
    )

    assert response.status == result
    if result == 200:
        storage = batch_sending.BatchSendingStorage(web_context)
        item = await storage.fetch(sending_id)
        assert item.state == status


@pytest.mark.parametrize(
    'campaign_id,group_id,result,status',
    [
        (1, 1, state.NEW, 200),
        (1, 2, state.PROCESSING, 200),
        (1, 3, state.FINISHED, 200),
        (1, 4, state.ERROR, 200),
        (1, 5, state.CANCELED, 200),
        (2, 1, state.FINISHED, 200),
        (3, 1, state.ERROR, 200),
        (4, 1, state.CANCELED, 200),
        (100, 100, None, 404),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['init.sql'])
async def test_status(web_app_client, campaign_id, group_id, result, status):
    response = await web_app_client.get(
        '/v1/communication/bulk/status',
        params={'campaign_id': campaign_id, 'group_id': group_id},
    )
    assert response.status == status

    if status == 200:
        response = await response.json()
        assert response['data'] == result
