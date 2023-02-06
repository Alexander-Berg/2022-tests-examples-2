import pytest


def make_campaign(
        name='рога и копыта', averagecrc=1000000, weekly_spend_limit=None,
) -> dict:
    averagecpc_json = {'AverageCpc': averagecrc}
    if weekly_spend_limit is not None:
        averagecpc_json['WeeklySpendLimit'] = weekly_spend_limit

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
                                'AverageCpc': averagecpc_json,
                                'BiddingStrategyType': 'AVERAGE_CPC',
                            },
                        },
                    },
                },
            ],
        },
    }
    return result


async def test_update_price_400(taxi_eats_restapp_marketing):
    # 400 - либо advert_id либо place_id
    response = await taxi_eats_restapp_marketing.post(
        '/4.0/restapp-front/marketing/v1/ad/update-price?place_id=123',
        headers={
            'Authorization': 'new_token',
            'X-Remote-IP': '127.0.0.1',
            'X-YaEda-PartnerId': '2',
        },
        json={'averagecpc': 1, 'weekly_spend_limit': 3, 'advert_id': 1114},
    )
    assert response.status_code == 400
    # 400 - required: advert_id либо place_id
    response = await taxi_eats_restapp_marketing.post(
        '/4.0/restapp-front/marketing/v1/ad/update-price',
        headers={
            'Authorization': 'new_token',
            'X-Remote-IP': '127.0.0.1',
            'X-YaEda-PartnerId': '2',
        },
        json={'averagecpc': 1, 'weekly_spend_limit': 3},
    )
    assert response.status_code == 400


@pytest.mark.pgsql('eats_restapp_marketing', files=['insert_adverts.sql'])
@pytest.mark.pgsql('eats_tokens', files=['insert_token.sql'])
async def test_update_price_403(taxi_eats_restapp_marketing):
    # 403 - разные passport_id
    response = await taxi_eats_restapp_marketing.post(
        '/4.0/restapp-front/marketing/v1/ad/update-price',
        headers={
            'Authorization': 'new_token',
            'X-Remote-IP': '127.0.0.1',
            'X-YaEda-PartnerId': '2',
        },
        json={'averagecpc': 1, 'weekly_spend_limit': 3, 'advert_id': 1114},
    )
    assert response.status_code == 403


@pytest.mark.now('2021-10-01T12:00:00+00:00')
@pytest.mark.pgsql('eats_restapp_marketing', files=['insert_adverts.sql'])
@pytest.mark.pgsql('eats_tokens', files=['insert_token.sql'])
async def test_update_price(
        taxi_eats_restapp_marketing,
        mockserver,
        mock_authorizer_allowed,
        mock_auth_partner,
        mock_blackbox_one,
        stq,
        pgsql,
):
    @mockserver.json_handler('/direct/json/v5/campaignsext')
    def _campaign_handler(request):
        assert request.headers['Authorization'].count('Bearer') == 1
        return mockserver.make_response(
            status=200, json={'result': make_campaign(weekly_spend_limit=3)},
        )

    response = await taxi_eats_restapp_marketing.post(
        '/4.0/restapp-front/marketing/v1/ad/update-price',
        headers={
            'Authorization': 'new_token',
            'X-Remote-IP': '127.0.0.1',
            'X-YaEda-PartnerId': '2',
        },
        json={'averagecpc': 1, 'weekly_spend_limit': 3, 'advert_id': 1111},
    )
    assert response.status_code == 200

    cursor = pgsql['eats_restapp_marketing'].cursor()

    cursor.execute(
        """
        SELECT averagecpc, weekly_spend_limit
        FROM eats_restapp_marketing.advert
        WHERE campaign_id = 59633948
    """,
    )
    for data in cursor:
        assert data[0] == 1000000
        assert data[1] == 3000000

    assert response.json() == {
        'campaigns': [
            {
                'advert_id': 1111,
                'average_cpc': 1,
                'campaign_id': 59633948,
                'created_at': '2021-05-23T08:35:16.788372+0000',
                'has_access': True,
                'is_rating_status_ok': True,
                'place_id': 333330,
                'started_at': '2021-07-29T07:18:02.618373+0000',
                'status': 'active',
                'weekly_spend_limit': 3,
                'owner': {
                    'avatar': (
                        'https://avatars.mds.yandex.net/get-yapic/123/40x40'
                    ),
                    'display_name': 'Козьма Прутков',
                    'login': 'login_1',
                    'status': 'ok',
                    'yandex_uid': 1229582676,
                },
            },
            {
                'advert_id': 2222,
                'average_cpc': 1,
                'campaign_id': 59633948,
                'created_at': '2021-07-10T13:48:31.781907+0000',
                'has_access': True,
                'is_rating_status_ok': True,
                'place_id': 444444,
                'started_at': '2021-07-29T07:18:02.618373+0000',
                'status': 'active',
                'weekly_spend_limit': 3,
                'owner': {
                    'avatar': (
                        'https://avatars.mds.yandex.net/get-yapic/123/40x40'
                    ),
                    'display_name': 'Козьма Прутков',
                    'login': 'login_1',
                    'status': 'ok',
                    'yandex_uid': 1229582676,
                },
            },
        ],
    }
