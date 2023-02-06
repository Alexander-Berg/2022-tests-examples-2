import pytest

from crm_admin import audience
from crm_admin import entity
from crm_admin import settings
from crm_admin import storage
from crm_admin.audience.base import summon_base as summon
from crm_admin.generated.service.swagger import models
from crm_admin.storage import group_adapters_v1
from test_crm_admin.utils import campaign as cutils

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
                'idea_approvers': ['approver_1', 'approver_2'],
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
            'final_approvers': ['default_int_final'],
            'idea_approvers': ['default_international_idea_approver'],
        },
    },
    'final_special': [
        {
            'approvers': ['uniq_int'],
            'limit': 3000,
            'type': 'unique_driver_id_international',
            'message': 'uniq_int message',
        },
        {
            'approvers': ['uniq_common'],
            'limit': 3000,
            'type': 'unique_driver_id_common',
            'message': 'uniq_common message',
        },
        {
            'approvers': ['newcomer_app'],
            'type': 'newcomer',
            'message': 'newcomer message',
        },
        {
            'approvers': ['sms_approver'],
            'limit': 650,
            'type': 'sms',
            'message': '[logins] sms more than [limit]',
        },
    ],
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


async def _prepare_segment(web_context, uniq_drivers):
    stats = models.api.SegmentStatInfo(
        size=3588,
        unique_drivers=uniq_drivers,
        global_control=0,
        global_control_unique_drivers=0,
        distribution=[],
    )

    db_segment = storage.DbSegment(web_context)
    segment = await db_segment.create(
        yql_shared_url='http://123.com',
        yt_table='hahn/yt_path',
        mode=entity.SegmentType.FILTER,
        control=settings.DEFAULT_CONTROL_VALUE,
        extra_columns=None,
        aggregate_info=stats,
    )

    return segment


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS={})
@pytest.mark.config(CRM_ADMIN_SUMMON_DUTY={})
@pytest.mark.now('2020-04-10 10:00:00')
async def test_empty_config(
        web_context, patch_aiohttp_session, response_mock, simple_secdist,
):
    campaign = await cutils.CampaignUtils.create_campaign(
        web_context, ticket=TICKET, country='br_russia', newcomer='exclude',
    )

    audience_cmp = audience.get_audience(campaign)
    summoner = audience_cmp.summon(web_context, campaign.campaign_id)
    with pytest.raises(summon.SummonNotFound) as e_info:
        await summoner.summon_idea_approvers()

    assert e_info.value.args[0] == 'config.CRM_ADMIN_SUMMON_DRIVERS is empty.'


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DUTY=CRM_ADMIN_SUMMON_DUTY)
@pytest.mark.now('2020-04-10 10:00:00')
async def test_country_from_common(
        web_context, patch_aiohttp_session, response_mock, simple_secdist,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert kwargs['json']['summonees'] == ['default_common_idea_approver']
        text = kwargs['json']['text']
        assert text.startswith(
            'Для продолжения работы над кампанией ожидаем '
            'согласования идеи от @default_common_idea_approver.',
        )
        return response_mock(json={})

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context, ticket=TICKET, country='br_russia', newcomer='exclude',
    )

    audience_cmp = audience.get_audience(campaign)
    summoner = audience_cmp.summon(web_context, campaign.campaign_id)
    await summoner.summon_idea_approvers()

    assert patch_issue.calls


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DUTY=CRM_ADMIN_SUMMON_DUTY)
@pytest.mark.now('2020-04-10 10:00:00')
async def test_country_from_international(
        web_context, patch_aiohttp_session, response_mock, simple_secdist,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert kwargs['json']['summonees'] == [
            'default_international_idea_approver',
        ]
        text = kwargs['json']['text']
        assert text.startswith(
            'Для продолжения работы над кампанией ожидаем '
            'согласования идеи от @default_international_idea_approver.',
        )
        return response_mock(json={})

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context, ticket=TICKET, country='br_israel', newcomer='exclude',
    )

    audience_cmp = audience.get_audience(campaign)
    summoner = audience_cmp.summon(web_context, campaign.campaign_id)
    await summoner.summon_idea_approvers()

    assert patch_issue.calls


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DUTY=CRM_ADMIN_SUMMON_DUTY)
@pytest.mark.now('2020-04-10 10:00:00')
async def test_country_from_common_and_international(
        web_context, patch_aiohttp_session, response_mock, simple_secdist,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert sorted(kwargs['json']['summonees']) == [
            'default_common_idea_approver',
            'default_international_idea_approver',
        ]
        return response_mock(json={})

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        ticket=TICKET,
        country=['br_russia', 'br_belarus', 'br_israel'],
        newcomer='exclude',
    )

    audience_cmp = audience.get_audience(campaign)
    summoner = audience_cmp.summon(web_context, campaign.campaign_id)
    await summoner.summon_idea_approvers()

    assert patch_issue.calls


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DUTY=CRM_ADMIN_SUMMON_DUTY)
@pytest.mark.now('2020-04-10 10:00:00')
async def test_without_country(
        web_context, patch_aiohttp_session, response_mock, simple_secdist,
):
    # User common if country is empty
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert kwargs['json']['summonees'] == ['default_common_idea_approver']
        text = kwargs['json']['text']
        assert text.startswith(
            'Для продолжения работы над кампанией ожидаем '
            'согласования идеи от @default_common_idea_approver.',
        )
        return response_mock(json={})

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context, ticket=TICKET, country='br_russia', newcomer='exclude',
    )

    audience_cmp = audience.get_audience(campaign)
    summoner = audience_cmp.summon(web_context, campaign.campaign_id)
    await summoner.summon_idea_approvers()

    assert patch_issue.calls


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DUTY=CRM_ADMIN_SUMMON_DUTY)
@pytest.mark.now('2020-04-10 10:00:00')
async def test_common_by_kind_intern_by_defaults(
        web_context, patch_aiohttp_session, response_mock, simple_secdist,
):
    # User common if country is empty
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert sorted(kwargs['json']['summonees']) == [
            'approver_1',
            'approver_2',
            'default_international_idea_approver',
        ]
        return response_mock(json={})

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        kind='by_kind',
        ticket=TICKET,
        country=['br_russia', 'br_belarus', 'br_israel'],
        newcomer='exclude',
    )

    audience_cmp = audience.get_audience(campaign)
    summoner = audience_cmp.summon(web_context, campaign.campaign_id)
    await summoner.summon_idea_approvers()

    assert patch_issue.calls


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DUTY=CRM_ADMIN_SUMMON_DUTY)
@pytest.mark.now('2020-04-10 10:00:00')
async def test_common_duty(
        web_context, patch_aiohttp_session, response_mock, simple_secdist,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert sorted(kwargs['json']['summonees']) == ['duty_user']
        return response_mock(json={})

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        kind='duty_kind',
        ticket=TICKET,
        country='br_russia',
        newcomer='exclude',
    )

    audience_cmp = audience.get_audience(campaign)
    summoner = audience_cmp.summon(web_context, campaign.campaign_id)
    await summoner.summon_idea_approvers()

    assert patch_issue.calls


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DUTY=CRM_ADMIN_SUMMON_DUTY)
@pytest.mark.now('2020-04-10 10:00:00')
async def test_final_special_unique_int(
        web_context, patch_aiohttp_session, response_mock, simple_secdist,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert sorted(kwargs['json']['summonees']) == [
            'default_int_final',
            'uniq_int',
        ]
        return response_mock(json={})

    segment = await _prepare_segment(web_context, 3600)

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        kind='duty_kind',
        ticket=TICKET,
        country='br_israel',
        segment_id=segment.segment_id,
        newcomer='exclude',
    )

    audience_cmp = audience.get_audience(campaign)
    summoner = audience_cmp.summon(web_context, campaign.campaign_id)
    await summoner.summon_final_approvers()

    assert patch_issue.calls


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DUTY=CRM_ADMIN_SUMMON_DUTY)
@pytest.mark.now('2020-04-10 10:00:00')
async def test_final_newcomer_include(
        web_context, patch_aiohttp_session, response_mock, simple_secdist,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert sorted(kwargs['json']['summonees']) == [
            'default_int_final',
            'newcomer_app',
        ]
        return response_mock(json={})

    segment = await _prepare_segment(web_context, 100)
    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        kind='duty_kind',
        ticket=TICKET,
        country='br_israel',
        segment_id=segment.segment_id,
        newcomer='include',
    )

    audience_cmp = audience.get_audience(campaign)
    summoner = audience_cmp.summon(web_context, campaign.campaign_id)
    await summoner.summon_final_approvers()

    assert patch_issue.calls


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DUTY=CRM_ADMIN_SUMMON_DUTY)
@pytest.mark.now('2020-04-10 10:00:00')
async def test_final_newcomer_empty(
        web_context, patch_aiohttp_session, response_mock, simple_secdist,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert sorted(kwargs['json']['summonees']) == [
            'default_int_final',
            'newcomer_app',
        ]
        return response_mock(json={})

    segment = await _prepare_segment(web_context, 100)
    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        kind='by_kind',
        ticket=TICKET,
        country='br_israel',
        segment_id=segment.segment_id,
    )

    audience_cmp = audience.get_audience(campaign)
    summoner = audience_cmp.summon(web_context, campaign.campaign_id)
    await summoner.summon_final_approvers()

    assert patch_issue.calls


# *****************************************************************************


async def _create_group(web_context, segment, total):
    params = models.api.FilterGroup(
        name='Default',
        limit=300,
        state='NEW',
        cities=[],
        intent='taxicrm_drivers',
        sender='taxi',
        channel='SMS',
        content='',
        locales=[],
        computed=models.api.NumberDict({'total': total}),
    )
    db_group = group_adapters_v1.DbGroup(web_context)
    return await db_group.create(
        segment_id=segment.segment_id,
        yql_shared_url='http://123.com/',
        params=params,
    )


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DUTY=CRM_ADMIN_SUMMON_DUTY)
@pytest.mark.now('2020-04-10 10:00:00')
async def test_final_special_sms_more_than_limit(
        web_context, patch_aiohttp_session, response_mock, simple_secdist,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert sorted(kwargs['json']['summonees']) == [
            'approvers',
            'final',
            'sms_approver',
        ]
        return response_mock(json={})

    segment = await _prepare_segment(web_context, 100)
    await _create_group(web_context, segment, 400)
    await _create_group(web_context, segment, 400)
    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        kind='by_kind',
        ticket=TICKET,
        country='br_russia',
        segment_id=segment.segment_id,
        newcomer='exclude',
    )

    audience_cmp = audience.get_audience(campaign)
    summoner = audience_cmp.summon(web_context, campaign.campaign_id)
    await summoner.summon_final_approvers()
    assert patch_issue.calls


# *****************************************************************************


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_SUMMON_DRIVERS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DUTY=CRM_ADMIN_SUMMON_DUTY)
@pytest.mark.now('2020-04-10 10:00:00')
async def test_final_special_sms_less_than_limit(
        web_context, patch_aiohttp_session, response_mock, simple_secdist,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/{TICKET}/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert sorted(kwargs['json']['summonees']) == ['approvers', 'final']
        return response_mock(json={})

    segment = await _prepare_segment(web_context, 100)
    await _create_group(web_context, segment, 100)
    await _create_group(web_context, segment, 100)

    campaign = await cutils.CampaignUtils.create_campaign(
        web_context,
        kind='by_kind',
        ticket=TICKET,
        country='br_russia',
        segment_id=segment.segment_id,
        newcomer='exclude',
    )

    audience_cmp = audience.get_audience(campaign)
    summoner = audience_cmp.summon(web_context, campaign.campaign_id)
    await summoner.summon_final_approvers()
    assert patch_issue.calls
