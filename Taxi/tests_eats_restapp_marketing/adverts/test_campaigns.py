import pytest

from tests_eats_restapp_marketing import sql

CAMPAIGNS_PATH: str = '/4.0/restapp-front/marketing/v1/ad/campaigns'


def get_marketing_flags_config():
    return pytest.mark.config(
        EATS_RESTAPP_MARKETING_FLAGS={
            'advert_access': False,
            'passport_logout': False,
            'order_count_from_table': True,
            'on_stats_in_campaigns': True,
        },
    )


def using_report_storage(enabled: bool):
    return pytest.mark.config(
        EATS_RESTAPP_MARKETING_FLAGS={
            'advert_access': False,
            'passport_logout': False,
            'order_count_from_table': True,
            'on_stats_in_campaigns': True,
            'using_report_storage': enabled,
        },
    )


def get_advert_order_stats_config(
        order_statistics: str = '//home/testsuite/orders',
        order_cohorts_summary: str = '//home/testsuite/order_cohorts_summary',
):
    return pytest.mark.config(
        EATS_RESTAPP_MARKETING_ADVERT_ORDERS_STATS={
            'download_statistics': {
                'cluster': 'yt-local',
                'order_statisics': order_statistics,
                'task_period': 60,
                'batch_size': 1000,
                'order_cohorts_summary': order_cohorts_summary,
            },
        },
    )


CAMPAIGN_1 = {
    'advert_id': 1,
    'place_id': 1,
    'status': 'active',
    'has_access': True,
    'campaign_id': 1,
    'campaign_uuid': '5d534825-be18-4728-bd9b-55b17353431a',
    'created_at': '2021-01-01T00:00:00+0000',
    'is_rating_status_ok': True,
    'average_cpc': 10,
    'started_at': '2021-01-01T00:00:00+0000',
    'stats': {
        'calculated_at': '2021-08-05T12:00:00+00:00',
        'shows': {'delta': 103, 'sum': 635, 'points': []},
        'clicks': {'delta': 158, 'sum': 410, 'points': []},
        'ad_orders': {'delta': 3, 'sum': 63, 'points': []},
    },
    'campaign_type': 'cpc',
}

CAMPAIGN_2 = {
    'advert_id': 2,
    'place_id': 2,
    'status': 'active',
    'has_access': True,
    'campaign_id': 2,
    'is_rating_status_ok': True,
    'average_cpc': 10,
    'created_at': '2021-01-01T00:00:00+0000',
    'stats': {
        'calculated_at': '2021-08-05T12:00:00+00:00',
        'shows': {'delta': 100, 'sum': 200, 'points': []},
        'clicks': {'delta': 90, 'sum': 160, 'points': []},
        'ad_orders': {'delta': 4, 'sum': 29, 'points': []},
    },
    'campaign_type': 'cpc',
}

CAMPAIGN_3 = {
    'advert_id': 3,
    'place_id': 3,
    'status': 'active',
    'has_access': True,
    'campaign_id': 3,
    'is_rating_status_ok': True,
    'average_cpc': 10,
    'created_at': '2021-01-01T00:00:00+0000',
    'suspended_at': '2021-03-20T00:00:00+0000',
    'stats': {
        'calculated_at': '2021-08-05T12:00:00+00:00',
        'shows': {'delta': 100, 'sum': 200, 'points': []},
        'clicks': {'delta': 90, 'sum': 160, 'points': []},
        'ad_orders': {'delta': 4, 'sum': 29, 'points': []},
    },
    'campaign_type': 'cpc',
}

CAMPAIGN_4 = {
    'advert_id': 4,
    'place_id': 4,
    'status': 'active',
    'has_access': True,
    'campaign_id': 4,
    'is_rating_status_ok': True,
    'average_cpc': 10,
    'created_at': '2021-01-01T00:00:00+0000',
    'started_at': '2021-03-01T00:00:00+0000',
    'suspended_at': '2021-06-01T00:00:00+0000',
    'stats': {
        'calculated_at': '2021-08-05T12:00:00+00:00',
        'shows': {'delta': -3, 'sum': 323, 'points': []},
        'clicks': {'delta': -100, 'sum': 360, 'points': []},
        'ad_orders': {'delta': 0, 'sum': 40, 'points': []},
    },
    'campaign_type': 'cpc',
}

CAMPAIGN_5 = {
    'advert_id': 5,
    'place_id': 5,
    'status': 'active',
    'has_access': True,
    'campaign_id': 5,
    'is_rating_status_ok': True,
    'average_cpc': 10,
    'created_at': '2021-01-01T00:00:00+0000',
    'campaign_type': 'cpc',
}

CPM_STARTED_AT = '2021-01-01T00:00:00+0000'
AVATAR = 'https://avatars.mds.yandex.net/get-yapic/1229582676_avatar/40x40'
CPM_OWNER = {
    'yandex_uid': 1229582676,
    'status': 'ok',
    'display_name': '1229582676_display_name',
    'login': '1229582676_login',
    'avatar': AVATAR,
}


def construct_cpm_response(banner: sql.Banner, campaign: sql.Campaign):
    res = {
        'campaign_type': 'cpm',
        'advert_id': -1,
        'cpm_advert_id': campaign.id,
        'place_id': banner.place_id,
        'owner': CPM_OWNER,
        'status': str(sql.BannerStatus(banner.status)),
        'has_access': True,
        'campaign_uuid': campaign.id,
        'is_rating_status_ok': True,
        'started_at': CPM_STARTED_AT,
        'created_at': '2022-04-26T13:41:21.145013+0000',
        'moderation_status': 'accepted',
    }
    if banner.original_image_id:
        res['source_image'] = 'http//' + banner.original_image_id
    if banner.image:
        res['image'] = 'http//' + banner.image
    if banner.image_text:
        res['text'] = banner.image_text
    if campaign.campaign_id:
        res['campaign_id'] = int(campaign.campaign_id)
    if campaign.parameters:
        res['finish_date'] = campaign.parameters['finish_date'].split('T')[0]
        res['averagecpm'] = campaign.parameters['averagecpm']
        res['spend_limit'] = campaign.parameters['spend_limit']
    return res


CPM_CAMPAIGN_1 = {
    'campaign_type': 'cpm',
    'advert_id': -1,
    'cpm_advert_id': '1',
    'place_id': 1,
    'owner': CPM_OWNER,
    'status': 'active',
    'has_access': True,
    'campaign_id': 123,
    'is_rating_status_ok': True,
    'moderation_status': 'accepted',
    'started_at': CPM_STARTED_AT,
    'created_at': '2022-04-26T13:41:21.145013+0000',
    'finish_date': '2022-01-01',
    'averagecpm': 2.0,
    'spend_limit': 100000000.0,
    'campaign_uuid': '1',
    'image': 'http//image1',
}

CPM_CAMPAIGN_2 = {
    'campaign_type': 'cpm',
    'advert_id': -1,
    'cpm_advert_id': '1',
    'place_id': 6542,
    'owner': CPM_OWNER,
    'status': 'active',
    'has_access': True,
    'campaign_id': 123,
    'is_rating_status_ok': True,
    'moderation_status': 'accepted',
    'started_at': CPM_STARTED_AT,
    'created_at': '2022-04-26T13:41:21.145013+0000',
    'finish_date': '2022-01-01',
    'averagecpm': 2.0,
    'spend_limit': 100000000.0,
    'campaign_uuid': '1',
    'image': 'http//image2',
}

CPM_BANNER_6 = sql.Banner(
    id=6,
    inner_campaign_id='4',
    place_id=6111,
    feeds_admin_id='abc5',
    status=sql.BannerStatus.ACTIVE,
    banner_id=6,
    group_id=6,
    ad_id=6,
    image='image6',
    original_image_id='original_image6',
    image_text='image6_text',
)

CPM_CAMPAIGN_4 = sql.Campaign(
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
    campaign_id='12',
    started_at=CPM_STARTED_AT,
    suspended_at=None,
    created_at='2022-04-26T13:41:21.145013+0000',
)

CPM_CAMPAIGN_BANNER_CONSTRUCTOR = construct_cpm_response(
    CPM_BANNER_6, CPM_CAMPAIGN_4,
)


def use_cache_experiment(enabled: bool):
    return pytest.mark.experiments3(
        name='eats_restapp_marketing_statistics_use_cache',
        consumers=['eats_restapp_marketing/ad/statistics'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
        is_config=True,
    )


async def handle_eats_report_storage(mockserver):
    place_4 = {
        'place_id': 4,
        'metrics': [
            {
                'data_key': 'advert_clicks',
                'name': 'Advert clicks',
                'total_value': {'value': 360, 'title': 'clicks'},
                'points_data': [
                    {
                        'status': 'active',
                        'value': 200,
                        'dt_from': '2021-02-28T00:00:00+0000',
                        'dt_to': '2021-02-28T00:00:00+0000',
                        'title': '200',
                    },
                    {
                        'status': 'active',
                        'value': 100,
                        'dt_from': '2021-03-05T00:00:00+0000',
                        'dt_to': '2021-03-05T00:00:00+0000',
                        'title': '100',
                    },
                ],
            },
            {
                'data_key': 'advert_shows',
                'name': 'Advert shows',
                'total_value': {'value': 323, 'title': 'shows'},
                'points_data': [
                    {
                        'status': 'active',
                        'value': 103,
                        'dt_from': '2021-02-28T00:00:00+0000',
                        'dt_to': '2021-02-28T00:00:00+0000',
                        'title': '103',
                    },
                    {
                        'status': 'active',
                        'value': 100,
                        'dt_from': '2021-03-05T00:00:00+0000',
                        'dt_to': '2021-03-05T00:00:00+0000',
                        'title': '100',
                    },
                ],
            },
            {
                'data_key': 'advert_ad_orders',
                'name': 'Advert AdOrders',
                'total_value': {'value': 40, 'title': 'ad_orders'},
                'points_data': [
                    {
                        'status': 'active',
                        'value': 37,
                        'dt_from': '2021-02-28T00:00:00+0000',
                        'dt_to': '2021-02-28T00:00:00+0000',
                        'title': '37',
                    },
                    {
                        'status': 'active',
                        'value': 37,
                        'dt_from': '2021-03-05T00:00:00+0000',
                        'dt_to': '2021-03-05T00:00:00+0000',
                        'title': '37',
                    },
                ],
            },
        ],
    }

    @mockserver.json_handler(
        '/eats-report-storage/internal/place-metrics/metrics/get',
    )
    def __get_metrics(request):
        return mockserver.make_response(
            status=200, json={'payload': [place_4]},
        )


@get_marketing_flags_config()
@get_advert_order_stats_config()
@pytest.mark.now('2021-08-05T12:00:00+00:00')
@pytest.mark.yt(static_table_data=['yt_order_cohorts_summary_table.yaml'])
@pytest.mark.parametrize(
    'place_ids,response_json',
    [
        pytest.param(
            [1],
            {'campaigns': [CAMPAIGN_1, CPM_CAMPAIGN_1], 'meta': {}},
            marks=(use_cache_experiment(enabled=False)),
            id='cache disabled: with started_at created_at-mock_now',
        ),
        pytest.param(
            [2],
            {'campaigns': [CAMPAIGN_2], 'meta': {}},
            marks=(use_cache_experiment(enabled=False)),
            id='cache disabled: created_at-mock_now',
        ),
        pytest.param(
            [3],
            {'campaigns': [CAMPAIGN_3], 'meta': {}},
            marks=(use_cache_experiment(enabled=False)),
            id='cache disabled: created_at-suspended_at',
        ),
        pytest.param(
            [4],
            {'campaigns': [CAMPAIGN_4], 'meta': {}},
            marks=(use_cache_experiment(enabled=False)),
            id='cache disabled: with started_at created_at-suspended_at',
        ),
        pytest.param(
            [5],
            {'campaigns': [CAMPAIGN_5], 'meta': {}},
            marks=(use_cache_experiment(enabled=False)),
            id='cache disabled: stats none',
        ),
        pytest.param(
            [1, 2, 3, 4, 5],
            {
                'campaigns': [
                    CAMPAIGN_1,
                    CAMPAIGN_2,
                    CAMPAIGN_3,
                    CAMPAIGN_4,
                    CAMPAIGN_5,
                    CPM_CAMPAIGN_1,
                ],
                'meta': {},
            },
            marks=(use_cache_experiment(enabled=False)),
            id='cache disabled: multi places',
        ),
        pytest.param(
            [1, 2, 3, 4, 5, 6542],
            {
                'campaigns': [
                    CAMPAIGN_1,
                    CAMPAIGN_2,
                    CAMPAIGN_3,
                    CAMPAIGN_4,
                    CAMPAIGN_5,
                    CPM_CAMPAIGN_1,
                    CPM_CAMPAIGN_2,
                ],
                'meta': {},
            },
            marks=(use_cache_experiment(enabled=False)),
            id='cache disabled: multi places cpm',
        ),
        pytest.param(
            [1],
            {'campaigns': [CAMPAIGN_1, CPM_CAMPAIGN_1], 'meta': {}},
            marks=(use_cache_experiment(enabled=True)),
            id='cache enabled: started_at-mock_now',
        ),
        pytest.param(
            [2],
            {'campaigns': [CAMPAIGN_2], 'meta': {}},
            marks=(use_cache_experiment(enabled=True)),
            id='cache enabled: created_at-mock_now',
        ),
        pytest.param(
            [3],
            {'campaigns': [CAMPAIGN_3], 'meta': {}},
            marks=(use_cache_experiment(enabled=True)),
            id='cache enabled: created_at-suspended_at',
        ),
        pytest.param(
            [4],
            {'campaigns': [CAMPAIGN_4], 'meta': {}},
            marks=(use_cache_experiment(enabled=True)),
            id='cache enabled: started_at-suspended_at',
        ),
        pytest.param(
            [5],
            {'campaigns': [CAMPAIGN_5], 'meta': {}},
            marks=(use_cache_experiment(enabled=True)),
            id='cache enabled: stats none',
        ),
        pytest.param(
            [1, 2, 3, 4, 5],
            {
                'campaigns': [
                    CAMPAIGN_1,
                    CAMPAIGN_2,
                    CAMPAIGN_3,
                    CAMPAIGN_4,
                    CAMPAIGN_5,
                    CPM_CAMPAIGN_1,
                ],
                'meta': {},
            },
            marks=(use_cache_experiment(enabled=True)),
            id='cache enabled: multi places',
        ),
        pytest.param(
            [5],
            {'campaigns': [CAMPAIGN_5], 'meta': {}},
            marks=(
                use_cache_experiment(enabled=True),
                using_report_storage(True),
            ),
            id='using report storage: stats none',
        ),
        pytest.param(
            [4],
            {'campaigns': [CAMPAIGN_4], 'meta': {}},
            marks=(
                use_cache_experiment(enabled=True),
                using_report_storage(True),
            ),
            id='using report storage: one campaign',
        ),
        pytest.param(
            [4, 5],
            {'campaigns': [CAMPAIGN_4, CAMPAIGN_5], 'meta': {}},
            marks=(
                use_cache_experiment(enabled=False),
                using_report_storage(True),
            ),
            id='using report storage: campaign not stats and stats',
        ),
        pytest.param(
            [6111],
            {'campaigns': [CPM_CAMPAIGN_BANNER_CONSTRUCTOR], 'meta': {}},
            marks=(use_cache_experiment(enabled=False)),
            id='getting banner from banner constructor',
        ),
    ],
)
@pytest.mark.pgsql('eats_restapp_marketing', files=['insert_adverts.sql'])
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
            'finish_date': '2022-01-01T00:00:00+00:00',
        },
        passport_id=1229582676,
        campaign_id='789',
        started_at='2021-01-01T00:00:00.000000+0000',
        suspended_at=None,
        created_at='2022-04-26T13:41:21.145013+0000',
    ),
    CPM_CAMPAIGN_4,
    sql.Campaign(
        id='5',
        status=sql.CampaignStatus.ENDED,
        parameters={
            'averagecpm': 2.0,
            'spend_limit': 100000000.0,
            'strategy_type': 'kCpMaximumImpressions',
            'start_date': '1970-01-01T00:00:00+00:00',
            'finish_date': '2022-05-01T00:00:00+00:00',
        },
        passport_id=1229582676,
        campaign_id='345',
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
            'finish_date': '2022-05-01T00:00:00+00:00',
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
    sql.Banner(
        id=5,
        inner_campaign_id='4',
        place_id=6545,
        feeds_admin_id='abc5',
        status=sql.BannerStatus.ACTIVE,
        banner_id=5,
        group_id=5,
        ad_id=5,
        image='image5',
    ),
    sql.Banner(
        id=6,
        inner_campaign_id='4',
        place_id=6111,
        feeds_admin_id='abc5',
        status=sql.BannerStatus.ACTIVE,
        banner_id=6,
        group_id=6,
        ad_id=6,
        image='image6',
        original_image_id='original_image6',
        image_text='image6_text',
    ),
)
async def test_get_campaigns_stats_from_cache(
        taxi_eats_restapp_marketing,
        authorizer_user_access,
        mockserver,
        direct_report_stats,
        yt_apply,
        mock_blackbox_tokeninfo,
        mock_any_handler,
        place_ids,
        response_json,
        mock_feeds_admin,
):
    await handle_eats_report_storage(mockserver)

    await mock_any_handler(
        url='/eats-restapp-authorizer/place-access/list',
        response={'status': 200, 'json': {'place_ids': place_ids}},
    )

    response = await taxi_eats_restapp_marketing.get(
        CAMPAIGNS_PATH,
        headers={
            'X-YaEda-PartnerId': '1',
            'Content-type': 'application/json',
            'Authorization': 'token',
            'X-Remote-IP': '127.0.0.1',
        },
    )

    print(response.json())
    assert response.status_code == 200
    assert response.json() == response_json
