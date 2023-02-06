import pytest

from crm_admin import settings
from crm_admin.utils.state import state
from test_crm_admin.utils import campaign as cutils

# More specs for summon can be found in test_summon_idea_for_driver.py
TICKET = 'CRMTEST-242'

CRM_ADMIN_SETTINGS = {
    'NirvanaSettings': {
        'instance_id': '99192650-8fd2-4f0d-8bd5-a28188ed9f9b',
        'segment_max_size': 2000000,
        'workflow_id': '8bff6765-9fe2-484c-99a7-149cf2b90ac9',
        'workflow_retry_period': 60,
        'workflow_timeout': 86400,
    },
    'SparkSettings': {
        'discovery_path': '//home/taxi-dwh-dev/test/spark-discovery',
    },
    'StartrekSettings': {
        'campaign_queue': 'CRMTEST',
        'creative_queue': 'CRMTEST',
        'idea_approved_statuses': ['В работе', 'Одобрено'],
        'target_statuses': ['Одобрено', 'Closed'],
        'unapproved_statuses': ['В работе'],
    },
}

CRM_ADMIN_SUMMON_DRIVERS = {
    'by_kind': {
        'common': [
            {
                'final_approvers': ['final', 'approvers'],
                'idea_approvers': ['approver_1', 'duty'],
                'kind': ['by_kind'],
            },
            {
                'final_approvers': ['duty'],
                'idea_approvers': ['duty'],
                'kind': ['duty_kind'],
            },
        ],
    },
    'defaults': {
        'common': {
            'final_approvers': ['default_final_approvers'],
            'idea_approvers': ['default_common_idea_approver'],
        },
        'international': {
            'final_approvers': ['esdomracheva'],
            'idea_approvers': ['default_international_idea_approver'],
        },
    },
}

CRM_ADMIN_SUMMON_DUTY = {
    'drivers': [
        {
            'duty': 'duty_user',
            'end_date': '2020-04-12T23:59:59+03:00',
            'start_date': '2020-04-01T00:00:00+03:00',
        },
        {
            'duty': 'verush',
            'end_date': '2020-04-20T23:59:59+00:00',
            'start_date': '2020-04-13T00:00:00+03:00',
        },
    ],
}


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS={})
@pytest.mark.config(CRM_ADMIN_SUMMON_DUTY={})
@pytest.mark.now('2020-04-10 10:00:00')
async def test_empty_config(
        web_context, patch_aiohttp_session, response_mock, simple_secdist,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert (
            kwargs['json']['text']
            == 'Расчет сегмента успешно завершен. Необходимо согласовать идею.'
        )
        return response_mock(json={})

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context, ticket=TICKET, ticket_status='READY', country='br_russia',
    )

    await state.cstate_try_update_without_save(
        web_context, campaign, [], settings.SEGMENT_RESULT_STATE, None, None,
    )

    assert patch_issue.calls
    assert campaign.state == settings.SEGMENT_RESULT_STATE


# **********************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DUTY=CRM_ADMIN_SUMMON_DUTY)
@pytest.mark.now('2020-04-10 10:00:00')
async def test_auto_idea_approve(
        web_context, patch_aiohttp_session, response_mock, simple_secdist,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={})

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        ticket=TICKET,
        ticket_status='В работе',
        country='br_russia',
    )

    await state.cstate_try_update_without_save(
        web_context, campaign, [], settings.SEGMENT_RESULT_STATE, None, None,
    )

    # State changed to 'groups_ready'
    assert not patch_issue.calls
    assert campaign.state == settings.GROUPS_READY_FOR_CALCULATION


# **********************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DUTY=CRM_ADMIN_SUMMON_DUTY)
@pytest.mark.now('2020-04-10 10:00:00')
async def test_auto_final_approve_on_groups_ready(
        web_context, patch_aiohttp_session, response_mock, simple_secdist,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={})

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        ticket=TICKET,
        ticket_status='Одобрено',
        country='br_russia',
    )

    await state.cstate_try_update_without_save(
        web_context, campaign, [], settings.GROUPS_RESULT_STATE, None, None,
    )

    # State changed to 'groups_ready'
    assert not patch_issue.calls
    assert campaign.state == settings.APPROVED_STATE


# **********************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DUTY=CRM_ADMIN_SUMMON_DUTY)
@pytest.mark.now('2020-04-10 10:00:00')
async def test_auto_final_approve_on_verify_ready(
        web_context, patch_aiohttp_session, response_mock, simple_secdist,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={})

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        ticket=TICKET,
        ticket_status='Одобрено',
        country='br_russia',
    )

    await state.cstate_try_update_without_save(
        web_context, campaign, [], settings.VERIFY_RESULT_STATE, None, None,
    )

    # State changed to 'groups_ready'
    assert not patch_issue.calls
    assert campaign.state == settings.APPROVED_STATE


# **********************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DUTY=CRM_ADMIN_SUMMON_DUTY)
@pytest.mark.now('2020-04-10 10:00:00')
async def test_country_from_common_and_international(
        web_context, patch_aiohttp_session, response_mock, simple_secdist,
):
    # Summary. by_king and duty for common, default for international
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert sorted(kwargs['json']['summonees']) == [
            'approver_1',
            'default_international_idea_approver',
            'duty_user',
        ]
        return response_mock(json={})

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        kind='by_kind',
        ticket=TICKET,
        country=['br_russia', 'br_belarus', 'br_israel'],
    )

    await state.cstate_try_update_without_save(
        web_context, campaign, [], settings.SEGMENT_RESULT_STATE, None, None,
    )

    assert patch_issue.calls
    assert campaign.state == settings.SEGMENT_RESULT_STATE
