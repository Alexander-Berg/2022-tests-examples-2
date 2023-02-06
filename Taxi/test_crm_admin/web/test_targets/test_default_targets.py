# pylint: disable=redefined-outer-name,unused-variable,too-many-lines
import pytest

from crm_admin import entity
from test_crm_admin.utils import audience_cfg

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
    **audience_cfg.CRM_ADMIN_SETTINGS,
}

CRM_ADMIN_DEFAULT_TARGETS = {
    'DefaultTargets': [
        {'label': 'label_1', 'audiences': ['User']},
        {
            'label': 'label_2',
            'audiences': ['User', 'Driver'],
            'trends': ['trend1'],
        },
        {'label': 'label_3', 'audiences': ['User'], 'trends': ['trend2']},
        {'label': 'label_4', 'audiences': ['Driver'], 'trends': ['trend1']},
        {'label': 'label_5', 'trends': ['trend1']},
        {'label': 'label_6', 'trends': ['trend2']},
    ],
}


@pytest.mark.now('2021-05-05 05:05:05')
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.config(
    CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS,
    CRM_ADMIN_DEFAULT_TARGETS=CRM_ADMIN_DEFAULT_TARGETS,
)
async def test_create_campaign(
        web_context,
        web_app_client,
        load_json,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + 'issue', 'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={'key': 'new_ticket_key'})

    form = load_json('campaign_new.json')
    owner = 'user_owner'
    response = await web_app_client.post(
        '/v1/campaigns/item', json=form, headers={'X-Yandex-Login': owner},
    )

    assert response.status == 201

    query = """
    SELECT *
    FROM crm_admin.campaign_target_connection
    """

    async with web_context.pg.master_pool.acquire() as conn:
        rows = await conn.fetch(query)

    target_connections = [
        entity.CampaignTargetConnection.from_db(row) for row in rows
    ]

    assert {
        target_connection.target_id for target_connection in target_connections
    } == {1, 2, 5}


@pytest.mark.now('2021-05-05 05:05:05')
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.config(
    CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS,
    CRM_ADMIN_DEFAULT_TARGETS=CRM_ADMIN_DEFAULT_TARGETS,
)
async def test_get_default_targets(
        web_context,
        web_app_client,
        load_json,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + 'issue', 'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={'key': 'new_ticket_key'})

    form = load_json('campaign_new.json')
    owner = 'user_owner'
    response = await web_app_client.post(
        '/v1/campaigns/item', json=form, headers={'X-Yandex-Login': owner},
    )

    assert response.status == 201

    campaign_id = 1

    response = await web_app_client.get(
        f'/v1/campaigns/{campaign_id}/default_targets',
    )

    assert response.status == 200

    result: list = await response.json()
    result.sort(key=lambda target: target['id'])

    expected_result = [
        {'id': 1, 'is_important': True, 'name': 'name'},
        {'id': 2, 'is_important': True, 'name': 'name'},
        {'id': 5, 'is_important': False, 'name': 'name'},
    ]

    assert result == expected_result


@pytest.mark.now('2021-05-05 05:05:05')
@pytest.mark.pgsql('crm_admin', files=['init_default_reset.sql'])
@pytest.mark.config(
    CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS,
    CRM_ADMIN_DEFAULT_TARGETS={
        'DefaultTargets': [
            {'label': 'label_1', 'audiences': ['User']},
            {'label': 'label_5', 'audiences': ['User']},
        ],
    },
)
async def test_reset_to_default_targets(
        web_context, web_app_client, response_mock,
):
    expected_target_ids = {1, 5}
    campaign_id = 1

    response = await web_app_client.post(
        f'/v1/campaigns/{campaign_id}/reset_targets',
    )
    assert response.status == 200
    targets = await response.json()
    target_ids = {target['id'] for target in targets}
    assert expected_target_ids == target_ids

    response = await web_app_client.get(f'/v1/campaigns/{campaign_id}/targets')
    assert response.status == 200
    targets = await response.json()
    target_ids = {target['id'] for target in targets}
    assert expected_target_ids == target_ids
