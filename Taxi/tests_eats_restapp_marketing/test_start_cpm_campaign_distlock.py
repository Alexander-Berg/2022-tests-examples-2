import pytest

from tests_eats_restapp_marketing import sql


CAMPAIGN_PARAMS = {
    'averagecpm': 2.0,
    'spend_limit': 100000000.0,
    'strategy_type': 'kCpMaximumImpressions',
    'start_date': '2022-01-01T00:00:00+00:00',
    'finish_date': '2022-10-01T00:00:00+00:00',
}

CAMPAIGN_PARAMS_NEXT_DATE = {
    'averagecpm': 2.0,
    'spend_limit': 100000000.0,
    'strategy_type': 'kCpMaximumImpressions',
    'start_date': '2022-02-01T00:00:00+00:00',
    'finish_date': '2022-10-01T00:00:00+00:00',
}


def cpm_start_campaign_settings(exp: str):
    return pytest.mark.experiments3(
        is_config=True,
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eats_restapp_marketing_cpm_start_campaign_settings',
        consumers=['eats-restapp-marketing/start_settings'],
        clauses=[
            {
                'title': 'Always match',
                'value': {'experiment': exp},
                'predicate': {'type': 'true'},
            },
        ],
        enable_debug=True,
    )


@pytest.mark.now('2022-01-01T00:00:00+0000')
async def test_start_cpm_campaign_tasks_empty_bd(
        testpoint, taxi_eats_restapp_marketing, pgsql, mockserver,
):
    @mockserver.json_handler('/feeds-admin/v1/eats-promotions/publish')
    async def __handle_feeds_admin_unpublish(request):
        return mockserver.make_response(status=200, json={})

    @testpoint('start-cpm-campaign-finished')
    async def handle_finished(arg):
        cursor = pgsql['eats_restapp_marketing'].cursor()
        cursor.execute(
            'SELECT id '
            'FROM eats_restapp_marketing.campaigns '
            'WHERE status = \'active\'',
        )
        assert list(cursor) == []

    async with taxi_eats_restapp_marketing.spawn_task('start-cpm-campaign'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'


@pytest.mark.now('2022-01-01T00:00:00+0000')
@pytest.mark.parametrize(
    'feeds_admin_response_code, active_ids',
    [
        pytest.param(
            200,
            [('1',), ('2',), ('3',), ('4',)],
            marks=(cpm_start_campaign_settings('test1')),
        ),
        pytest.param(
            400,
            [('1',), ('2',), ('3',), ('4',)],
            marks=(cpm_start_campaign_settings('test1')),
        ),
        pytest.param(
            404,
            [('1',), ('2',), ('3',), ('4',)],
            marks=(cpm_start_campaign_settings('test1')),
        ),
        pytest.param(
            409,
            [('1',), ('2',), ('3',), ('4',)],
            marks=(cpm_start_campaign_settings('test1')),
        ),
        pytest.param(
            503,
            [('1',), ('2',), ('3',), ('4',)],
            marks=(cpm_start_campaign_settings('test1')),
        ),
    ],
)
@pytest.mark.campaigns(
    sql.Campaign(
        id='1', status=sql.CampaignStatus.READY, parameters=CAMPAIGN_PARAMS,
    ),
    sql.Campaign(
        id='2', status=sql.CampaignStatus.READY, parameters=CAMPAIGN_PARAMS,
    ),
    sql.Campaign(
        id='3', status=sql.CampaignStatus.READY, parameters=CAMPAIGN_PARAMS,
    ),
    sql.Campaign(
        id='4', status=sql.CampaignStatus.READY, parameters=CAMPAIGN_PARAMS,
    ),
    sql.Campaign(
        id='5', status=sql.CampaignStatus.ENDED, parameters=CAMPAIGN_PARAMS,
    ),
    sql.Campaign(
        id='6',
        status=sql.CampaignStatus.READY,
        parameters=CAMPAIGN_PARAMS_NEXT_DATE,
    ),
)
@pytest.mark.banners(
    sql.Banner(
        id=1,
        inner_campaign_id='1',
        place_id=6541,
        feeds_admin_id='abc1',
        status=sql.BannerStatus.APPROVED,
    ),
    sql.Banner(
        id=2,
        inner_campaign_id='1',
        place_id=6542,
        feeds_admin_id='abc2',
        status=sql.BannerStatus.APPROVED,
    ),
    sql.Banner(
        id=3,
        inner_campaign_id='2',
        place_id=6543,
        feeds_admin_id='abc3',
        status=sql.BannerStatus.APPROVED,
    ),
    sql.Banner(
        id=5,
        inner_campaign_id='4',
        place_id=6544,
        feeds_admin_id='abc5',
        status=sql.BannerStatus.STOPPED,
    ),
)
async def test_start_cpm_campaign_tasks(
        testpoint,
        taxi_eats_restapp_marketing,
        pgsql,
        mockserver,
        feeds_admin_response_code,
        active_ids,
):
    @mockserver.json_handler('/feeds-admin/v1/eats-promotions/publish')
    async def __handle_feeds_admin_unpublishr(request):
        if feeds_admin_response_code == 200:
            return mockserver.make_response(status=200, json={})
        if feeds_admin_response_code == 404:
            return mockserver.make_response(status=feeds_admin_response_code)
        return mockserver.make_response(
            status=feeds_admin_response_code,
            json={'code': str(feeds_admin_response_code), 'message': 'error'},
        )

    @testpoint('start-cpm-campaign-finished')
    async def handle_finished(arg):
        cursor = pgsql['eats_restapp_marketing'].cursor()
        cursor.execute(
            'SELECT id '
            'FROM eats_restapp_marketing.campaigns '
            'WHERE status = \'active\'',
        )
        assert list(cursor) == active_ids

    async with taxi_eats_restapp_marketing.spawn_task('start-cpm-campaign'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'
