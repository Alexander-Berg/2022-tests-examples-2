import pytest

from crm_admin.storage import campaign_adapters
from crm_admin.storage import group_adapters
from crm_admin.storage import segment_adapters


async def check_campaign_info(context, campaign_id, campaign_info):
    campaign = await campaign_adapters.DbCampaign(context).fetch(campaign_id)
    campaign_dict = campaign.__dict__
    for key, val in campaign_info.items():
        if key not in (
                'segment_id',
                'is_active',
                'created_at',
                'updated_at',
                'campaign_id',
                'owner_name',
                'ticket',
                'ticket_status',
                'deleted_at',
                'name',
                'settings',
                'version_info',
        ):
            assert str(campaign_dict.get(key, None)) == str(val)
        elif key == 'settings':
            settings = [s.serialize() for s in campaign_dict['settings']]
            assert settings == campaign_info['settings']

    return campaign


async def check_segment_info(context, segment_id, segment_info):
    segment = await segment_adapters.DbSegment(context).fetch(segment_id)
    if segment.aggregate_info:
        segment.aggregate_info = segment.aggregate_info.serialize()
    segment_dict = segment.__dict__
    for key, val in segment_info.items():
        if key not in ('id', 'yt_table'):
            # pylint: disable=consider-using-in
            assert segment_dict[key] == val or segment_dict[key].value == val
    return segment


async def check_groups_info(context, segment_id, groups_info):
    groups = await group_adapters.DbGroup(context).fetch_by_segment(segment_id)
    groups.sort(key=lambda x: x.params.name)
    for expected, real in zip(groups_info, groups):
        for key, val in expected.items():
            assert (
                real.__dict__[key] == val
                or real.__dict__[key].serialize() == val
            )
    return groups


async def check_yt_tables(
        yt_client, yt_table, yt_segment_info, yt_verification_info,
):
    if yt_segment_info:
        yt_segment = list(yt_client.read_table('//' + yt_table))
        assert yt_segment == yt_segment_info

    if yt_verification_info:
        yt_verification_table = list(
            yt_client.read_table('//' + yt_table + '_verification_clean'),
        )
        assert yt_verification_table == yt_verification_info


async def check_internal_campaign(
        context, campaign_id, internal_campaign, yt_client,
):
    campaign = await check_campaign_info(
        context, campaign_id, internal_campaign['campaign'],
    )

    if 'segment' in internal_campaign and internal_campaign['segment']:
        segment = await check_segment_info(
            context, campaign.segment_id, internal_campaign['segment'],
        )
        await check_groups_info(
            context, campaign.segment_id, internal_campaign['groups'],
        )
        await check_yt_tables(
            yt_client,
            segment.yt_table,
            internal_campaign['yt_segment'],
            internal_campaign['yt_verification_table'],
        )


@pytest.mark.parametrize('campaign_id', [1, 2, 3])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.yt(
    static_table_data=[
        'yt_cmp_1_seg.yaml',
        'yt_cmp_1_seg_stat.yaml',
        'yt_cmp_1_seg_summary.yaml',
        'yt_cmp_1_seg_verification.yaml',
        'yt_cmp_2_seg.yaml',
        'yt_cmp_2_seg_verification.yaml',
    ],
)
async def test_internal_clear_campaign(
        yt_apply, yt_client, web_app_client, campaign_id, web_context,
):
    async with web_context.pg.master_pool.acquire() as conn:
        query_all = (
            f'SELECT '
            f'    c.segment_id as segment_id, '
            f'    ARRAY_AGG(g.id) as group_ids, '
            f'    s.yt_table as yt_table '
            f'FROM crm_admin.campaign c '
            f'LEFT JOIN crm_admin.segment s ON c.segment_id = s.id '
            f'LEFT JOIN crm_admin.group g ON s.id = g.segment_id '
            f'WHERE c.id = {campaign_id} '
            f'GROUP BY c.id, s.yt_table;'
        )

        data_to_remove = await conn.fetchrow(query_all)
        segment_id = data_to_remove['segment_id']
        groups_ids = data_to_remove['group_ids']
        yt_table = data_to_remove['yt_table']

        if segment_id is None:
            segment_id = 'NULL'
        if set(groups_ids) == {None}:
            groups_ids = ['NULL']
        if yt_table:
            yt_table = '//' + yt_table
            assert yt_client.exists(yt_table)

        response = await web_app_client.delete(
            '/v1/internal/campaign/clear', params={'id': campaign_id},
        )
        assert response.status == 200

        query_campaign = (
            f'SELECT * FROM crm_admin.campaign WHERE id = {campaign_id};'
        )
        query_segment = (
            f'SELECT * FROM crm_admin.segment WHERE id = {segment_id};'
        )
        query_groups = (
            f'SELECT * FROM crm_admin.group '
            f'WHERE id IN ({", ".join(map(str, groups_ids))});'
        )
        for query in [query_campaign, query_segment, query_groups]:
            assert not await conn.fetch(query)

        if yt_table:
            for suffix in ['', '_stat', '_summary', '_verification']:
                assert not yt_client.exists(yt_table + suffix)


async def test_internal_clear_campaign_not_found(web_app_client):
    response = await web_app_client.delete(
        '/v1/internal/campaign/clear', params={'id': 1},
    )
    assert response.status == 404


@pytest.mark.parametrize(
    'internal_campaign',
    [
        {
            'campaign': {
                'name': 'test campaign',
                'entity_type': 'Driver',
                'trend': 'test trend',
                'discount': False,
                'campaign_id': 0,
                'state': 'GROUPS_READY',
                'owner_name': 'rnglol',
                'test_users': [],
                'global_control': False,
                'com_politic': False,
                'efficiency': False,
                'tasks': [],
                'created_at': '2021-07-14T17:07:21.583960+03:00',
                'qs_major_version': 0,
                'settings': [
                    {'fieldId': 'country', 'value': ['br_russia']},
                    {'fieldId': 'city', 'value': []},
                    {'fieldId': 'city_exclude', 'value': []},
                    {'fieldId': 'brand', 'value': 'yandex'},
                    {'fieldId': 'active_taxi', 'value': 'off'},
                ],
            },
            'segment': {
                'yql_shared_url': 'yql_link',
                'extra_columns': [],
                'control': 0,
                'mode': 'Share',
                'yt_table': 'yt_table',
            },
            'groups': [
                {
                    'yql_shared_url': 'yql_link',
                    'params': {'name': 'group #1', 'share': 0},
                },
                {
                    'yql_shared_url': 'yql_link',
                    'params': {'name': 'group #2', 'share': 0},
                },
            ],
            'yt_segment': [{'data': 'Athens'}, {'data': 'Sparta'}],
            'yt_verification_table': [{'data': 'Athens'}, {'data': 'Sparta'}],
        },
        {
            'campaign': {
                'name': 'test campaign',
                'entity_type': 'Driver',
                'trend': 'test trend',
                'discount': False,
                'campaign_id': 0,
                'state': 'NEW',
                'owner_name': 'rnglol',
                'test_users': [],
                'global_control': False,
                'com_politic': False,
                'efficiency': False,
                'tasks': [],
                'created_at': '2021-07-14T17:07:21.583960+03:00',
                'qs_major_version': 0,
            },
            'segment': {
                'yql_shared_url': 'yql_link',
                'extra_columns': [],
                'control': 0,
                'mode': 'Share',
                'yt_table': 'yt_table',
            },
            'groups': [],
            'yt_segment': [{'data': 'Athens'}, {'data': 'Sparta'}],
            'yt_verification_table': [{'data': 'Athens'}, {'data': 'Sparta'}],
        },
        {
            'campaign': {
                'name': 'test campaign',
                'entity_type': 'Driver',
                'trend': 'test trend',
                'discount': False,
                'campaign_id': 0,
                'state': 'CANCELED',
                'owner_name': 'rnglol',
                'test_users': [],
                'global_control': False,
                'com_politic': False,
                'efficiency': False,
                'tasks': [],
                'created_at': '2021-07-14T17:07:21.583960+03:00',
                'qs_major_version': 0,
            },
            'segment': {
                'yql_shared_url': 'yql_link',
                'extra_columns': [],
                'control': 0,
                'mode': 'Share',
                'yt_table': 'yt_table',
            },
            'groups': [
                {
                    'yql_shared_url': 'yql_link',
                    'params': {'name': 'group #1', 'share': 0},
                },
                {
                    'yql_shared_url': 'yql_link',
                    'params': {'name': 'group #2', 'share': 0},
                },
            ],
            'yt_segment': [],
            'yt_verification_table': [],
        },
        {
            'campaign': {
                'name': 'test campaign',
                'entity_type': 'Driver',
                'trend': 'test trend',
                'discount': False,
                'campaign_id': 0,
                'state': 'NEW',
                'owner_name': 'rnglol',
                'test_users': [],
                'global_control': False,
                'com_politic': False,
                'efficiency': False,
                'tasks': [],
                'created_at': '2021-07-14T17:07:21.583960+03:00',
                'qs_major_version': 0,
            },
            'segment': None,
            'groups': [],
            'yt_segment': [],
            'yt_verification_table': [],
        },
    ],
)
@pytest.mark.yt(static_table_data=['yt_cmp_1_seg_summary.yaml'])
async def test_internal_import_campaign(
        yt_apply,
        yt_client,
        web_app_client,
        web_context,
        internal_campaign,
        patch,
):
    @patch('crm_admin.utils.startrek.startrek.TicketManager.create_ticket')
    async def _(*args, **kwargs):
        return 'ticket_key'

    @patch('crm_admin.utils.startrek.startrek.TicketManager.add_comment')
    async def _(*args, **kwargs):
        return {}

    yt_client.remove('//home/taxi-crm/robot-crm-admin/cmp_1_seg')
    yt_client.remove(
        '//home/taxi-crm/robot-crm-admin/cmp_1_seg_verification_clean',
    )

    response = await web_app_client.post(
        '/v1/internal/campaign/import', json=internal_campaign,
    )
    campaign_id = await response.json()

    await check_internal_campaign(
        web_context, campaign_id, internal_campaign, yt_client,
    )


@pytest.mark.parametrize(
    'campaign_id,status', [(1337, 404), (1, 200), (2, 200), (3, 200)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.yt(
    static_table_data=[
        'yt_cmp_1_seg.yaml',
        'yt_cmp_1_seg_verification.yaml',
        'yt_cmp_2_seg.yaml',
        'yt_cmp_2_seg_verification.yaml',
    ],
)
async def test_internal_export_campaign(
        yt_apply, yt_client, web_context, web_app_client, campaign_id, status,
):
    response = await web_app_client.get(
        '/v1/internal/campaign/export', params={'id': campaign_id},
    )
    assert response.status == status
    if status == 200:
        internal_campaign = await response.json()
        await check_internal_campaign(
            web_context, campaign_id, internal_campaign, yt_client,
        )


@pytest.mark.parametrize('campaign_id', [1, 2, 3])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.yt(
    static_table_data=[
        'yt_cmp_1_seg.yaml',
        'yt_cmp_1_seg_verification.yaml',
        'yt_cmp_2_seg.yaml',
        'yt_cmp_2_seg_verification.yaml',
    ],
)
async def test_internal_import_export_bundle(
        yt_apply, yt_client, web_context, web_app_client, campaign_id, patch,
):
    @patch('crm_admin.utils.startrek.startrek.TicketManager.create_ticket')
    async def _(*args, **kwargs):
        return 'ticket_key'

    @patch('crm_admin.utils.startrek.startrek.TicketManager.add_comment')
    async def _(*args, **kwargs):
        return {}

    export_response = await web_app_client.get(
        '/v1/internal/campaign/export', params={'id': campaign_id},
    )
    internal_campaign = await export_response.json()

    import_response = await web_app_client.post(
        '/v1/internal/campaign/import', json=internal_campaign,
    )
    assert import_response.status == 200

    campaign_id = await import_response.json()
    await check_internal_campaign(
        web_context, campaign_id, internal_campaign, yt_client,
    )
