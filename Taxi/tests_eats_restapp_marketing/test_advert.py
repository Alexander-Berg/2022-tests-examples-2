import random

import pytest

from tests_eats_restapp_marketing import sql


CPC_ADVERT_1 = sql.Advert(
    id=1,
    place_id=53468,
    average_cpc=100,
    campaign_id=399264,
    group_id=4,
    ad_id=5,
    banner_id=1,
    weekly_spend_limit=1000000,
    passport_id=1229582676,
)

CPC_ADVERT_2 = sql.Advert(
    id=2,
    place_id=3965,
    average_cpc=100,
    campaign_id=399265,
    group_id=4,
    weekly_spend_limit=2000000,
    passport_id=1229582678,
)

CPC_ADVERT_3 = sql.Advert(
    id=3,
    place_id=2464,
    average_cpc=100,
    campaign_id=399266,
    group_id=4,
    ad_id=5,
    banner_id=1,
    is_active=True,
    weekly_spend_limit=3000000,
    passport_id=1229582676,
)

CPC_ADVERT_4 = sql.Advert(
    id=4,
    place_id=2465,
    average_cpc=100,
    campaign_id=399267,
    group_id=4,
    ad_id=5,
    weekly_spend_limit=4000000,
)


async def request_proxy_advert_campaigns(
        taxi_eats_restapp_marketing, partner_id,
):
    url = '/4.0/restapp-front/marketing/v1/ad/campaigns'
    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
        'Authorization': 'token',
        'X-Remote-IP': '127.0.0.1',
    }
    extra = {'headers': headers}

    return await taxi_eats_restapp_marketing.get(url, **extra)


@pytest.mark.pgsql('eats_restapp_marketing', files=['advert_campaigns.sql'])
async def test_get_advert_camapigns(
        taxi_eats_restapp_marketing,
        mock_any_handler,
        mock_authorizer_allowed,
        mock_blackbox_all,
):
    await mock_any_handler(
        url='/eats-restapp-authorizer/place-access/list',
        response={
            'status': 200,
            'json': {'place_ids': [53468, 3965, 2464, 2465, 18536]},
        },
    )
    partner_id = 1
    response = await request_proxy_advert_campaigns(
        taxi_eats_restapp_marketing, partner_id,
    )

    assert response.status_code == 200
    campaigns = {}
    for campaign in response.json()['campaigns']:
        campaigns[campaign['place_id']] = [
            campaign['status'],
            campaign['campaign_id'],
            campaign['has_access'],
            campaign.get('owner', None),
        ]

    login_1 = {
        'status': 'ok',
        'display_name': 'Козьма Прутков',
        'login': 'login_1',
        'avatar': 'https://avatars.mds.yandex.net/get-yapic/123/40x40',
        'yandex_uid': 1229582676,
    }
    login_2 = {
        'status': 'ok',
        'display_name': 'Козьма Прутков',
        'login': 'login_2',
        'yandex_uid': 1229582678,
    }
    assert campaigns == {
        53468: ['suspended', 399264, True, login_1],
        3965: ['create_error', 399265, False, login_2],
        2465: ['process', 399267, True, None],
        2464: ['active', 399266, True, login_1],
        18536: ['process', 399268, True, login_1],
    }


@pytest.mark.adverts(CPC_ADVERT_1, CPC_ADVERT_2, CPC_ADVERT_3, CPC_ADVERT_4)
async def test_get_advert_camapigns_with_weekly_limit(
        taxi_eats_restapp_marketing,
        mock_any_handler,
        mock_authorizer_allowed,
        mock_blackbox_tokeninfo,
):
    await mock_any_handler(
        url='/eats-restapp-authorizer/place-access/list',
        response={
            'status': 200,
            'json': {'place_ids': [53468, 3965, 2464, 2465]},
        },
    )

    partner_id = 1
    response = await request_proxy_advert_campaigns(
        taxi_eats_restapp_marketing, partner_id,
    )

    assert response.status_code == 200
    campaigns = {}
    for campaign in response.json()['campaigns']:
        campaigns[campaign['place_id']] = [
            campaign['status'],
            campaign['campaign_id'],
            campaign['weekly_spend_limit'],
            campaign['has_access'],
        ]
    assert campaigns == {
        53468: ['suspended', 399264, 1, True],
        3965: ['process', 399265, 2, False],
        2465: ['process', 399267, 4, True],
        2464: ['active', 399266, 3, True],
    }


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_ADVERT_RATING_THRESHOLD={
        'rating_threshold': 3.5,
        'is_enabled': True,
        'batch_size': 1000,
        'periodic': {'interval_seconds': 3600},
    },
)
@pytest.mark.adverts(CPC_ADVERT_1, CPC_ADVERT_2, CPC_ADVERT_3, CPC_ADVERT_4)
async def test_get_advert_camapigns_with_rating_ok(
        taxi_eats_restapp_marketing,
        mock_any_handler,
        mock_authorizer_allowed,
        mock_blackbox_tokeninfo,
        mockserver,
):
    await mock_any_handler(
        url='/eats-restapp-authorizer/place-access/list',
        response={
            'status': 200,
            'json': {'place_ids': [53468, 3965, 2464, 2465]},
        },
    )

    @mockserver.json_handler(
        '/eats-place-rating/eats/v1/eats-place-rating/v1/places-rating-info',
    )
    def _mock_rating_info(request):
        res = {'places_rating_info': []}
        rating_test = {'2464': 3.0, '2465': 3.5, '3965': 4.0, '53468': 2.0}
        for place_id in request.query['place_ids'].split(','):
            res['places_rating_info'].append(
                {
                    'average_rating': rating_test[place_id],
                    'calculated_at': '2021-01-01',
                    'cancel_rating': 4.0,
                    'place_id': int(place_id),
                    'show_rating': True,
                    'user_rating': 4.0,
                },
            )
        return mockserver.make_response(status=200, json=res)

    partner_id = 1
    response = await request_proxy_advert_campaigns(
        taxi_eats_restapp_marketing, partner_id,
    )

    assert response.status_code == 200
    campaigns = {}
    for campaign in response.json()['campaigns']:
        campaigns[campaign['place_id']] = [
            campaign['status'],
            campaign['campaign_id'],
            campaign['weekly_spend_limit'],
            campaign['has_access'],
            campaign['is_rating_status_ok'],
        ]
    assert campaigns == {
        53468: ['suspended', 399264, 1, True, False],
        3965: ['process', 399265, 2, False, True],
        2465: ['process', 399267, 4, True, True],
        2464: ['active', 399266, 3, True, False],
    }


async def request_proxy_advert_resume(
        taxi_eats_restapp_marketing, partner_id, place_id, operation,
):
    url = '/4.0/restapp-front/marketing/v1/ad/{}?place_id={}'.format(
        operation, place_id,
    )
    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
        'Authorization': 'token',
        'X-Remote-IP': '127.0.0.1',
    }
    extra = {'headers': headers}

    return await taxi_eats_restapp_marketing.post(url, **extra)


@pytest.mark.adverts(
    sql.Advert(
        id=1,
        place_id=53468,
        average_cpc=10,
        campaign_id=399264,
        group_id=4,
        ad_id=5,
        banner_id=1,
    ),
)
async def test_get_advert_resume(
        taxi_eats_restapp_marketing,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_eats_advert_resume,
        mock_blackbox_tokeninfo,
        mock_rating_info_ok,
        pgsql,
):
    partner_id = 1
    place_id = 53468
    operaton = 'resume'
    response = await request_proxy_advert_resume(
        taxi_eats_restapp_marketing, partner_id, place_id, operaton,
    )
    assert response.status_code == 200

    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
            SELECT is_active
            FROM eats_restapp_marketing.advert
            WHERE place_id = %s
            """,
        (place_id,),
    )
    assert list(cursor)[0][0]


@pytest.mark.adverts(
    sql.Advert(
        id=1,
        place_id=53468,
        average_cpc=10,
        campaign_id=399264,
        group_id=4,
        ad_id=5,
        banner_id=1,
    ),
)
async def test_start_end_dates(
        taxi_eats_restapp_marketing,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_eats_advert_resume,
        mock_blackbox_tokeninfo,
        mock_rating_info_ok,
        pgsql,
):
    def fetch_params(place_id):
        cursor = pgsql['eats_restapp_marketing'].cursor()
        cursor.execute(
            """
            SELECT is_active, started_at, suspended_at
            FROM eats_restapp_marketing.advert
            WHERE place_id = %s;
            """,
            (place_id,),
        )
        return list(cursor)

    partner_id = 1
    place_id = 53468
    assert fetch_params(place_id)[0] == (False, None, None)
    await request_proxy_advert_resume(
        taxi_eats_restapp_marketing, partner_id, place_id, 'resume',
    )
    params = fetch_params(place_id)[0]
    assert params[0]
    assert params[1] is not None
    assert params[2] is None

    await request_proxy_advert_resume(
        taxi_eats_restapp_marketing, partner_id, place_id, 'suspend',
    )
    params = fetch_params(place_id)[0]
    assert not params[0]
    assert params[1] is not None
    assert params[2] is not None


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_ADVERT_RATING_THRESHOLD={
        'rating_threshold': 3.5,
        'is_enabled': True,
        'batch_size': 1000,
        'periodic': {'interval_seconds': 3600},
    },
)
@pytest.mark.adverts(CPC_ADVERT_1)
async def test_get_advert_resume_low_rating_400(
        taxi_eats_restapp_marketing,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_eats_advert_resume,
        mock_blackbox_tokeninfo,
        mock_rating_info_low,
        load_json,
):
    partner_id = 1
    place_id = 53468
    operaton = 'resume'
    response = await request_proxy_advert_resume(
        taxi_eats_restapp_marketing, partner_id, place_id, operaton,
    )

    assert response.status_code == 400
    resp = load_json('response_rating_error.json')
    assert response.json() == resp


@pytest.mark.adverts(CPC_ADVERT_1)
async def test_get_advert_resume_error(
        taxi_eats_restapp_marketing,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_eats_advert_resume_error,
        mock_blackbox_tokeninfo,
        mock_rating_info_ok,
):
    partner_id = 1
    place_id = 53468
    operaton = 'resume'
    response = await request_proxy_advert_resume(
        taxi_eats_restapp_marketing, partner_id, place_id, operaton,
    )

    assert response.status_code == 400


@pytest.mark.adverts(
    sql.Advert(
        id=1,
        place_id=53468,
        average_cpc=100,
        campaign_id=399264,
        group_id=4,
        ad_id=5,
        banner_id=1,
        passport_id=1229582678,
    ),
)
async def test_get_advert_access(
        taxi_eats_restapp_marketing,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_eats_advert_resume,
        mock_blackbox_tokeninfo,
):
    partner_id = 1
    place_id = 53468
    operaton = 'resume'
    response = await request_proxy_advert_resume(
        taxi_eats_restapp_marketing, partner_id, place_id, operaton,
    )
    assert response.status_code == 403
    assert response.json()['details']['error_slug'] == 'WRONG_PASSPORT_ACCOUNT'


@pytest.mark.adverts(
    sql.Advert(
        id=1,
        place_id=53468,
        average_cpc=100,
        campaign_id=399264,
        group_id=4,
        ad_id=5,
        banner_id=1,
        is_active=True,
    ),
)
async def test_get_advert_resume_active(
        taxi_eats_restapp_marketing,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_blackbox_tokeninfo,
):
    partner_id = 1
    place_id = 53468
    operaton = 'resume'
    response = await request_proxy_advert_resume(
        taxi_eats_restapp_marketing, partner_id, place_id, operaton,
    )

    assert response.status_code == 200


async def request_proxy_advert_internal(
        taxi_eats_restapp_marketing, limit, cursor=None,
):
    url = '/internal/marketing/v1/ad/campaigns?limit={}'.format(limit)
    if cursor is not None:
        url += '&cursor={}'.format(cursor)

    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}

    return await taxi_eats_restapp_marketing.post(url, **extra)


def load_adverts(eats_restapp_marketing_db, size: int):
    ids = [x for x in range(1, size)]
    random.shuffle(ids)
    while sorted(ids) == ids:
        random.shuffle(ids)

    for i in ids:
        sql.insert_advert(
            eats_restapp_marketing_db,
            advert=sql.Advert(
                id=i,
                place_id=2464 + i,
                average_cpc=10,
                campaign_id=i,
                group_id=4,
                ad_id=5,
                banner_id=i,
                is_active=True,
            ),
        )


async def test_non_ordered_id(
        taxi_eats_restapp_marketing, eats_restapp_marketing_db,
):
    size_table = 20
    load_adverts(eats_restapp_marketing_db, size_table)
    limit = 5

    cursor = None
    common_camp_list = []
    while True:
        response = await request_proxy_advert_internal(
            taxi_eats_restapp_marketing, limit, cursor,
        )
        assert response.status_code == 200
        cursor = response.json()['cursor']
        if not response.json()['campaigns']:
            break
        common_camp_list += [
            id['banner_id'] for id in response.json()['campaigns']
        ]

    expected_list = [v for v in range(1, size_table)]
    assert len(expected_list) == len(common_camp_list)
    common_camp_list.sort()
    assert expected_list == common_camp_list


@pytest.mark.adverts(
    sql.Advert(
        id=1,
        place_id=2464,
        average_cpc=10,
        campaign_id=1,
        group_id=4,
        ad_id=5,
        banner_id=72057603971034011,
        is_active=True,
    ),
    sql.Advert(
        id=2,
        place_id=2465,
        average_cpc=10,
        campaign_id=1,
        group_id=4,
        ad_id=5,
        banner_id=72057603971034012,
        is_active=True,
    ),
    sql.Advert(
        id=3,
        place_id=3965,
        average_cpc=10,
        campaign_id=1,
        group_id=4,
        ad_id=5,
        banner_id=72057603971034013,
        is_active=True,
    ),
    sql.Advert(
        id=4,
        place_id=53468,
        average_cpc=10,
        campaign_id=1,
        group_id=4,
        ad_id=5,
        banner_id=72057603971034016,
        is_active=True,
    ),
    sql.Advert(
        id=5,
        place_id=53468,
        average_cpc=11,
        campaign_id=1,
        group_id=4,
        ad_id=5,
        banner_id=72057603971034016,
        is_active=True,
        experiment='foo_exp_name',
    ),
)
async def test_get_advert_campaigns_internal(taxi_eats_restapp_marketing):
    limit = 3
    response = await request_proxy_advert_internal(
        taxi_eats_restapp_marketing, limit,
    )

    assert response.status_code == 200
    assert len(response.json()['campaigns']) == limit

    cursor = response.json()['cursor']
    campaigns, banner_ids, exp = set(), set(), set()
    for campaign in response.json()['campaigns']:
        campaigns.add(campaign['place_id'])
        banner_ids.add(campaign['banner_id'])

    response = await request_proxy_advert_internal(
        taxi_eats_restapp_marketing, limit, cursor,
    )
    assert response.status_code == 200
    assert len(response.json()['campaigns']) == 2
    for campaign in response.json()['campaigns']:
        campaigns.add(campaign['place_id'])
        banner_ids.add(campaign['banner_id'])
        exp.add(campaign['experiment'])

    assert campaigns == {2464, 2465, 3965, 53468}
    assert banner_ids == {
        72057603971034011,
        72057603971034012,
        72057603971034013,
        72057603971034016,
    }
    assert exp == {'', '', '', '', 'foo_exp_name'}


async def request_proxy_internal_info(taxi_eats_restapp_marketing, place_ids):
    url = '/internal/marketing/v1/ad/campaigns-info'
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}

    return await taxi_eats_restapp_marketing.post(
        url, **extra, json={'place_ids': place_ids},
    )


@pytest.mark.adverts(
    sql.Advert(
        id=1,
        place_id=3965,
        average_cpc=900000,
        campaign_id=396129,
        group_id=4,
        ad_id=72057603971034012,
    ),
)
async def test_get_internal_campaigns_info(taxi_eats_restapp_marketing, pgsql):
    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
        INSERT INTO eats_restapp_marketing.advert_orders_stats  (
            place_id,
            day_orders,
            week_orders,
            month_orders,
            all_orders,
            updated_at
        ) VALUES (
            3965,
            1,
            2,
            3,
            4,
            '2021-01-21T01:02:03+0300'
        );
        """,
    )

    place_ids = [3965, 4945]
    response = await request_proxy_internal_info(
        taxi_eats_restapp_marketing, place_ids,
    )

    assert response.status_code == 200
    assert response.json() == {
        'places': [
            {
                'place_id': 3965,
                'has_campaign': True,
                'averagecpc': 900000,
                'direct_info': {
                    'advert_id': 72057603971034012,
                    'banner_id': None,
                    'campaign_id': 396129,
                    'is_active': False,
                },
                'orders_info': {
                    'all_orders': 4,
                    'day_orders': 1,
                    'month_orders': 3,
                    'updated_at': '2021-01-21T01:02:03',
                    'week_orders': 2,
                },
            },
            {'place_id': 4945, 'has_campaign': False},
        ],
    }


@pytest.mark.adverts(
    sql.Advert(
        id=1,
        place_id=3965,
        average_cpc=900000,
        campaign_id=396129,
        group_id=4,
        ad_id=72057603971034012,
        weekly_spend_limit=10000000,
    ),
)
async def test_get_internal_campaigns_info_with_weekly_spend_limit(
        taxi_eats_restapp_marketing, pgsql,
):
    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
        INSERT INTO eats_restapp_marketing.advert_orders_stats (
            place_id,
            day_orders,
            week_orders,
            month_orders,
            all_orders,
            updated_at
        ) VALUES (
            3965,
            1,
            2,
            3,
            4,
            '2021-03-10T05:00:00+0300'
        );
        """,
    )

    place_ids = [3965, 4945]
    response = await request_proxy_internal_info(
        taxi_eats_restapp_marketing, place_ids,
    )

    assert response.status_code == 200
    assert response.json() == {
        'places': [
            {
                'place_id': 3965,
                'has_campaign': True,
                'averagecpc': 900000,
                'weekly_spend_limit': 10000000,
                'direct_info': {
                    'advert_id': 72057603971034012,
                    'banner_id': None,
                    'campaign_id': 396129,
                    'is_active': False,
                },
                'orders_info': {
                    'all_orders': 4,
                    'day_orders': 1,
                    'month_orders': 3,
                    'updated_at': '2021-03-10T05:00:00',
                    'week_orders': 2,
                },
            },
            {'place_id': 4945, 'has_campaign': False},
        ],
    }


async def request_proxy_balance(taxi_eats_restapp_marketing):
    url = '/4.0/restapp-front/marketing/v1/ad/balance'
    headers = {
        'Content-type': 'application/json',
        'Authorization': 'token',
        'X-Remote-IP': 'localhost',
        'X-YaEda-PartnerId': '1',
    }
    extra = {'headers': headers}

    return await taxi_eats_restapp_marketing.get(url, **extra)


async def test_get_balance(
        taxi_eats_restapp_marketing,
        mock_eats_advert_balance,
        mock_blackbox_tokeninfo,
):
    response = await request_proxy_balance(taxi_eats_restapp_marketing)

    assert response.status_code == 200
    assert response.json() == {'balance': '8333.33', 'currency': 'RUB'}


async def test_get_balance_add_token(
        taxi_eats_restapp_marketing,
        mock_eats_advert_balance,
        mock_blackbox_tokeninfo,
        pgsql,
):
    response = await request_proxy_balance(taxi_eats_restapp_marketing)

    assert response.status_code == 200
    assert response.json() == {'balance': '8333.33', 'currency': 'RUB'}
    # проверяем, что у нас токен добавился в базу
    cursor = pgsql['eats_tokens'].cursor()
    cursor.execute("""SELECT token_id, passport_id FROM eats_tokens.tokens""")
    tokens = list(cursor)
    assert len(tokens) == 1
    token = tokens[0]
    # в моке возвращается именно этот passport_id
    assert token[1] == 1229582676
    # проверяем, что при повторном вызове баланса у нас не добавился лишний
    # токен

    response = await request_proxy_balance(taxi_eats_restapp_marketing)

    assert response.status_code == 200
    assert response.json() == {'balance': '8333.33', 'currency': 'RUB'}

    cursor = pgsql['eats_tokens'].cursor()
    cursor.execute("""SELECT token_id, passport_id FROM eats_tokens.tokens""")
    tokens = list(cursor)
    assert len(tokens) == 1
    token = tokens[0]
    # в моке возвращается именно этот passport_id
    assert token[1] == 1229582676


async def test_wrong_balance_token(
        taxi_eats_restapp_marketing, mock_balance_token_error,
):
    response = await request_proxy_balance(taxi_eats_restapp_marketing)

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'wrong oauth token',
        'details': {'error_slug': 'PASSPORT_TOKEN_ERROR'},
    }
