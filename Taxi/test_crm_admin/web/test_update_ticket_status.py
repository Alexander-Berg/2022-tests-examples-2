# pylint: disable=unused-variable

import pytest

from crm_admin import settings
from test_crm_admin.utils import campaign as cutils

TICKET = 'CRMTEST-242'

CRM_ADMIN_SETTINGS = {
    'StartrekSettings': {
        'campaign_queue': 'CRMTEST',
        'creative_queue': 'CRMTEST',
        'idea_approved_statuses': [
            'idea_approved_state',
            'final_approved_state',
        ],
        'target_statuses': ['final_approved_state'],
        'unapproved_statuses': ['unapproved_state'],
    },
}


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
async def test_do_not_change_state_on_idea(web_context, web_app_client):
    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        ticket=TICKET,
        ticket_status='ticket_status',
        state=settings.SEGMENT_RESULT_STATE,
    )

    t_status = 'other_state'
    data = {'ticket': TICKET, 'status': t_status}
    response = await web_app_client.put(
        f'/v1/ticket/status?id={campaign.campaign_id}', json=data,
    )
    assert response.status == 200

    campaign = await cutils.CampaignUtils.fetch_campaign(
        web_context, campaign.campaign_id,
    )
    assert campaign.ticket_status == t_status
    assert campaign.state == settings.SEGMENT_RESULT_STATE


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
async def test_change_state_on_idea(web_context, web_app_client):
    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        ticket=TICKET,
        ticket_status='ticket_status',
        state=settings.SEGMENT_RESULT_STATE,
    )

    t_status = 'idea_approved_state'
    data = {'ticket': TICKET, 'status': t_status}
    response = await web_app_client.put(
        f'/v1/ticket/status?id={campaign.campaign_id}', json=data,
    )
    assert response.status == 200

    campaign = await cutils.CampaignUtils.fetch_campaign(
        web_context, campaign.campaign_id,
    )
    assert campaign.ticket_status == t_status
    assert campaign.state == settings.GROUPS_READY_FOR_CALCULATION


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
async def test_do_not_change_state_on_pending(web_context, web_app_client):
    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        ticket=TICKET,
        ticket_status='ticket_status',
        state=settings.PENDING_STATE,
    )

    t_status = 'idea_approved_state'
    data = {'ticket': TICKET, 'status': t_status}
    response = await web_app_client.put(
        f'/v1/ticket/status?id={campaign.campaign_id}', json=data,
    )
    assert response.status == 200

    campaign = await cutils.CampaignUtils.fetch_campaign(
        web_context, campaign.campaign_id,
    )
    assert campaign.ticket_status == t_status
    assert campaign.state == settings.PENDING_STATE


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
async def test_change_state_on_pending(web_context, web_app_client):
    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        ticket=TICKET,
        ticket_status='ticket_status',
        state=settings.PENDING_STATE,
    )

    t_status = 'final_approved_state'
    data = {'ticket': TICKET, 'status': t_status}
    response = await web_app_client.put(
        f'/v1/ticket/status?id={campaign.campaign_id}', json=data,
    )
    assert response.status == 200

    campaign = await cutils.CampaignUtils.fetch_campaign(
        web_context, campaign.campaign_id,
    )
    assert campaign.ticket_status == t_status
    assert campaign.state == settings.APPROVED_STATE


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
async def test_change_state_on_unapprove(web_context, web_app_client):
    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        ticket=TICKET,
        ticket_status='ticket_status',
        state=settings.APPROVED_STATE,
    )

    t_status = 'unapproved_state'
    data = {'ticket': TICKET, 'status': t_status}
    response = await web_app_client.put(
        f'/v1/ticket/status?id={campaign.campaign_id}', json=data,
    )
    assert response.status == 200

    campaign = await cutils.CampaignUtils.fetch_campaign(
        web_context, campaign.campaign_id,
    )
    assert campaign.ticket_status == t_status
    assert campaign.state == settings.GROUPS_RESULT_STATE
