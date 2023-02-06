import pytest


@pytest.mark.parametrize(
    'timestamp, campaigns_ids',
    [
        ('2021-03-27 01:00:00', {1, 2, 3, 4}),
        ('2021-03-27 02:00:00', {1, 2, 3, 4}),
        ('2021-03-27 04:00:00', {2, 3, 4}),
        ('2021-03-27 05:00:00', set()),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_efficiency.sql'])
async def test_meta_campaigns_list_efficiency(
        web_app_client, web_context, timestamp, campaigns_ids,
):
    campaigns_w_full_params = [1, 2]

    response = await web_app_client.get(
        '/v1/campaigns/meta/list', params={'update_timestamp': timestamp},
    )
    assert response.status == 200
    meta_info = await response.json()
    campaigns = meta_info['campaigns']

    assert (
        set(campaign['campaign_id'] for campaign in campaigns) == campaigns_ids
    )

    for campaign in campaigns:
        async with web_context.pg.master_pool.acquire() as conn:
            len_groups = await conn.fetchval(
                f'SELECT count(*) as cnt FROM crm_admin.campaign c '
                f'JOIN crm_admin.group_v2 g '
                f'ON c.segment_id = g.segment_id '
                f'WHERE c.id = {campaign["campaign_id"]} ',
            )
        assert len_groups == len(campaign['groups'])

        if campaign['campaign_id'] not in campaigns_w_full_params:
            continue

        for group in campaign['groups']:
            assert group['allowed_time_scope'] == {
                'start_scope_time': '2021-03-27T10:00:00+03:00',
                'end_scope_time': '2021-03-30T23:00:00+03:00',
                'start_time_sec': 7 * 60 * 60,
                'stop_time_sec': 20 * 60 * 60,
            }


@pytest.mark.parametrize(
    'timestamp, campaigns_ids', [('2021-03-27 01:00:00', {1})],
)
@pytest.mark.pgsql('crm_admin', files=['init_oneshot.sql'])
async def test_meta_campaigns_list_oneshot(
        web_app_client, web_context, timestamp, campaigns_ids,
):
    campaigns_w_full_params = [1, 2]

    response = await web_app_client.get(
        '/v1/campaigns/meta/list', params={'update_timestamp': timestamp},
    )
    assert response.status == 200
    meta_info = await response.json()
    campaigns = meta_info['campaigns']

    assert (
        set(campaign['campaign_id'] for campaign in campaigns) == campaigns_ids
    )

    for campaign in campaigns:
        async with web_context.pg.master_pool.acquire() as conn:
            len_groups = await conn.fetchval(
                f'SELECT count(*) FROM crm_admin.campaign c '
                f'JOIN crm_admin.group_v2 g ON c.segment_id = g.segment_id '
                f'WHERE c.id = {campaign["campaign_id"]} ',
            )
        assert len_groups == len(campaign['groups'])

        if campaign['campaign_id'] not in campaigns_w_full_params:
            continue

        for group in campaign['groups']:
            assert group['allowed_time_scope'] == {
                'start_scope_time': '2021-03-27T10:00:00+03:00',
                'end_scope_time': '2021-03-30T23:00:00+03:00',
                'start_time_sec': 0,
                'stop_time_sec': (23 * 60 + 59) * 60,
                'using_timezone_for_daytime': False,
                'using_timezone_for_date': False,
            }


@pytest.mark.parametrize(
    'timestamp, campaigns_ids', [('2021-03-27 01:00:00', {1})],
)
@pytest.mark.pgsql('crm_admin', files=['init_regular.sql'])
async def test_meta_campaigns_list_regular(
        web_app_client, web_context, timestamp, campaigns_ids,
):
    campaigns_w_full_params = [1, 2]

    response = await web_app_client.get(
        '/v1/campaigns/meta/list', params={'update_timestamp': timestamp},
    )
    assert response.status == 200
    meta_info = await response.json()
    campaigns = meta_info['campaigns']

    assert (
        set(campaign['campaign_id'] for campaign in campaigns) == campaigns_ids
    )

    for campaign in campaigns:
        async with web_context.pg.master_pool.acquire() as conn:
            len_groups = await conn.fetchval(
                f'SELECT count(*) FROM crm_admin.campaign c '
                f'JOIN crm_admin.group_v2 g ON c.segment_id = g.segment_id '
                f'WHERE c.id = {campaign["campaign_id"]} ',
            )
        assert len_groups == len(campaign['groups'])

        if campaign['campaign_id'] not in campaigns_w_full_params:
            continue

        for group in campaign['groups']:
            assert group['allowed_time_scope'] == {
                'start_scope_time': '2021-03-27T10:00:00+03:00',
                'end_scope_time': '2021-03-30T23:00:00+03:00',
                'start_time_sec': 0,
                'stop_time_sec': (23 * 60 + 59) * 60,
                'using_timezone_for_daytime': True,
                'using_timezone_for_date': True,
            }
