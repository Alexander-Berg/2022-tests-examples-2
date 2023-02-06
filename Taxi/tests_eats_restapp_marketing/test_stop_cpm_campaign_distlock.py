import pytest

from tests_eats_restapp_marketing import sql


@pytest.mark.now('2022-02-01T00:00:00+0000')
async def test_stop_cpm_campaign_tasks_empty_bd(
        testpoint, taxi_eats_restapp_marketing, pgsql, mockserver,
):
    @mockserver.json_handler('/feeds-admin/v1/eats-promotions/unpublish')
    async def __handle_feeds_admin_unpublish(request):
        return mockserver.make_response(status=200, json={})

    @testpoint('stop-cpm-campaign-finished')
    async def handle_finished(arg):
        cursor = pgsql['eats_restapp_marketing'].cursor()
        cursor.execute(
            'SELECT id '
            'FROM eats_restapp_marketing.campaigns '
            'WHERE status = \'active\'',
        )
        assert list(cursor) == []

    async with taxi_eats_restapp_marketing.spawn_task('stop-cpm-campaign'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'


@pytest.mark.campaigns(
    sql.Campaign(
        id='1',
        status=sql.CampaignStatus.ACTIVE,
        parameters={
            'averagecpm': 2.0,
            'spend_limit': 100000000.0,
            'strategy_type': 'kCpMaximumImpressions',
            'start_date': '1970-01-01T00:00:00+00:00',
            'finish_date': '2022-01-01T00:00:00+00:00',
        },
        passport_id=1229582676,
        campaign_id='123',
        started_at='2021-01-01T00:00:00.000000+0000',
        suspended_at=None,
        created_at='2022-04-26T13:41:21.145013+0000',
    ),
    sql.Campaign(
        id='2',
        status=sql.CampaignStatus.ACTIVE,
        parameters={
            'averagecpm': 2.0,
            'spend_limit': 100000000.0,
            'strategy_type': 'kCpMaximumImpressions',
            'start_date': '1970-01-01T00:00:00+00:00',
            'finish_date': '2022-01-01T00:00:00+00:00',
        },
        passport_id=1229582676,
        campaign_id='456',
        started_at='2021-01-01T00:00:00.000000+0000',
        suspended_at=None,
        created_at='2022-04-26T13:41:21.145013+0000',
    ),
    sql.Campaign(
        id='3',
        status=sql.CampaignStatus.ACTIVE,
        parameters={
            'averagecpm': 2.0,
            'spend_limit': 100000000.0,
            'strategy_type': 'kCpMaximumImpressions',
            'start_date': '1970-01-01T00:00:00+00:00',
            'finish_date': '2022-02-01T00:00:00+00:00',
        },
        passport_id=1229582676,
        campaign_id='789',
        started_at='2021-01-01T00:00:00.000000+0000',
        suspended_at=None,
        created_at='2022-04-26T13:41:21.145013+0000',
    ),
    sql.Campaign(
        id='4',
        status=sql.CampaignStatus.ACTIVE,
        parameters={
            'averagecpm': 2.0,
            'spend_limit': 100000000.0,
            'strategy_type': 'kCpMaximumImpressions',
            'start_date': '1970-01-01T00:00:00+00:00',
            'finish_date': '2022-05-01T00:00:00+00:00',
        },
        passport_id=1229582676,
        campaign_id='789',
        started_at='2021-01-01T00:00:00.000000+0000',
        suspended_at=None,
        created_at='2022-04-26T13:41:21.145013+0000',
    ),
    sql.Campaign(
        id='6',
        status=sql.CampaignStatus.ACTIVE,
        parameters={
            'averagecpm': 2.0,
            'spend_limit': 100000000.0,
            'strategy_type': 'kCpMaximumImpressions',
            'start_date': '1970-01-01T00:00:00+00:00',
            'finish_date': '2021-01-01T00:00:00+00:00',
        },
        passport_id=1229582676,
        campaign_id='678',
        started_at='2021-01-01T00:00:00.000000+0000',
        suspended_at=None,
        created_at='2022-04-26T13:41:21.145013+0000',
    ),
)
@pytest.mark.banners(
    sql.Banner(
        id=1,
        inner_campaign_id='1',
        place_id=1,
        feeds_admin_id='abc1',
        status=sql.BannerStatus.ACTIVE,
        banner_id=1,
        group_id=1,
        ad_id=1,
        image='image1',
    ),
    sql.Banner(
        id=2,
        inner_campaign_id='1',
        place_id=6542,
        feeds_admin_id='abc2',
        status=sql.BannerStatus.ACTIVE,
        banner_id=2,
        group_id=2,
        ad_id=2,
        image='image2',
    ),
    sql.Banner(
        id=3,
        inner_campaign_id='2',
        place_id=6543,
        feeds_admin_id='abc3',
        status=sql.BannerStatus.ACTIVE,
        banner_id=3,
        group_id=3,
        ad_id=3,
        image='image3',
    ),
    sql.Banner(
        id=4,
        inner_campaign_id='3',
        place_id=6544,
        feeds_admin_id='abc4',
        status=sql.BannerStatus.ACTIVE,
        banner_id=4,
        group_id=4,
        ad_id=4,
        image='image4',
    ),
)
@pytest.mark.now('2022-02-01T00:00:00+0000')
@pytest.mark.parametrize(
    'feeds_admin_response_code, active_ids',
    [
        pytest.param(200, [('3',), ('4',)]),
        pytest.param(400, [('1',), ('2',), ('3',), ('4',)]),
        pytest.param(404, [('1',), ('2',), ('3',), ('4',)]),
        pytest.param(409, [('1',), ('2',), ('3',), ('4',)]),
        pytest.param(503, [('1',), ('2',), ('3',), ('4',)]),
    ],
)
async def test_stop_cpm_campaign_tasks(
        testpoint,
        taxi_eats_restapp_marketing,
        pgsql,
        mockserver,
        feeds_admin_response_code,
        active_ids,
):
    @mockserver.json_handler('/feeds-admin/v1/eats-promotions/unpublish')
    async def __handle_feeds_admin_unpublishr(request):
        if feeds_admin_response_code == 200:
            return mockserver.make_response(status=200, json={})
        if feeds_admin_response_code == 404:
            return mockserver.make_response(status=feeds_admin_response_code)
        return mockserver.make_response(
            status=feeds_admin_response_code,
            json={'code': str(feeds_admin_response_code), 'message': 'error'},
        )

    @testpoint('stop-cpm-campaign-finished')
    async def handle_finished(arg):
        cursor = pgsql['eats_restapp_marketing'].cursor()
        cursor.execute(
            'SELECT id '
            'FROM eats_restapp_marketing.campaigns '
            'WHERE status = \'active\'',
        )
        assert list(cursor) == active_ids

    async with taxi_eats_restapp_marketing.spawn_task('stop-cpm-campaign'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'
