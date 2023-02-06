from aiohttp import web
import pytest

from crm_admin import storage

CRM_ADMIN_GROUPS_V2 = {'all_on': True}

CRM_ADMIN_AUDIENCES_SETTINGS = (
    {'id': 'User', 'local_time_enabled': True, 'promocodes_enabled': True},
)


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.parametrize(
    'file, id_, result',
    [('group.json', 6, 200), ('campaign_empty.json', 1, 404)],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_retrieve_statistic(
        web_app_client, load_json, file, id_, result,
):
    existing_stat = load_json(file)
    response = await web_app_client.get(
        '/v1/campaigns/stat', params={'id': id_},
    )
    assert response.status == result
    if response.status == 200:
        retrieved_stat = await response.json()
        assert existing_stat == retrieved_stat


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.parametrize(
    'entity, values',
    [
        (
            'User',
            [
                {'label': 'PUSH', 'value': 'PUSH', 'is_dated': False},
                {'label': 'PROMO_FS', 'value': 'promo.fs', 'is_dated': True},
            ],
        ),
        ('Driver', [{'label': 'PUSH', 'value': 'PUSH', 'is_dated': False}]),
    ],
)
async def test_channels_list(web_app_client, entity, values):
    response = await web_app_client.get(
        '/v1/dictionaries/channels', params={'entity': entity},
    )
    assert response.status == 200
    retrieved_channels = await response.json()
    for value in values:
        assert value in retrieved_channels


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.parametrize(
    'file, id_, result',
    [
        ('group_update_filter.json', 6, 200),
        ('group_update_share.json', 7, 200),
        ('group_update_filter.json', 100, 404),
        ('group_update_share.json', 10, 200),
        ('group_update_value.json', 6, 200),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_create_groups(
        web_context, web_app_client, load_json, file, id_, result,
):
    new_groups = load_json(file)
    response = await web_app_client.post(
        '/v2/campaigns/groups/item', params={'id': id_}, json=new_groups,
    )
    assert response.status == result
    if result != 200:
        return

    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(id_)
    db_group = storage.DbGroup(web_context)
    groups = await db_group.fetch_by_segment(campaign.segment_id)
    assert len(groups) == len(new_groups['groups'])

    # yql_shared_url should be reset when a group is re-created
    assert all(g.yql_shared_url is None for g in groups)


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.parametrize(
    'file, id_, mode, result',
    [
        ('group_update_share.json', 6, 'Share', 200),
        ('group_update_filter.json', 7, 'Filter', 200),
        ('group_update_share_default.json', 8, 'Share', 200),
        ('group_update_filter_default.json', 9, 'Filter', 200),
        ('group_update_share.json', 100, 'Share', 404),
        ('group_share_drivers.json', 10, 'Share', 200),
        ('group_com_policy_off.json', 11, 'Share', 200),
        ('group_com_policy_on.json', 12, 'Share', 200),
        ('new_filter_groups.json', 13, 'Filter', 200),
        ('group_update_value.json', 15, 'Value', 200),
        ('empty_segment_groups.json', 16, 'Value', 200),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_retrieve_groups(
        web_app_client, load_json, file, id_, mode, result,
):
    expected_groups = load_json(file)
    response = await web_app_client.get(
        '/v2/campaigns/groups/item', params={'id': id_},
    )
    assert response.status == result
    if response.status == 200:
        retrieved_groups = await response.json()
        assert expected_groups == retrieved_groups


@pytest.mark.parametrize(
    'campaign_id, expected_response, request_json',
    [
        (6, 200, 'group_update.json'),
        (7, 400, 'group_update_prohibited.json'),
        (17, 424, 'group_update.json'),
    ],
)
@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_update_groups(
        web_app_client,
        load_json,
        campaign_id,
        expected_response,
        request_json,
        patch,
):
    @patch(
        'crm_admin.utils.validation.group_validators.group_update_validation',
    )
    async def _validate(*args, **kwargs):
        return []

    updated_groups = load_json(request_json)
    response = await web_app_client.put(
        '/v2/campaigns/groups/item',
        params={'id': campaign_id},
        json=updated_groups,
    )
    assert response.status == expected_response
    if expected_response == 200:
        expected_groups = load_json('group_update_share_updated.json')
        assert expected_groups == await response.json()


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_create_groups_from_bad_state(web_app_client, load_json):
    id_ = 8
    updated_groups = load_json('group_update_filter.json')
    response = await web_app_client.post(
        '/v2/campaigns/groups/item', params={'id': id_}, json=updated_groups,
    )
    assert response.status == 404
    body = await response.json()
    assert body['message'].startswith(
        'Campaign state \'NEW\' is not in expected',
    )


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.config(CRM_ADMIN_AUDIENCES_SETTINGS=CRM_ADMIN_AUDIENCES_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_update_groups_clear_send_at(
        web_context, web_app_client, load_json,
):
    db_group = storage.DbGroup(web_context)
    group = await db_group.fetch(1, use_v2=True)
    assert group.params.send_at  # present in db

    updated_groups = load_json('group_update_drop_send_at.json')
    response = await web_app_client.put(
        '/v2/campaigns/groups/item', params={'id': 6}, json=updated_groups,
    )
    assert response.status == 200

    retrieved_groups = await response.json()

    assert retrieved_groups['groups'][0]['id'] == 1
    assert 'send_at' not in retrieved_groups['groups'][0]

    group = await db_group.fetch(1, use_v2=True)
    assert group.params.send_at is None  # cleared in db


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.config(CRM_ADMIN_AUDIENCES_SETTINGS=CRM_ADMIN_AUDIENCES_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_update_groups_clear_creative(
        web_context, web_app_client, load_json,
):
    db_group = storage.DbGroup(web_context)

    updated_groups = load_json('group_update_drop_creative_id.json')
    response = await web_app_client.put(
        '/v2/campaigns/groups/item', params={'id': 6}, json=updated_groups,
    )
    assert response.status == 200

    retrieved_groups = await response.json()

    assert 'creative_id' not in retrieved_groups['groups'][0]

    group = await db_group.fetch(1, use_v2=True)
    assert group.params.creative_id is None


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_good_content(web_app_client, load_json, mock_promotions, patch):
    @patch(
        'crm_admin.utils.validation.group_validators.group_update_validation',
    )
    async def _validate(*args, **kwargs):
        return []

    @mock_promotions('/admin/promotions/')
    async def _promo(request):
        return web.json_response(
            {
                'id': 'good_content',
                'name': 'name',
                'promotion_type': 'promotion_type',
                'status': 'status',
            },
            status=200,
        )

    updated_groups = load_json('group_update.json')
    updated_groups[0]['content'] = 'good'
    updated_groups[0]['channel'] = 'promo.fs'
    response = await web_app_client.put(
        '/v2/campaigns/groups/item', params={'id': 6}, json=updated_groups,
    )
    assert response.status == 200
