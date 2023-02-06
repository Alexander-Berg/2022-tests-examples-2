# pylint: disable=unused-argument,unused-variable

import pytest

from crm_admin.utils.startrek import startrek
from test_crm_admin.utils import campaign as campaign_utils

TEST_QUEUE = 'CRMTEST'
CRM_ADMIN_TEST_SETTINGS = {
    'NirvanaSettings': {
        'instance_id': '618c35c0-8a4d-4b61-9ebf-856d7359dfca',
        'workflow_id': '8bff6765-9fe2-484c-99a7-149cf2b90ac9',
        'workflow_retry_period': 60,
        'workflow_timeout': 3600,
    },
    'StartrekSettings': {
        'campaign_queue': 'CRMTEST',
        'target_statuses': ['target_status'],
        'idea_approved_statuses': ['target_status'],
        'unapproved_statuses': ['В работе'],
    },
}
CRM_ADMIN_AUDIENCES_SETTINGS_V2 = {
    'Driver': {
        'directional_config': {
            'creative_ticket_queue': 'CRMTEST',
            'children': {
                'summon_trend': {
                    'children': {
                        'summon_kind': {
                            'creative_ticket_summon_enabled': True,
                            'creative_ticket_summon_users': [
                                'testuser1',
                                'testuser2',
                            ],
                            'creative_ticket_summon_text': 'hey {{users}}',
                        },
                    },
                },
            },
        },
    },
}


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
async def test_create_ticket(web_context, patch, load_json):
    summary = 'TEST summary'
    description = 'test description'

    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    async def _create_ticket(smr, queue, desc, followers, tags, links):
        ticket = load_json('ticket_1.json')
        return ticket

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def _create_comment(ticket, text, summonees):
        ticket = load_json('ticket_1.json')
        return ticket

    campaign = await campaign_utils.CampaignUtils.create_campaign(
        web_context=web_context,
        campaign_id=1,
        name=summary,
        specification=description,
        entity_type='User',
        trend='trend',
        kind='kind',
        subkind='subkind',
        discount=True,
        state='State',
        owner_name='Owner_name',
    )

    st_adapter = startrek.TicketManager(web_context)
    ticket_key = await st_adapter.create_ticket(campaign)
    assert ticket_key == 'CRMTEST-1'


async def test_get_ticket(web_context, patch, load_json):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _(_):
        return load_json('ticket_1.json')

    ticket_key = 'CRMTEST-1'
    st_adapter = startrek.TicketManager(web_context)
    ticket_info = await st_adapter.get_ticket(ticket_key)
    assert ticket_info['key'] == ticket_key


async def test_get_ticket_status(web_context, patch, load_json):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _(_):
        return load_json('ticket_1.json')

    ticket_key = 'CRMTEST-1'
    st_adapter = startrek.TicketManager(web_context)
    ticket_status = await st_adapter.get_ticket_status(ticket_key)
    assert ticket_status['key'] == 'readyForTest'


async def test_get_ticket_status_key(web_context, patch, load_json):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _(_):
        return load_json('ticket_1.json')

    ticket_key = 'CRMTEST-1'
    st_adapter = startrek.TicketManager(web_context)
    ticket_status_key = await st_adapter.get_ticket_status_key(ticket_key)
    assert ticket_status_key == 'readyForTest'


@pytest.mark.config(
    CRM_ADMIN_AUDIENCES_SETTINGS_V2=CRM_ADMIN_AUDIENCES_SETTINGS_V2,
)
async def test_create_creative_ticket(web_context, patch):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    async def create_ticket(**kwargs):
        return dict(key='ticket_key')

    campaign = await campaign_utils.CampaignUtils.create_campaign(
        web_context=web_context,
        campaign_id=1,
        name='summary',
        specification='description',
        entity_type='Driver',
        trend='trend',
        kind='kind',
        subkind='subkind',
        discount=True,
        state='State',
        owner_name='username',
        ticket='campaign_ticket',
    )

    ticket_manager = startrek.TicketManager(web_context)
    ticket_key = await ticket_manager.create_creative_ticket(campaign)
    assert ticket_key == 'ticket_key'

    ticket_params = create_ticket.call['kwargs']
    unique_ticked_id = f'crm-admin/unittests/{campaign.campaign_id}/creative'
    assert ticket_params['unique'] == unique_ticked_id


@pytest.mark.config(
    CRM_ADMIN_AUDIENCES_SETTINGS_V2=CRM_ADMIN_AUDIENCES_SETTINGS_V2,
)
async def test_create_creative_ticket_summons(web_context, patch):

    ticket_key = 'ticket_key'

    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    async def create_ticket(**kwargs):
        return dict(key=ticket_key)

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(**kwargs):
        return {}

    campaign = await campaign_utils.CampaignUtils.create_campaign(
        web_context=web_context,
        campaign_id=1,
        name='summary',
        specification='description',
        entity_type='Driver',
        trend='summon_trend',
        kind='summon_kind',
        subkind='subkind',
        state='State',
        owner_name='username',
        ticket='campaign_ticket',
        ticket_status=None,
    )

    ticket_manager = startrek.TicketManager(web_context)
    ticket_key = await ticket_manager.create_creative_ticket(campaign)

    assert create_comment.call['kwargs'] == {
        'ticket': ticket_key,
        'text': 'hey @testuser1, @testuser2',
        'summonees': ['testuser1', 'testuser2'],
    }
