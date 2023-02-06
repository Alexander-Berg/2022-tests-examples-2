import datetime

import pytest

# pylint: disable=W0621


async def test_create_campaign(web_app_client, campaign_exists):
    owner = 'owner'
    campaign = dict(
        ticket_name='ticket_name',
        description='description',
        status='inactive',
        valid_until='2019-11-20 01:00:00',
        entity_type='user',
        experiment='experiment id',
        experiment_groups=[
            dict(
                group_id='1_testing',
                control=False,
                channel='push',
                channel_info=dict(channel_name='user_push'),
                pause_time_communication=3600,
            ),
        ],
        global_control=False,
    )

    response = await web_app_client.post(
        '/v1/trigger-campaigns/item',
        json=campaign,
        headers={'X-Yandex-Login': owner},
    )
    assert response.status == 201
    response = await response.json()
    assert campaign_exists(response['campaign_id'])


@pytest.mark.pgsql('crm_admin', files=['trigger_campaigns.sql'])
@pytest.mark.parametrize(
    'campaign_id,status',
    [
        ('00000000-0000-0000-0000-000000000001', 200),
        ('00000000-0000-0000-0000-000000000002', 200),
        ('00000000-0000-0000-0000-111111111111', 404),
    ],
)
async def test_get_campaign(web_app_client, load_json, campaign_id, status):
    response = await web_app_client.get(
        '/v1/trigger-campaigns/item', params=dict(id=campaign_id),
    )
    campaigns = load_json('trigger_campaigns.json')

    assert response.status == status
    if status == 200:
        value = await response.json()
        assert value == campaigns[campaign_id]


@pytest.mark.parametrize(
    'entity_type,channel',
    [
        ('user', 'push'),
        ('user', 'sms'),
        ('driver', 'push'),
        ('driver', 'sms'),
        ('driver', 'wall'),
    ],
)
async def test_channel_types(web_app_client, entity_type, channel):
    owner = 'owner'
    channel_name = f'{entity_type}_{channel}'

    campaign = dict(
        status='inactive',
        valid_until='2019-11-20 01:00:00',
        entity_type=entity_type,
        experiment='experiment id',
        experiment_groups=[
            dict(
                group_id='1_testing',
                control=True,
                pause_time_communication=1000,
                channel=channel,
                channel_info=dict(channel_name=channel_name),
            ),
        ],
    )
    response = await web_app_client.post(
        '/v1/trigger-campaigns/item',
        json=campaign,
        headers={'X-Yandex-Login': owner},
    )
    assert response.status == 201

    campaign_id = (await response.json())['campaign_id']
    response = await web_app_client.get(
        '/v1/trigger-campaigns/item', params=dict(id=campaign_id),
    )
    assert response.status == 200

    created_campaign = await response.json()
    channel = created_campaign['experiment_groups'][0]['channel_info']
    assert channel['channel_name'] == channel_name


@pytest.mark.parametrize(
    'campaign_id,status',
    [
        ('00000000-0000-0000-0000-000000000001', 200),
        ('00000000-0000-0000-0000-111111111111', 404),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['trigger_campaigns.sql'])
async def test_update_campaign(
        web_app_client, get_campaign, campaign_id, status,
):
    campaign = dict(
        status='active',
        ticket_name='new ticket name',
        description='new description',
        valid_until='2019-11-20 01:00:00',
        entity_type='driver',
        experiment='new experiment',
        experiment_groups=[
            dict(
                group_id='1_testing',
                control=True,
                channel='sms',
                channel_info=dict(channel_name='driver_sms', sender='go'),
                pause_time_communication=86400,
            ),
        ],
    )

    owner = 'owner'
    response = await web_app_client.put(
        '/v1/trigger-campaigns/item',
        params={'id': campaign_id},
        json=campaign,
        headers={'X-Yandex-Login': owner},
    )

    campaign['valid_until'] = datetime.datetime(2019, 11, 20, 1, 0, 0)

    assert response.status == status
    if status == 200:
        stored_campaign = get_campaign(campaign_id)
        expected = {k: stored_campaign[k] for k in campaign}
        assert campaign == expected
        assert stored_campaign['updated_at'] is not None


@pytest.mark.parametrize(
    'projections, entity_type, count, update_timestamp, offset, limit, name',
    [
        ([], None, 10, None, 0, 100, None),
        (['CONTENT'], None, 3, '2020-05-22 00:00:00', 0, 100, None),
        (['EXPERIMENT'], None, 7, '2020-05-21 00:00:00', 0, 100, None),
        (['CONTENT', 'EXPERIMENT'], None, 12, None, 0, 100, None),
        (['PREVIEW'], None, 10, None, 0, 100, None),
        (['PREVIEW'], None, 5, None, 5, 100, None),
        (['PREVIEW'], None, 3, None, 0, 3, None),
        (['PREVIEW'], None, 1, None, 0, 100, 'campaign6name'),
        (['PREVIEW'], None, 4, None, 0, 100, 'backend'),
        (['EXPERIMENT'], 'user', 2, None, 0, 100, None),
        (['EXPERIMENT'], 'driver', 10, None, 0, 100, None),
    ],
)
@pytest.mark.pgsql(
    'crm_admin', files=['trigger_campaigns.sql', 'list_batch_campaigns.sql'],
)
async def test_list_campaign(
        web_app_client,
        projections,
        entity_type,
        count,
        update_timestamp,
        offset,
        limit,
        name,
):
    url = '/v1/trigger-campaigns/list'

    params = dict()
    if projections:
        params['projections'] = ','.join(projections)
    if entity_type:
        params['entity_type'] = entity_type
    if update_timestamp:
        params['update_timestamp'] = update_timestamp
    if offset:
        params['offset'] = offset
    if limit:
        params['limit'] = limit
    if name:
        params['name'] = name

    response = await web_app_client.get(url, params=params)
    assert response.status == 200
    campaigns = await response.json()

    if 'PREVIEW' in projections:
        # Preview should not return backend campaings.
        # The condition above is a hack.
        # Stricktly speaking, that condition does not necessarily mean
        # that the campaing is a 'backend' campaing, but here
        # we assume that it is.
        #
        assert not any('backend' in c['name'] for c in campaigns)
    else:
        assert len(campaigns) == count

    if not projections:
        return

    def is_trigger_campaing(campaign):
        return len(campaign['campaign_id']) == 36

    for campaign in campaigns:
        if 'CONTENT' in projections and is_trigger_campaing(campaign):
            assert 'name' in campaign
            assert 'content' in campaign
            assert 'groups' in campaign['content']
            for group in campaign['content']['groups']:
                assert 'channel_info' in group
                assert 'control' in group
            assert campaign['content']['groups']

        if 'EXPERIMENT' in projections:
            assert 'experiment' in campaign
            assert 'groups' in campaign['experiment']
            for group in campaign['experiment']['groups']:
                assert 'cooldown' in group
            assert campaign['experiment']['groups']

            if not is_trigger_campaing(campaign):
                assert campaign['experiment']['experiment_id'] == '__default__'

        if 'PREVIEW' in projections and is_trigger_campaing(campaign):
            assert 'name' in campaign
            assert 'owner' in campaign
            assert 'status' in campaign
            assert 'entity_type' in campaign
            assert 'created_at' in campaign
            assert 'updated_at' in campaign
