# pylint: disable=unused-variable

import pytest

from crm_admin import settings
from crm_admin import storage
from crm_admin.generated.service.swagger import models

TICKET = 'CRMTEST-242'

CRM_ADMIN_SETTINGS = {
    'StartrekSettings': {
        'campaign_queue': 'CRMTEST',
        'creative_queue': 'CRMTEST',
        'idea_approved_statuses': [
            'idea_approved_state',
            'final_approved_state',
        ],
        'draft_approved_statuses': ['draft_approved_state'],
        'target_statuses': ['final_approved_state'],
        'unapproved_statuses': ['unapproved_state'],
    },
}


async def _prepare_campaign(
        web_context,
        kind,
        country=None,
        ticket_status=None,
        segment_id=None,
        state=None,
        is_regular=None,
        is_active=None,
        version_info=None,
):
    db_campaign = storage.DbCampaign(web_context)
    data = models.api.CampaignInfo(
        name='name',
        specification='specification',
        entity='Driver',
        trend='trend',
        kind=kind,
        discount=False,
        version_info=version_info,
    )
    campaign = await db_campaign.create(data, 'pytest')
    campaign.ticket = TICKET
    campaign.ticket_status = ticket_status
    campaign.segment_id = segment_id
    campaign.state = state
    campaign.is_regular = is_regular
    campaign.is_active = is_active
    if country:
        if isinstance(country, str):
            country = [country]
        campaign.settings = [
            models.api.FilterFieldInfo(field_id='country', value=country),
        ]
    await db_campaign.update(campaign)
    await db_campaign.update_state(campaign)
    return campaign


async def _fetch_campaign(web_context, campaign_id):
    db_campaign = storage.DbCampaign(web_context)
    return await db_campaign.fetch(campaign_id)


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
async def test_change_state_on_unapproved(web_context, web_app_client):
    campaign = await _prepare_campaign(
        web_context,
        kind='other_kind',
        ticket_status='ticket_status',
        state=settings.PENDING_STATE,
        version_info=models.api.VersionInfo(
            version_state=settings.VersionState.DRAFT,
        ),
    )

    t_status = 'unapproved_state'
    data = {'ticket': TICKET, 'status': t_status}
    response = await web_app_client.put(f'/v1/ticket/status', json=data)
    assert response.status == 200

    campaign = await _fetch_campaign(web_context, campaign.campaign_id)
    assert campaign.ticket_status == t_status
    assert campaign.state == settings.GROUPS_RESULT_STATE


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
async def test_change_ticket_statuses(web_context, web_app_client):
    actual_campaign = await _prepare_campaign(
        web_context,
        kind='other_kind',
        ticket_status='ticket_status',
        state=settings.REGULAR_SCHEDULED,
        version_info=models.api.VersionInfo(
            version_state=settings.VersionState.ACTUAL,
        ),
    )

    draft_campaign = await _prepare_campaign(
        web_context,
        kind='other_kind',
        ticket_status='ticket_status',
        state=settings.PENDING_STATE,
        version_info=models.api.VersionInfo(
            version_state=settings.VersionState.DRAFT,
        ),
    )

    t_status = 'final_approved_state'
    data = {'ticket': TICKET, 'status': t_status}
    response = await web_app_client.put(f'/v1/ticket/status', json=data)
    assert response.status == 200

    actual_campaign = await _fetch_campaign(
        web_context, actual_campaign.campaign_id,
    )
    draft_campaign = await _fetch_campaign(
        web_context, draft_campaign.campaign_id,
    )

    assert actual_campaign.ticket_status == t_status
    assert actual_campaign.state == settings.REGULAR_SCHEDULED

    assert draft_campaign.ticket_status == t_status
    assert draft_campaign.state == settings.APPROVED_STATE
