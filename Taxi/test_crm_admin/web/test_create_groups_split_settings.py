import pytest

from crm_admin import storage

CRM_ADMIN_GROUPS_V2 = {'all_on': True}


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.parametrize(
    'campaign_id, request_id, result_code',
    [
        (1, '1', 200),
        (2, '2', 200),
        (3, '3', 200),
        (4, '4', 200),
        (5, '1', 424),
        (1, '5', 400),
        (6, '1', 404),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_create_groups(
        web_context,
        web_app_client,
        load_json,
        campaign_id,
        request_id,
        result_code,
):
    request_data = load_json('requests.json')[request_id]
    expected_result = load_json('results.json')[request_id]

    response = await web_app_client.post(
        '/v1/campaigns/groups/split_settings',
        params={'id': campaign_id},
        json=request_data,
    )

    assert response.status == result_code
    if result_code != 200:
        return

    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id)

    db_segment = storage.DbSegment(web_context)
    segment = await db_segment.fetch(campaign.segment_id)

    assert segment.control == expected_result['control']
    assert segment.mode.value == expected_result['mode']

    db_group = storage.DbGroup(web_context)
    groups = await db_group.fetch_by_segment(campaign.segment_id)

    serialized_groups_params = [group.params.serialize() for group in groups]

    assert expected_result['groups'] == serialized_groups_params
