import dateutil.parser
import pytest

from crm_admin import settings
from test_crm_admin.utils import audience_cfg


# =============================================================================


@pytest.mark.pgsql('crm_admin', files=['map_state.sql'])
@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_retrieve_list_check_map_state(web_app_client, load_json):
    body = {}
    response = await web_app_client.post('/v1/campaigns/list', json=body)
    assert response.status == 200
    retrieved_previews = await response.json()

    expected_states = {
        1: 'NEW',
        2: 'READY',
        3: 'SEGMENT_CALCULATING',
        4: 'GROUPS_CALCULATING',
        5: 'VERIFY_PROCESSING',
        6: 'SEGMENT_CALCULATING',
    }

    for row in retrieved_previews:
        assert row['state'] == expected_states[row['id']]


# =============================================================================


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_retrieve_list_campaigns(web_app_client, load_json):
    limit = 4
    offset = 1
    existing_previews = load_json('new_previews.json')
    existing_previews = sorted(
        existing_previews,
        key=lambda item: dateutil.parser.parse(item['updated_at']),
        reverse=True,
    )

    response = await web_app_client.post(
        '/v1/campaigns/list', json={'limit': limit, 'offset': offset},
    )
    assert response.status == 200
    retrieved_previews = await response.json()
    for i in range(limit):
        assert retrieved_previews[i] == existing_previews[i + offset]


# =============================================================================


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_retrieve_list_campaigns_wo_limit(web_app_client, load_json):
    existing_previews = load_json('new_previews.json')
    existing_previews = sorted(
        existing_previews,
        key=lambda item: dateutil.parser.parse(item['updated_at']),
        reverse=True,
    )

    response = await web_app_client.post('/v1/campaigns/list', json={})
    assert response.status == 200
    retrieved_previews = await response.json()
    assert len(retrieved_previews) == len(existing_previews)
    for retried, existing in zip(retrieved_previews, existing_previews):
        assert retried == existing


# =============================================================================


@pytest.mark.parametrize(
    'body, existing_indexes',
    [
        (
            {'name': 'ТаЯ', 'order_by': 'updated_at', 'order': 'desc'},
            [5, 8, 4, 3],
        ),
        ({'trend': 'Направление или тип третьей кампании'}, [2]),
        ({'kind': 'Тип или подтип пятой кампании'}, [4]),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_retrieve_list_campaigns_filtered(
        web_app_client, load_json, body, existing_indexes,
):
    existing_previews = load_json('new_previews.json')
    response = await web_app_client.post('/v1/campaigns/list', json=body)
    assert response.status == 200
    retrieved_previews = await response.json()
    existing_previews_list = []
    for index in existing_indexes:
        existing_previews_list.append(existing_previews[index])

    assert retrieved_previews == existing_previews_list


# =============================================================================


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_retrieve_list_campaigns_filtered_date(
        web_app_client, load_json,
):
    # select campaigns from the range
    # [2020-03-20T00:00:00+03, 2020-04-20T00:00:00+03)
    # or in UTC
    # [2020-03-19T21:00:00, 2020-03-20T21:00:00)
    #
    body = {'created_at': '2020-03-20T00:00:00+03'}

    existing_previews = load_json('new_previews.json')
    response = await web_app_client.post('/v1/campaigns/list', json=body)
    assert response.status == 200
    retrieved_previews = await response.json()
    assert retrieved_previews == [
        existing_previews[0],
        existing_previews[5],
        existing_previews[6],
        existing_previews[7],
        existing_previews[8],
    ]


# =============================================================================


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_retrieve_list_campaigns_ordered(web_app_client, load_json):
    body = {
        'order_by': 'updated_at',
        'order': 'asc',
        'ticket_status': 'Открыт',
    }

    existing_previews = load_json('new_previews.json')
    response = await web_app_client.post('/v1/campaigns/list', json=body)
    assert response.status == 200
    retrieved_previews = await response.json()
    assert retrieved_previews == [
        existing_previews[1],
        existing_previews[2],
        existing_previews[3],
        existing_previews[4],
        existing_previews[0],
        existing_previews[5],
        existing_previews[6],
        existing_previews[7],
        existing_previews[8],
        existing_previews[10],
        existing_previews[9],
    ]


# =============================================================================


@pytest.mark.pgsql(
    'crm_admin', files=['init_campaigns.sql', 'regular_campaigns.sql'],
)
@pytest.mark.parametrize('campaign_type', ['regular', 'oneshot'])
@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_retrieve_list_campaigns_by_campaign_type(
        web_app_client, campaign_type,
):
    body = {'campaign_type': campaign_type}

    response = await web_app_client.post('/v1/campaigns/list', json=body)
    assert response.status == 200
    response = await response.json()

    assert all(c['campaign_type'] == campaign_type for c in response)


# =============================================================================


@pytest.mark.pgsql(
    'crm_admin', files=['init_campaigns.sql', 'failed_campaings.sql'],
)
@pytest.mark.parametrize(
    'state, states_group',
    [
        (settings.NEW_CAMPAIGN, {settings.NEW_CAMPAIGN}),
        (settings.SEGMENT_EXPECTED_STATE, {settings.SEGMENT_EXPECTED_STATE}),
        (settings.SEGMENT_ERROR, settings.ERROR_STATES_GROUP),
        (settings.GROUPS_ERROR, settings.ERROR_STATES_GROUP),
    ],
)
@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_retrieve_list_campaigns_by_state(
        web_app_client, load_json, state, states_group,
):
    body = {'state': state}
    existing_previews = load_json('new_previews.json')
    existing_previews += load_json('failed_campaings_preview.json')

    response = await web_app_client.post('/v1/campaigns/list', json=body)
    assert response.status == 200
    retrieved_previews = await response.json()

    def is_selected(campaign):
        return campaign['state'] in states_group

    expected = sum(is_selected(c) for c in existing_previews)
    assert len(retrieved_previews) == expected


# =============================================================================


@pytest.mark.parametrize('salt, count', [('salt', 2), ('other salt', 1)])
@pytest.mark.pgsql('crm_admin', files=['campaign_list_salt.sql'])
@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_retrieve_list_campaigns_by_salt(web_app_client, salt, count):
    response = await web_app_client.post(
        '/v1/campaigns/list', json={'salt': salt},
    )
    assert response.status == 200
    result = await response.json()
    assert len(result) == count


# =============================================================================


@pytest.mark.parametrize(
    'version_state, root_id, is_main_campaign, campaign_ids',
    [
        ('ACTUAL', None, None, {2}),
        ('DRAFT', None, None, {3, 5}),
        (None, 1, None, {1, 2, 5}),
        (None, 3, None, {3}),
        (None, None, True, {2, 3, 4}),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['regular_campaigns_drafts.sql'])
@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_retrieve_list_campaigns_for_drafts(
        web_app_client,
        load_json,
        version_state,
        root_id,
        is_main_campaign,
        campaign_ids,
):
    response = await web_app_client.post(
        '/v1/campaigns/list',
        json={
            'version_state': version_state,
            'root_id': root_id,
            'is_main_campaign': is_main_campaign,
        },
    )
    assert response.status == 200
    result = await response.json()

    expected_campaigns = load_json('regular_campaigns_drafts_expected.json')

    expected_result = [
        expected_campaigns[str(campaign_id)]
        for campaign_id in sorted(campaign_ids)
    ]

    assert len(result) == len(expected_result)

    for campaign, expected_campaign in zip(
            sorted(result, key=lambda x: x['id']), expected_result,
    ):
        for key in expected_campaign:
            assert key in campaign
            assert expected_campaign[key] == campaign[key]


# =============================================================================


@pytest.mark.parametrize(
    'target_id, expected_ids', [(1, [0, 1]), (2, [0, 2]), (3, []), (4, [1])],
)
@pytest.mark.pgsql('crm_admin', files=['targets.sql'])
@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_target_id_filter(
        web_app_client, load_json, target_id, expected_ids,
):
    body = {'target_id': target_id, 'is_main_campaign': True}

    response = await web_app_client.post('/v1/campaigns/list', json=body)
    assert response.status == 200
    answer = await response.json()

    existing_campaigns = load_json('expected_targets.json')

    assert len(answer) == len(expected_ids)
    for index, _id in enumerate(expected_ids):
        assert answer[index] == existing_campaigns[_id]


# =============================================================================
