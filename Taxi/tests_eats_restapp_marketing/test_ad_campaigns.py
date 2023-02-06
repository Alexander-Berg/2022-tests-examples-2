import pytest


@pytest.fixture(name='get_ad_campaigns')
def _get_ad_campaigns(taxi_eats_restapp_marketing):
    """
    Фикстура для запросов в ручку
    `/4.0/restapp-front/marketing/v1/ad/campaigns`
    """

    url = '/4.0/restapp-front/marketing/v1/ad/campaigns'

    async def get(partner_id: int = 1):
        headers = {
            'X-YaEda-PartnerId': str(partner_id),
            'x-remote-ip': 'localhost',
            'Authorization': 'token',
        }
        return await taxi_eats_restapp_marketing.get(url, headers=headers)

    return get


@pytest.mark.pgsql('eats_restapp_marketing', files=['insert_campaigns.sql'])
@pytest.mark.now('2020-01-01T12:00:00Z')
@pytest.mark.parametrize(
    'place_ids, campaigns',
    (
        pytest.param([], [], id='no place ids'),
        pytest.param([10, 11, 12], [], id='no campaigns for places'),
        pytest.param(
            [4],
            [
                {
                    'campaign_type': 'cpc',
                    'advert_id': 4,
                    'place_id': 4,
                    'has_access': True,
                    'status': 'active',
                    'campaign_id': 1,
                    'is_rating_status_ok': True,
                    'average_cpc': 10,
                },
            ],
            id='single campaign in response',
        ),
        pytest.param(
            [4, 6],
            [
                {
                    'campaign_type': 'cpc',
                    'advert_id': 4,
                    'place_id': 4,
                    'has_access': True,
                    'status': 'active',
                    'campaign_id': 1,
                    'is_rating_status_ok': True,
                    'average_cpc': 10,
                },
                {
                    'campaign_type': 'cpc',
                    'advert_id': 6,
                    'place_id': 6,
                    'has_access': True,
                    'status': 'active',
                    'campaign_id': 3,
                    'is_rating_status_ok': True,
                    'average_cpc': 30,
                },
            ],
            id='not even campaigns',
        ),
    ),
)
async def test_request_ad_campaigns(
        taxi_eats_restapp_marketing,
        mockserver,
        mock_any_handler,
        mock_blackbox_tokeninfo,
        place_ids,
        campaigns,
        get_ad_campaigns,
):
    auth_list_places_handler = await mock_any_handler(
        url='/eats-restapp-authorizer/place-access/list',
        response={'status': 200, 'json': {'place_ids': place_ids}},
    )

    response = await get_ad_campaigns(partner_id='1')

    assert response.status_code == 200
    assert auth_list_places_handler.times_called == 1

    assert campaigns == response.json()['campaigns']


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_ADVERT_RATING_THRESHOLD={
        'rating_threshold': 3.5,
        'is_enabled': True,
        'batch_size': 1000,
        'periodic': {'interval_seconds': 3600},
    },
)
@pytest.mark.now('2020-01-01T12:00:00Z')
@pytest.mark.parametrize(
    'place_ids, campaigns',
    (
        pytest.param(
            [1],
            [
                {
                    'campaign_type': 'cpc',
                    'advert_id': 1,
                    'place_id': 1,
                    'has_access': True,
                    'status': 'active',
                    'campaign_id': 1,
                    'is_rating_status_ok': True,
                    'average_cpc': 10,
                    'started_at': '2021-01-01T09:05:01.358114+0000',
                    'suspended_at': '2021-01-10T09:05:01.358514+0000',
                },
            ],
            id='single campaign in response',
        ),
        pytest.param(
            [1, 3],
            [
                {
                    'campaign_type': 'cpc',
                    'advert_id': 1,
                    'place_id': 1,
                    'has_access': True,
                    'status': 'active',
                    'campaign_id': 1,
                    'is_rating_status_ok': True,
                    'average_cpc': 10,
                    'started_at': '2021-01-01T09:05:01.358114+0000',
                    'suspended_at': '2021-01-10T09:05:01.358514+0000',
                },
                {
                    'campaign_type': 'cpc',
                    'advert_id': 3,
                    'place_id': 3,
                    'has_access': True,
                    'status': 'active',
                    'campaign_id': 3,
                    'is_rating_status_ok': True,
                    'average_cpc': 30,
                    'started_at': '2020-01-01T10:05:01.358114+0000',
                    'created_at': '2019-01-01T10:05:01.358114+0000',
                },
            ],
            id='not even campaigns',
        ),
        pytest.param(
            [1],
            [
                {
                    'campaign_type': 'cpc',
                    'advert_id': 1,
                    'place_id': 1,
                    'has_access': True,
                    'status': 'active',
                    'campaign_id': 1,
                    'is_rating_status_ok': True,
                    'average_cpc': 10,
                    'started_at': '2021-01-01T09:05:01.358114+0000',
                    'suspended_at': '2021-01-10T09:05:01.358514+0000',
                },
                {
                    'campaign_type': 'cpc',
                    'advert_id': 3,
                    'place_id': 1,
                    'has_access': True,
                    'status': 'active',
                    'campaign_id': 3,
                    'is_rating_status_ok': True,
                    'average_cpc': 30,
                    'started_at': '2020-01-01T10:05:01.358114+0000',
                    'created_at': '2019-01-01T10:05:01.358114+0000',
                    'experiment': 'foo_name_exp',
                },
            ],
            id='exclude experimental',
        ),
    ),
)
@pytest.mark.pgsql('eats_restapp_marketing', files=['insert_campaigns.sql'])
async def test_request_ad_campaigns_with_rating(
        taxi_eats_restapp_marketing,
        mockserver,
        mock_any_handler,
        pgsql,
        mock_blackbox_tokeninfo,
        place_ids,
        campaigns,
        get_ad_campaigns,
):
    auth_list_places_handler = await mock_any_handler(
        url='/eats-restapp-authorizer/place-access/list',
        response={'status': 200, 'json': {'place_ids': place_ids}},
    )

    @mockserver.json_handler(
        '/eats-place-rating/eats/v1/eats-place-rating/v1/places-rating-info',
    )
    def _mock_rating_info(request):
        res = {'places_rating_info': []}
        for place_id in request.query['place_ids'].split(','):
            res['places_rating_info'].append(
                {
                    'average_rating': 4.4,
                    'calculated_at': '2021-01-01',
                    'cancel_rating': 4.0,
                    'place_id': int(place_id),
                    'show_rating': True,
                    'user_rating': 4.0,
                },
            )
        return mockserver.make_response(status=200, json=res)

    response = await get_ad_campaigns(partner_id='1')
    assert response.status_code == 200
    assert auth_list_places_handler.times_called == 1

    campaigns_excl = [camp for camp in campaigns if not 'experiment' in camp]
    assert campaigns_excl == response.json()['campaigns']
    assert response.json()['meta'] == {'rating_threshold': 3.5}
