import datetime

import pytest

# pylint: disable=W0621


async def test_create_backend_campaign(web_app_client, campaign_exists):
    backend_campaign = dict(entity_type='user', channel='push')

    response = await web_app_client.post(
        '/v1/campaign/backend/item', json=backend_campaign,
    )
    assert response.status == 200
    response = await response.json()

    assert campaign_exists(response['id'])


@pytest.mark.parametrize('source_campaign_id', ['source_id', None])
async def test_create_without_duplication(
        web_app_client, campaign_exists, source_campaign_id,
):
    backend_campaign = dict(
        entity_type='user',
        channel='push',
        source_campaign_id=source_campaign_id,
    )

    response = await web_app_client.post(
        '/v1/campaign/backend/item', json=backend_campaign,
    )
    assert response.status == 200
    first_campaign = await response.json()
    assert campaign_exists(first_campaign['id'])

    response = await web_app_client.post(
        '/v1/campaign/backend/item', json=backend_campaign,
    )
    assert response.status == 200
    second_campaign = await response.json()

    if source_campaign_id:
        assert first_campaign['id'] == second_campaign['id']
    else:
        assert first_campaign['id'] != second_campaign['id']


@pytest.mark.parametrize(
    'campaign_id,status',
    [
        ('00000000-0000-0000-0000-000000000007', 200),
        ('00000000-0000-0000-0000-111111111111', 404),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['trigger_campaigns.sql'])
async def test_update_backend_campaign(
        web_app_client, get_campaign, campaign_id, status,
):
    campaign = dict(
        id=campaign_id,
        status='inactive',
        source_campaign_id='source_campaign_id',
        name='campaign_new_name',
        entity_type='driver',
        valid_until='2019-11-30 01:00:00',
        channel='wall',
        pause_time_communication=1000,
    )

    response = await web_app_client.put(
        '/v1/campaign/backend/item', json=campaign,
    )

    campaign['valid_until'] = datetime.datetime(2019, 11, 30, 1, 0, 0)

    assert response.status == status
    if status == 200:
        stored_campaign = get_campaign(campaign_id)

        assert campaign['status'] == stored_campaign['status']
        assert (
            campaign['source_campaign_id']
            == stored_campaign['source_campaign_id']
        )
        assert campaign['name'] == stored_campaign['name']
        assert campaign['valid_until'] == stored_campaign['valid_until']

        default_group = None
        for group in stored_campaign['experiment_groups']:
            if group['group_id'] == '__default__':
                default_group = group
                break

        assert default_group
        assert default_group['channel'] == campaign['channel']
        assert (
            default_group['pause_time_communication']
            == campaign['pause_time_communication']
        )


@pytest.mark.pgsql('crm_admin', files=['trigger_campaigns.sql'])
@pytest.mark.parametrize(
    'campaign_id,status',
    [
        ('00000000-0000-0000-0000-000000000007', 200),
        ('00000000-0000-0000-0000-000000000008', 404),
        ('00000000-0000-0000-0000-000000000009', 404),
        ('00000000-0000-0000-0000-111111111111', 404),
    ],
)
async def test_get_backend_campaign(web_app_client, campaign_id, status):
    response = await web_app_client.get(
        '/v1/campaign/backend/item', params=dict(id=campaign_id),
    )

    campaign = dict(
        id=campaign_id.replace('-', ''),
        status='active',
        name='backend_campaign7name',
        entity_type='driver',
        valid_until='2020-06-20T03:00:00+03:00',
        channel='push',
        pause_time_communication=20,
    )

    assert response.status == status
    if status == 200:
        value = await response.json()
        assert value == campaign


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.parametrize(
    'campaign_id, feeds_id, group_id, group_name, campaign_name, result',
    [
        ('1', '1001', '3', 'Campaign1Group3', 'Campaign_1', 200),
        ('2', '2001', '6', 'Campaign2Group6', 'Campaign_2', 200),
        ('3', '3001', '9', 'Campaign3Group9', 'Campaign_3', 200),
        ('4', '4001', '12', 'Campaign4Group12', 'Campaign_4', 200),
        ('1', '4001', None, None, None, 404),
        ('4', '1001', None, None, None, 404),
        ('100', '101', None, None, None, 404),
    ],
)
async def test_get_group_by_feeds(
        web_app_client,
        campaign_id,
        feeds_id,
        group_id,
        group_name,
        campaign_name,
        result,
):
    response = await web_app_client.get(
        '/v1/groups/item',
        params=dict(campaign_id=campaign_id, feeds_id=feeds_id),
    )

    assert response.status == result
    if result == 200:
        value = await response.json()
        assert value['id'] == group_id
        assert value['name'] == group_name
        assert value['campaign_name'] == campaign_name
