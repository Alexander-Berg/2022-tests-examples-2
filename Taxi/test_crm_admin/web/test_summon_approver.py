# pylint: disable=unused-variable

import pytest

from crm_admin import entity
from crm_admin import settings
from crm_admin import storage
from crm_admin.generated.service.swagger import models
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

CRM_ADMIN_SUMMON_DRIVERS = {
    'defaults': {
        'common': {
            'final_approvers': ['default_final_approvers'],
            'idea_approvers': ['default_common_idea_approver'],
        },
        'international': {
            'final_approvers': ['default_int_final'],
            'idea_approvers': ['default_international_idea_approver'],
        },
    },
}


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
async def test_bad_state_for_summon(
        web_context,
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        simple_secdist,
        patch,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert kwargs['json']['summonees'] == ['default_final_approvers']
        return response_mock(json={})

    @patch(
        'crm_admin.utils.validation' '.groupings.summon_approver_validation',
    )
    async def validation_mock(*args, **kwargs):
        return []

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        ticket=TICKET,
        ticket_status='ticket_status',
        state=settings.SEGMENT_RESULT_STATE,
    )

    response = await web_app_client.post(
        f'/v1/process/summon_approver?id={campaign.campaign_id}',
    )

    assert not patch_issue.calls  # Not summon
    assert response.status == 400
    data = await response.json()
    assert 'Campaign state' in data['message']

    campaign = await cutils.CampaignUtils.fetch_campaign(
        web_context, campaign.campaign_id,
    )
    assert campaign.state == settings.SEGMENT_RESULT_STATE


# *****************************************************************************


@pytest.mark.config(
    CRM_ADMIN_VERIFY_SEND_PERMISSIONS=[
        {
            'entity': 'Driver',
            'permissions': {
                'everybody_can_test': False,
                'users_can_test': ['success_user'],
            },
        },
    ],
    CRM_ADMIN_GROUPS_V2={'all_on': True},
    CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS,
    CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS,
)
@pytest.mark.parametrize(
    'yandex_login, status',
    [('success_user', 200), ('unsuccess_user', 403), (None, 403)],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_validate_user_login_for_summon(
        web_context,
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        simple_secdist,
        patch,
        yandex_login,
        status,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert kwargs['json']['summonees'] == ['default_final_approvers']
        return response_mock(json={})

    @patch(
        'crm_admin.utils.validation' '.groupings.summon_approver_validation',
    )
    async def validation_mock(*args, **kwargs):
        return []

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        ticket=TICKET,
        ticket_status='unapproved_state',
        state=settings.VERIFY_RESULT_STATE,
        entity='Driver',
        segment_id=1,
    )

    headers = {'X-Yandex-Login': yandex_login} if yandex_login else None
    campaign_id = campaign.campaign_id

    response = await web_app_client.post(
        '/v1/process/summon_approver',
        headers=headers,
        params={'id': campaign_id},
    )

    assert response.status == status


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
async def test_summon(
        web_context,
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        simple_secdist,
        patch,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert kwargs['json']['summonees'] == ['default_final_approvers']
        return response_mock(json={})

    @patch(
        'crm_admin.utils.validation' '.groupings.summon_approver_validation',
    )
    async def validation_mock(*args, **kwargs):
        return []

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        ticket=TICKET,
        ticket_status='unapproved_state',
        state=settings.VERIFY_RESULT_STATE,
    )

    response = await web_app_client.post(
        f'/v1/process/summon_approver?id={campaign.campaign_id}',
    )

    assert patch_issue.calls
    assert response.status == 200

    campaign = await cutils.CampaignUtils.fetch_campaign(
        web_context, campaign.campaign_id,
    )
    assert campaign.state == settings.PENDING_STATE


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
async def test_auto_appove(
        web_context,
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        simple_secdist,
        patch,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert kwargs['json']['summonees'] == ['default_final_approvers']
        return response_mock(json={})

    @patch(
        'crm_admin.utils.validation' '.groupings.summon_approver_validation',
    )
    async def validation_mock(*args, **kwargs):
        return []

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        ticket=TICKET,
        ticket_status='final_approved_state',
        state=settings.VERIFY_RESULT_STATE,
    )

    response = await web_app_client.post(
        f'/v1/process/summon_approver?id={campaign.campaign_id}',
    )

    assert not patch_issue.calls  # No call, auto_approve
    assert response.status == 200

    campaign = await cutils.CampaignUtils.fetch_campaign(
        web_context, campaign.campaign_id,
    )
    assert campaign.state == settings.APPROVED_STATE


@pytest.mark.parametrize(
    'is_regular, channel, is_ok',
    [(True, None, False), (True, 'PUSH', True), (False, None, True)],
)
@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
async def test_group_channels(
        web_context,
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        simple_secdist,
        is_regular,
        channel,
        is_ok,
        patch,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={})

    @patch(
        'crm_admin.utils.validation' '.groupings.summon_approver_validation',
    )
    async def validation_mock(*args, **kwargs):
        return []

    db_segment = storage.DbSegment(web_context)
    segment = await db_segment.create(
        yql_shared_url='yql_shared_url',
        yt_table='yt_table',
        mode=entity.segment.SegmentType.SHARED,
        control=10,
    )

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        kind='kind',
        ticket=TICKET,
        ticket_status='unapproved_state',
        state=settings.VERIFY_RESULT_STATE,
        segment_id=segment.segment_id,
        is_regular=is_regular,
    )

    db_groups = storage.DbGroup(web_context)
    for channel_name in ['PUSH', channel]:
        await db_groups.create(
            segment_id=campaign.segment_id,
            yql_shared_url='yql_shared_url',
            params=models.api.ShareGroup(
                name='a', share=0.1, channel=channel_name,
            ),
        )

    response = await web_app_client.post(
        '/v1/process/summon_approver', params={'id': campaign.campaign_id},
    )

    assert patch_issue.calls
    if is_ok:
        assert response.status == 200
    else:
        assert response.status == 400


@pytest.mark.config(
    CRM_ADMIN_GROUPS_V2={'all_on': True},
    CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS,
    CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS,
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_tags_without_creative_validate_for_summon(
        web_context,
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        simple_secdist,
        patch,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert kwargs['json']['summonees'] == ['default_final_approvers']
        return response_mock(json={})

    @patch(
        'crm_admin.utils.validation.extra_data_validators.'
        'validate_personalization_params',
    )
    async def validate_personalization_mock(*args, **kwargs):
        return []

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        ticket=TICKET,
        ticket_status='unapproved_state',
        state=settings.VERIFY_RESULT_STATE,
        entity='Driver',
        segment_id=1,
    )

    campaign_id = campaign.campaign_id

    response = await web_app_client.post(
        '/v1/process/summon_approver', params={'id': campaign_id},
    )

    assert response.status == 400
