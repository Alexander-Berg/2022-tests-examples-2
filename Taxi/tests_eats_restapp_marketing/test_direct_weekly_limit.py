# pylint: disable=unused-variable


def make_campaign(
        name='рога и копыта', averagecrc=1000000, weekly_spend_limit=None,
) -> dict:
    result = {
        'method': 'add',
        'params': {
            'Campaigns': [
                {
                    'Name': 'EDA_2',
                    'StartDate': '2020-12-04',
                    'ClientInfo': name,
                    'ContentPromotionCampaign': {
                        'BiddingStrategy': {
                            'Network': {'BiddingStrategyType': 'SERVING_OFF'},
                            'Search': {
                                'AverageCpc': {
                                    'AverageCpc': averagecrc,
                                    'WeeklySpendLimit': weekly_spend_limit,
                                },
                                'BiddingStrategyType': 'AVERAGE_CPC',
                            },
                        },
                    },
                },
            ],
        },
    }

    return result


async def test_direct_update_price(
        taxi_eats_restapp_marketing,
        mockserver,
        mock_auth_partner,
        mock_authorizer_allowed,
        stq,
        pgsql,
):
    @mockserver.json_handler('/blackbox')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=200,
            json={
                'oauth': {
                    'uid': '1229582676',
                    'token_id': '2498905377',
                    'device_id': '',
                    'device_name': '',
                    'scope': 'direct:api',
                    'ctime': '2020-12-07 20:49:55',
                    'issue_time': '2021-03-08 16:15:39',
                    'expire_time': '2022-03-08 16:15:39',
                    'is_ttl_refreshable': True,
                    'client_id': 'cfe379f646f3446ea1e6bc43e1385e3f',
                    'client_name': 'Яндекс.Еда для ресторанов',
                    'client_icon': 'https://avatars.mds.yandex.net/.../normal',
                    'client_homepage': '',
                    'client_ctime': '2020-11-10 13:16:25',
                    'client_is_yandex': False,
                    'xtoken_id': '',
                    'meta': '',
                },
                'uid': {'value': '1229582676', 'lite': False, 'hosted': False},
                'login': 'yndx-eda-direct-test',
                'have_password': True,
                'have_hint': False,
                'aliases': {'1': 'yndx-eda-direct-test'},
                'karma': {'value': 0},
                'karma_status': {'value': 0},
                'dbfields': {'subscription.suid.669': ''},
                'status': {'value': 'VALID', 'id': 0},
                'error': 'OK',
                'connection_id': 't:2498905377',
                'login_id': 's:1592308671257:XXXXX:c',
            },
        )

    @mockserver.json_handler('/direct/json/v5/campaignsext')
    def campaign_handler(request):
        assert request.headers['Authorization'].count('Bearer') == 1
        return mockserver.make_response(
            status=200, json={'result': make_campaign(weekly_spend_limit=3)},
        )

    cursor = pgsql['eats_restapp_marketing'].cursor()

    cursor.execute(
        """INSERT INTO eats_restapp_marketing.advert
        (campaign_id, passport_id, updated_at, place_id,
        averagecpc, weekly_spend_limit, is_active)
        VALUES ({}, {}, NOW(),{},{},{},false);""".format(
            111111, 1229582676, 2, 1000000, 2000000,
        ),
    )

    cursor.execute(
        """
        SELECT averagecpc, passport_id, weekly_spend_limit
        FROM eats_restapp_marketing.advert
        WHERE place_id=2 AND campaign_id IS NOT NULL
    """,
    )
    campaign_info = list(cursor)[0]
    assert campaign_info[0] == 1000000
    assert campaign_info[1] == 1229582676
    assert campaign_info[2] == 2000000

    response = await taxi_eats_restapp_marketing.post(
        '/4.0/restapp-front/marketing/v1/ad/update-price?place_id=2',
        headers={
            'Authorization': 'new_token',
            'X-Remote-IP': '127.0.0.1',
            'X-YaEda-PartnerId': '2',
        },
        json={'averagecpc': 1, 'weekly_spend_limit': 3},
    )
    assert response.status_code == 200

    cursor.execute(
        """
        SELECT averagecpc, passport_id, weekly_spend_limit
        FROM eats_restapp_marketing.advert
        WHERE place_id=2 AND campaign_id IS NOT NULL
    """,
    )
    campaign_info = list(cursor)[0]
    assert campaign_info[0] == 1000000
    assert campaign_info[1] == 1229582676
    assert campaign_info[2] == 3000000

    response = await taxi_eats_restapp_marketing.post(
        '/4.0/restapp-front/marketing/v1/ad/update-price?place_id=2',
        headers={
            'Authorization': 'new_token',
            'X-Remote-IP': '127.0.0.1',
            'X-YaEda-PartnerId': '2',
        },
        json={'averagecpc': 1, 'weekly_spend_limit': 3},
    )
    assert response.status_code == 200

    cursor.execute(
        """
        SELECT averagecpc, passport_id, weekly_spend_limit
        FROM eats_restapp_marketing.advert
        WHERE place_id=2 AND campaign_id IS NOT NULL
    """,
    )
    campaign_info = list(cursor)[0]
    assert campaign_info[0] == 1000000
    assert campaign_info[1] == 1229582676
    assert campaign_info[2] == 3000000

    response = await taxi_eats_restapp_marketing.post(
        '/4.0/restapp-front/marketing/v1/ad/update-price?place_id=2',
        headers={
            'Authorization': 'new_token',
            'X-Remote-IP': '127.0.0.1',
            'X-YaEda-PartnerId': '2',
        },
        json={'averagecpc': 2},
    )
    assert response.status_code == 200

    cursor.execute(
        """
        SELECT averagecpc, passport_id, weekly_spend_limit
        FROM eats_restapp_marketing.advert
        WHERE place_id=2 AND campaign_id IS NOT NULL
    """,
    )
    campaign_info = list(cursor)[0]
    assert campaign_info[0] == 2000000
    assert campaign_info[1] == 1229582676
    assert campaign_info[2] is None


async def test_direct_update_price_400_less_error(
        taxi_eats_restapp_marketing,
        mockserver,
        mock_auth_partner,
        mock_authorizer_allowed,
        stq,
        pgsql,
):
    @mockserver.json_handler('/blackbox')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=200,
            json={
                'oauth': {
                    'uid': '1229582676',
                    'token_id': '2498905377',
                    'device_id': '',
                    'device_name': '',
                    'scope': 'direct:api',
                    'ctime': '2020-12-07 20:49:55',
                    'issue_time': '2021-03-08 16:15:39',
                    'expire_time': '2022-03-08 16:15:39',
                    'is_ttl_refreshable': True,
                    'client_id': 'cfe379f646f3446ea1e6bc43e1385e3f',
                    'client_name': 'Яндекс.Еда для ресторанов',
                    'client_icon': 'https://avatars.mds.yandex.net/.../normal',
                    'client_homepage': '',
                    'client_ctime': '2020-11-10 13:16:25',
                    'client_is_yandex': False,
                    'xtoken_id': '',
                    'meta': '',
                },
                'uid': {'value': '1229582676', 'lite': False, 'hosted': False},
                'login': 'yndx-eda-direct-test',
                'have_password': True,
                'have_hint': False,
                'aliases': {'1': 'yndx-eda-direct-test'},
                'karma': {'value': 0},
                'karma_status': {'value': 0},
                'dbfields': {'subscription.suid.669': ''},
                'status': {'value': 'VALID', 'id': 0},
                'error': 'OK',
                'connection_id': 't:2498905377',
                'login_id': 's:1592308671257:XXXXX:c',
            },
        )

    cursor = pgsql['eats_restapp_marketing'].cursor()

    cursor.execute(
        """INSERT INTO eats_restapp_marketing.advert
        (campaign_id, passport_id, updated_at, place_id,
        averagecpc, weekly_spend_limit, is_active)
        VALUES ({}, {}, NOW(),{},{},{},false);""".format(
            111111, 1229582676, 2, 1000000, 2000000,
        ),
    )

    cursor.execute(
        """
        SELECT averagecpc, passport_id, weekly_spend_limit
        FROM eats_restapp_marketing.advert
        WHERE place_id=2 AND campaign_id IS NOT NULL
    """,
    )
    campaign_info = list(cursor)[0]
    assert campaign_info[0] == 1000000
    assert campaign_info[1] == 1229582676
    assert campaign_info[2] == 2000000

    response = await taxi_eats_restapp_marketing.post(
        '/4.0/restapp-front/marketing/v1/ad/update-price?place_id=2',
        headers={
            'Authorization': 'new_token',
            'X-Remote-IP': '127.0.0.1',
            'X-YaEda-PartnerId': '2',
        },
        json={'averagecpc': 3, 'weekly_spend_limit': 1},
    )
    assert response.status_code == 400

    cursor.execute(
        """
        SELECT averagecpc, passport_id, weekly_spend_limit
        FROM eats_restapp_marketing.advert
        WHERE place_id=2 AND campaign_id IS NOT NULL
    """,
    )
    campaign_info = list(cursor)[0]
    assert campaign_info[0] == 1000000
    assert campaign_info[1] == 1229582676
    assert campaign_info[2] == 2000000
