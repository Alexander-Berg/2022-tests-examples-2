import pytest


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
