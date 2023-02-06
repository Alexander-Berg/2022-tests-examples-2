# pylint: disable=unused-variable,invalid-name
import pytest


from crm_admin import entity
from crm_admin import settings
from crm_admin import storage

CAMPAIGN_COPIED_FIELDS = [
    'name',
    'specification',
    'entity_type',
    'trend',
    'kind',
    'subkind',
    'discount',
    'ticket',
    'settings',
    'extra_data',
    'extra_data_path',
    'creative',
    'test_users',
    'global_control',
    'com_politic',
    'efficiency',
    'tasks',
    'planned_start_date',
    'extra_data_key',
    'is_regular',
    'schedule',
    'regular_start_time',
    'regular_stop_time',
    'efficiency_start_time',
    'efficiency_stop_time',
    'motivation_methods',
]

CRM_ADMIN_GROUPS_V2 = {'all_on': True}

CRM_ADMIN_SETTINGS = {
    'StartrekSettings': {
        'campaign_queue': 'CRMTEST',
        'creative_queue': 'CRMTEST',
        'idea_approved_statuses': ['В работе', 'Одобрено'],
        'target_statuses': ['Одобрено', 'Closed'],
        'agreement_statuses': ['Согласование', 'Требует согласования'],
        'unapproved_statuses': ['В работе'],
    },
}


def check_response_campaign(
        response_campaign: dict, expected_campaign_dict: dict,
):
    for field, expected_value in expected_campaign_dict.items():
        if expected_value:
            assert field in response_campaign
            assert response_campaign[field] == expected_value
        else:
            assert not response_campaign.get(field, None)


async def check_db_campaign(context, root_id: int):
    db_campaign = storage.DbCampaign(context)

    draft_campaign = await db_campaign.fetch_by_version_state(
        root_id, settings.VersionState.DRAFT,
    )
    actual_campaign = await db_campaign.fetch_by_version_state(
        root_id, settings.VersionState.ACTUAL,
    )
    assert draft_campaign
    assert actual_campaign

    assert draft_campaign.owner_name == 'trusienkodv'
    assert draft_campaign.state == entity.CampaignDraftStates.PREPARING_DRAFT
    assert draft_campaign.parent_id == actual_campaign.campaign_id
    assert draft_campaign.root_id == root_id
    assert actual_campaign.child_id == draft_campaign.campaign_id
    assert not draft_campaign.is_active

    for field in CAMPAIGN_COPIED_FIELDS:
        actual_field = getattr(actual_campaign, field, None)
        draft_field = getattr(draft_campaign, field, None)
        assert actual_field == draft_field


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.parametrize(
    'parent_id, result', [(1, 200), (6, 404), (2, 400), (3, 400)],
)
async def test_process_draft(
        web_context, web_app_client, patch, load_json, parent_id, result,
):
    @patch('crm_admin.generated.service.stq_client.plugin.QueueClient.call')
    async def start_task(*args, **kwargs):
        pass

    @patch('crm_admin.utils.startrek.startrek.TicketManager.add_comment')
    async def add_comment(*args, **kwargs):
        pass

    owner = 'trusienkodv'
    response = await web_app_client.post(
        '/v1/campaigns/create_draft',
        params={'parent_id': parent_id},
        headers={'X-Yandex-Login': owner},
    )

    assert response.status == result
    if result == 200:
        assert start_task.calls
        assert add_comment.calls

        check_response_campaign(
            await response.json(), load_json('response.json')[str(parent_id)],
        )

        await check_db_campaign(web_context, parent_id)


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.parametrize('parent_id, result', [(4, 200)])
async def test_process_draft_with_cancel(
        web_context, web_app_client, patch, load_json, parent_id, result,
):
    @patch('crm_admin.generated.service.stq_client.plugin.QueueClient.call')
    async def start_task(*args, **kwargs):
        pass

    @patch('crm_admin.utils.startrek.startrek.TicketManager.add_comment')
    async def add_comment(*args, **kwargs):
        pass

    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(parent_id)
    old_draft_campaign_id = campaign.child_id

    owner = 'trusienkodv'
    response = await web_app_client.post(
        '/v1/campaigns/create_draft',
        params={'parent_id': parent_id},
        headers={'X-Yandex-Login': owner},
    )

    assert response.status == result
    if result == 200:
        assert start_task.calls
        assert add_comment.calls

        check_response_campaign(
            await response.json(), load_json('response.json')[str(parent_id)],
        )

        await check_db_campaign(web_context, parent_id)

        old_draft_campaign = await db_campaign.fetch(old_draft_campaign_id)

        assert old_draft_campaign.deleted_at
        assert old_draft_campaign.parent_id is None
