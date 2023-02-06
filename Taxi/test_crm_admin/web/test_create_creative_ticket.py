# pylint: disable=unused-variable,unused-argument

import pytest

from test_crm_admin.utils import audience_cfg


@pytest.mark.parametrize(
    'campaign_id,status',
    [
        (1, 200),  # a user campaign, OK
        (2, 200),  # a driver campaign, OK
        (3, 424),  # a driver campaign with a linked cretive ticket
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_create_creative_ticket(
        web_app_client, patch, campaign_id, status,
):
    @patch(
        'crm_admin.utils.startrek.startrek.TicketManager.create_creative_ticket',  # noqa E501
    )
    async def create_creative_ticket(campaing):
        return 'ticket_key'

    response = await web_app_client.post(
        '/v1/process/creative', params={'id': campaign_id},
    )
    assert response.status == status
    if status == 200:
        assert await response.json() == {'data': 'ticket_key'}

    response = await web_app_client.get(
        '/v1/campaigns/item', params={'id': campaign_id},
    )
    assert response.status == 200

    response = await response.json()
    assert 'creative' in response
    if status == 200:
        assert response['creative'] == 'ticket_key'
