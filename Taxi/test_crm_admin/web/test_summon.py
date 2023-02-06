# pylint: disable=unused-variable
import dataclasses

import pytest

from crm_admin import audience
from crm_admin import settings
from crm_admin import storage
from crm_admin.utils.state import state as state_module

SUMMON_USERS_V2_CFG = {
    'by_kind': {
        'common': [
            {
                'analysts': [],
                'idea_approvers': [],
                'final_approvers': [],
                'trend': 'Trend_0',
            },
            {
                'analysts': ['belokrylov-al'],
                'idea_approvers': [
                    'vnazarovat',
                    'esdomracheva',
                    'IlyaBorisov',
                ],
                'final_approvers': ['vnazarovat'],
                'trend': 'Trend_1',
            },
            {
                'final_approvers': ['vnazarovat-2'],
                'trend': 'Trend_1',
                'kind': 'Kind_3',
            },
            {
                'analysts': ['kind1_analyst'],
                'idea_approvers': ['kind1_idea'],
                'final_approvers': ['kind1_final'],
                'trend': 'Trend_2',
                'kind': 'Kind_1',
            },
            {
                'analysts': ['kind2_analyst'],
                'idea_approvers': ['kind2_idea'],
                'final_approvers': ['kind2_final'],
                'trend': 'Trend_2',
                'kind': 'Kind_2',
            },
            {
                'analysts': ['subkind1_analyst'],
                'idea_approvers': ['subkind1_idea'],
                'final_approvers': ['subkind1_final'],
                'trend': 'Trend_2',
                'kind': 'Kind_2',
                'subkind': 'Subkind_1',
            },
            {
                'analysts': ['subkind2_analyst'],
                'idea_approvers': ['subkind2_idea'],
                'final_approvers': ['subkind2_final'],
                'trend': 'Trend_2',
                'kind': 'Kind_2',
                'subkind': 'Subkind_2',
            },
        ],
    },
}

SUMMON_DRIVERS_CFG = {
    'by_kind': {
        'common': [
            {
                'analysts': ['common_kind_analyst'],
                'final_approvers': ['duty'],
                'idea_approvers': ['duty'],
                'kind': ['the_kind'],
            },
        ],
        'international': [],
    },
    'defaults': {
        'common': {
            'analysts': ['common_analyst'],
            'final_approvers': ['common_final'],
            'idea_approvers': ['common_idea'],
        },
        'international': {
            # 'analysts': ['int_analyst'], # bad config, but it's possible
            'final_approvers': ['int_final'],
            'idea_approvers': ['int_idea'],
        },
    },
}

SUMMON_LAVKAUSER_CFG = {
    'common': [
        {
            'analysts': [],
            'idea_approvers': [],
            'final_approvers': [],
            'trend': 'Trend_0',
        },
        {
            'analysts': ['belokrylov-al'],
            'idea_approvers': ['vnazarovat', 'esdomracheva', 'IlyaBorisov'],
            'final_approvers': ['vnazarovat'],
            'trend': 'Trend_1',
        },
        {
            'final_approvers': ['vnazarovat-2'],
            'trend': 'Trend_1',
            'kind': 'Kind_3',
        },
        {
            'analysts': ['kind1_analyst'],
            'idea_approvers': ['kind1_idea'],
            'final_approvers': ['kind1_final'],
            'trend': 'Trend_2',
            'kind': 'Kind_1',
        },
        {
            'analysts': ['kind2_analyst_lavka'],
            'idea_approvers': ['kind2_idea'],
            'final_approvers': ['kind2_final'],
            'trend': 'Trend_2',
            'kind': 'Kind_2',
        },
        {
            'analysts': ['subkind1_analyst'],
            'idea_approvers': ['subkind1_idea'],
            'final_approvers': ['subkind1_final'],
            'trend': 'Trend_2',
            'kind': 'Kind_2',
            'subkind': 'Subkind_1',
        },
        {
            'analysts': ['subkind2_analyst_lavka'],
            'idea_approvers': ['subkind2_idea'],
            'final_approvers': ['subkind2_final'],
            'trend': 'Trend_2',
            'kind': 'Kind_2',
            'subkind': 'Subkind_2',
        },
    ],
    'deli-israel': [{'final_approvers': ['israel_final'], 'trend': 'Trend_1'}],
}

CRM_ADMIN_SUMMON = {
    'regular_idea_approvers': {
        'message': (
            '{{logins}}. Регулярная кампания. Необходимо согласование идеи.'
        ),
        'users': ['idea', 'regular'],
    },
    'regular_final_approvers': {
        'message': (
            '{{logins}}. Регулярная кампания. Необходимо финальное '
            'согласование.'
        ),
        'users': ['final', 'regular'],
    },
}

CRM_ADMIN_SETTINGS = {
    'StartrekSettings': {
        'campaign_queue': 'CRMTEST',
        'creative_queue': 'CRMTEST',
        'idea_approved_statuses': ['В работе', 'Одобрено'],
        'target_statuses': ['Одобрено', 'Closed'],
        'unapproved_statuses': ['В работе', 'Открыт'],
    },
}

CRM_ADMIN_SUMMON_EFFICIENCY = {'push_limit': 1100, 'sms_limit': 6600}

COUNTRIES_COMMON = [
    'br_armenia',
    'arm',
    'br_azerbaijan',
    'aze',
    'br_belarus',
    'blr',
    'br_estonia',
    'est',
    'br_georgia',
    'geo',
    'br_kazakhstan',
    'kaz',
    'br_kyrgyzstan',
    'kgz',
    'kgs',
    'br_latvia',
    'lva',
    'br_lithuania',
    'ltu',
    'br_moldova',
    'mda',
    'br_russia',
    'rus',
    'br_ukraine',
    'ukr',
    'br_uzbekistan',
    'uzb',
    'tjk',
]

COUNTRIES_INTERNATIONAL = [
    'br_cote_divoire',
    'civ',
    'br_finland',
    'fin',
    'br_ghana',
    'gha',
    'br_israel',
    'isr',
    'br_romania',
    'rou',
    'br_serbia',
    'srb',
    'br_south_africa',
    'zaf',
    'usa',
    'ita',
    'cze',
    'fra',
    'bel',
    'swe',
    'gbr',
    'vnm',
    'prt',
    'pol',
    'are',
    'che',
    'esp',
    'chn',
    'dnk',
    'gua',
    'tun',
    'deu',
    'lux',
    'kor',
    'tur',
    'egy',
    'ind',
]

COUNTRIES_CFG = [
    # most of the tests use copy of such config located in
    # default/config.json in static folders of respective groups
    {'group_type': 'common', 'countries': COUNTRIES_COMMON},
    {'group_type': 'international', 'countries': COUNTRIES_INTERNATIONAL},
    {'group_type': 'deli-israel', 'countries': ['br_israel']},
]


@dataclasses.dataclass
class MockBatchCampaign:
    entity_type: str


@pytest.mark.config(
    CRM_ADMIN_SUMMON_USERS_V2=SUMMON_USERS_V2_CFG,
    CRM_ADMIN_SUMMON_EATSUSERS=SUMMON_USERS_V2_CFG,
    CRM_ADMIN_SUMMON_DRIVERS=SUMMON_DRIVERS_CFG,
    CRM_ADMIN_SUMMON_LAVKAUSERS=SUMMON_LAVKAUSER_CFG,
    CRM_ADMIN_SUMMON_EFFICIENCY=CRM_ADMIN_SUMMON_EFFICIENCY,
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.now('2020-03-20 10:00:00')
@pytest.mark.parametrize(
    'campaign_id, status, error_message, summonees',
    [
        (-1, 404, 'Campaign {campaign_id} was not found', None),
        (1, 404, 'Campaign {campaign_id} without trend.', None),
        (11, 404, 'Campaign {campaign_id} without trend.', None),
        (2, 404, 'analysts not found for campaign {campaign_id}', None),
        (10, 404, 'analysts not found for campaign {campaign_id}', None),
        (3, 200, None, ['belokrylov-al']),
        (9, 200, None, ['belokrylov-al']),
        (4, 200, None, ['common_kind_analyst']),
        (5, 200, None, ['common_analyst']),
        (6, 404, 'analysts not found for campaign {campaign_id}', None),
        (12, 200, None, ['kind2_analyst']),
        (13, 200, None, ['kind2_analyst', 'subkind2_analyst']),
        (22, 200, None, ['kind2_analyst_lavka']),
        (23, 200, None, ['kind2_analyst_lavka', 'subkind2_analyst_lavka']),
    ],
)
async def test_summon_approvers(
        web_app_client,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        campaign_id,
        status,
        error_message,
        summonees,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']
    url = st_settings['robot-crm-admin']['url'] + 'issues/CRMTEST-1/comments'

    @patch_aiohttp_session(url, 'POST')
    def patch_issue(*args, **kwargs):
        if summonees is not None:
            assert set(kwargs['json']['summonees']) == set(summonees)
            assert 'Не все условия для формирования' in kwargs['json']['text']
        return response_mock(json={})

    response = await web_app_client.post(
        '/v1/process/summon', params={'id': campaign_id},
    )
    assert response.status == status

    if error_message is not None:
        body = await response.json()
        assert body == {
            'message': error_message.format(campaign_id=campaign_id),
        }
    else:
        body = await response.text()
        assert body == ''
        assert patch_issue.calls

    if response.status == 200:
        resummon_response = await web_app_client.post(
            '/v1/process/summon', params={'id': campaign_id},
        )
        assert resummon_response.status == 404
        body = await resummon_response.json()
        assert body == {'message': 'Analysts already summoned.'}


@pytest.mark.config(
    CRM_ADMIN_SUMMON_USERS_V2=SUMMON_USERS_V2_CFG,
    CRM_ADMIN_SUMMON_EATSUSERS=SUMMON_USERS_V2_CFG,
    CRM_ADMIN_SUMMON_EFFICIENCY=CRM_ADMIN_SUMMON_EFFICIENCY,
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.now('2020-03-20 10:00:00')
@pytest.mark.parametrize(
    'campaign_id, entity_type', [(3, 'User'), (9, 'EatsUser')],
)
async def test_success_summon_idea_approvers(
        web_context,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        campaign_id,
        entity_type,
):
    ticket = 'CRMTEST-1'
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']
    url = st_settings['robot-crm-admin']['url'] + f'issues/{ticket}/comments'

    @patch_aiohttp_session(url, 'POST')
    def patch_issue(*args, **kwargs):
        assert sorted(kwargs['json']['summonees']) == [
            'IlyaBorisov',
            'esdomracheva',
            'vnazarovat',
        ]
        assert 'Для продолжения работы над кампанией' in kwargs['json']['text']
        return response_mock(json={})

    audience_cmp = audience.get_audience(
        MockBatchCampaign(entity_type=entity_type),
    )
    summoner = audience_cmp.summon(web_context, campaign_id)
    await summoner.summon_idea_approvers()

    assert patch_issue.calls


@pytest.mark.parametrize(
    'campaign_id,state,summonees,message,calls',
    [
        # Need approve
        (
            7,
            settings.SEGMENT_RESULT_STATE,
            ['idea', 'regular'],
            '@idea, @regular. Регулярная кампания. Необходимо согласование '
            'идеи.',
            True,
        ),
        (
            7,
            settings.PENDING_STATE,
            ['final', 'regular'],
            '@final, @regular. Регулярная кампания. Необходимо финальное '
            'согласование.',
            True,
        ),
        # Already in cycle
        (8, settings.SEGMENT_RESULT_STATE, None, None, False),
        (8, settings.PENDING_STATE, None, None, False),
    ],
)
@pytest.mark.config(
    CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS,
    CRM_ADMIN_SUMMON=CRM_ADMIN_SUMMON,
    CRM_ADMIN_SUMMON_EFFICIENCY=CRM_ADMIN_SUMMON_EFFICIENCY,
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.now('2020-03-20 10:00:00')
async def test_idea_approve_summon_on_regular_campaign(
        web_context,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        campaign_id,
        state,
        summonees,
        message,
        calls,
):
    ticket = 'CRMTEST-1'
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']
    url = st_settings['robot-crm-admin']['url'] + f'issues/{ticket}/comments'

    @patch_aiohttp_session(url, 'POST')
    def patch_issue(*args, **kwargs):
        if summonees:
            assert sorted(kwargs['json']['summonees']) == summonees
        assert kwargs['json']['text'] == message
        return response_mock(json={})

    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id)

    await state_module.cstate_try_update_without_save(
        web_context, campaign, [], state, None, None,
    )

    assert bool(patch_issue.calls) == calls


@pytest.mark.config(
    CRM_ADMIN_SUMMON_USERS_V2=SUMMON_USERS_V2_CFG,
    CRM_ADMIN_SUMMON_EATSUSERS=SUMMON_USERS_V2_CFG,
    CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS,
    CRM_ADMIN_SUMMON_LAVKAUSERS=SUMMON_LAVKAUSER_CFG,
    CRM_ADMIN_SUMMON_COUNTRIES=COUNTRIES_CFG,
    CRM_ADMIN_SUMMON_EFFICIENCY=CRM_ADMIN_SUMMON_EFFICIENCY,
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.now('2020-03-20 10:00:00')
@pytest.mark.parametrize(
    'campaign_id, status, error_message, summonees',
    [
        (-1, 404, 'Campaign {campaign_id} was not found', None),
        (1, 200, None, None),
        (11, 200, None, None),
        (2, 200, None, None),
        (10, 200, None, None),
        (3, 200, None, ['vnazarovat']),
        (9, 200, None, ['vnazarovat']),
        (12, 200, None, ['kind2_final']),
        (13, 200, None, ['kind2_final', 'subkind2_final']),
        (14, 200, None, ['vnazarovat']),
        (15, 200, None, None),
        (16, 200, None, ['kind2_final']),
        (17, 200, None, ['kind2_final', 'subkind2_final']),
        (18, 200, None, ['israel_final']),
        (19, 200, None, ['vnazarovat', 'israel_final']),
        (20, 200, None, ['vnazarovat', 'vnazarovat-2']),
        (21, 200, None, ['vnazarovat', 'vnazarovat-2']),
    ],
)
async def test_summon_final_approvers(
        web_app_client,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        campaign_id,
        status,
        error_message,
        summonees,
        patch,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']
    url = st_settings['robot-crm-admin']['url'] + 'issues/CRMTEST-1/comments'

    @patch_aiohttp_session(url, 'POST')
    def patch_issue(*args, **kwargs):
        if summonees is not None:
            assert set(kwargs['json']['summonees']) == set(summonees)
            assert (
                'Необходимо финальное согласование рассылки с'
                in kwargs['json']['text']
            )
        else:
            assert 'summonees' not in kwargs['json']
        return response_mock(json={})

    @patch(
        'crm_admin.utils.validation' '.groupings.summon_approver_validation',
    )
    async def validation_mock(*args, **kwargs):
        return []

    response = await web_app_client.post(
        '/v1/process/summon_approver', params={'id': campaign_id},
    )
    assert response.status == status

    if error_message is not None:
        body = await response.json()
        assert body == {
            'message': error_message.format(campaign_id=campaign_id),
        }
    else:
        body = await response.text()
        assert body == ''
        assert patch_issue.calls
