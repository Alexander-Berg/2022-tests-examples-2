import pytest

from tests_eats_restapp_marketing import sql

ARCHIVE_CPC_PATH: str = '/4.0/restapp-front/marketing/v1/ad/cpc/archive'
ARCHIVE_CPM_PATH: str = '/4.0/restapp-front/marketing/v1/ad/cpm/archive'


def mock_restapp_authorizer_200(mockserver):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(status=200)


def mock_restapp_authorizer_403(mockserver):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=403,
            json={
                'code': '403',
                'message': 'forbidden',
                'details': {
                    'permissions': ['permission.advert.delete'],
                    'place_ids': [123],
                },
            },
        )


def mock_restapp_authorizer_400(mockserver):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'bad request'},
        )


def mock_restapp_authorizer_list(mockserver, place_ids):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/list')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=200, json={'place_ids': place_ids},
        )


def mock_restapp_authorizer(mockserver, response_status):
    if response_status == 400:
        return mock_restapp_authorizer_400(mockserver)
    if response_status == 403:
        return mock_restapp_authorizer_403(mockserver)
    return mock_restapp_authorizer_200(mockserver)


def fill_tabels(eats_restapp_marketing_db):
    campaign = sql.Campaign(
        id='1111',
        campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
        passport_id=1229582676,
        campaign_id=1,
        parameters={
            'averagecpm': 2,
            'spend_limit': 100,
            'strategy_type': 'kWbMaximumImpressions',
            'start_date': '2022-05-04T10:00:00+03:00',
            'finish_date': '2022-06-04T10:00:00+03:00',
        },
        status=sql.CampaignStatus.ENDED,
    )

    sql.insert_campaign(eats_restapp_marketing_db, campaign)

    banner = sql.Banner(
        id=1,
        place_id=329210,
        inner_campaign_id='1111',
        banner_id=1,
        status=sql.BannerStatus.STOPPED,
    )

    sql.insert_banner(eats_restapp_marketing_db, banner)

    campaign = sql.Campaign(
        id='1112',
        campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
        passport_id=1229582676,
        parameters={
            'averagecpm': 2,
            'spend_limit': 100,
            'strategy_type': 'kWbMaximumImpressions',
            'start_date': '2022-05-04T10:00:00+03:00',
            'finish_date': '2022-06-04T10:00:00+03:00',
        },
        status=sql.CampaignStatus.ACTIVE,
    )

    sql.insert_campaign(eats_restapp_marketing_db, campaign)

    banner = sql.Banner(
        id=2,
        place_id=2,
        inner_campaign_id='1112',
        banner_id=2,
        status=sql.BannerStatus.ACTIVE,
    )

    sql.insert_banner(eats_restapp_marketing_db, banner)

    campaign = sql.Campaign(
        id='1113',
        campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
        passport_id=1229582676,
        parameters={
            'averagecpm': 2,
            'spend_limit': 100,
            'strategy_type': 'kWbMaximumImpressions',
            'start_date': '2022-05-04T10:00:00+03:00',
            'finish_date': '2022-06-04T10:00:00+03:00',
        },
        status=sql.CampaignStatus.ENDED,
    )

    sql.insert_campaign(eats_restapp_marketing_db, campaign)

    banner = sql.Banner(
        id=3,
        place_id=3,
        inner_campaign_id='1113',
        banner_id=3,
        status=sql.BannerStatus.ACTIVE,
    )

    sql.insert_banner(eats_restapp_marketing_db, banner)

    advert = sql.Advert(
        id=1114,
        place_id=329210,
        average_cpc=5000000,
        campaign_id=59633949,
        group_id=4482853598,
        ad_id=10353448896,
        content_id=1356710,
        banner_id=72057604391376832,
        is_active=False,
        passport_id=1229582676,
        campaign_type='CPM',
        strategy_type='average_cpc',
    )

    sql.insert_advert(eats_restapp_marketing_db, advert)

    advert = sql.Advert(
        id=3913,
        place_id=403354,
        average_cpc=15000000,
        campaign_id=62034246,
        group_id=4570457393,
        ad_id=10909254740,
        content_id=2183565,
        banner_id=72057604947182676,
        is_active=True,
        passport_id=1229582676,
        campaign_type='CPM',
        strategy_type='average_cpc',
    )

    sql.insert_advert(eats_restapp_marketing_db, advert)


@pytest.mark.pgsql('eats_tokens', files=['insert_token.sql'])
@pytest.mark.parametrize(
    'headers,'
    'response_code,'
    'request_dict,'
    'direct_response_list,'
    'authorizer_code,'
    'expected_data,'
    'has_db_error',
    [
        (
            {'X-YaEda-PartnerId': '123', 'X-Remote-IP': '127.0.0.1'},
            400,
            {'adverts': [{'id': 1114}]},
            [{'Id': 59633949}],
            400,
            [(1114, None)],
            False,
        ),
        (
            {'X-YaEda-PartnerId': '123', 'X-Remote-IP': '127.0.0.1'},
            403,
            {'adverts': [{'id': 1114}]},
            [{'Id': 59633949}],
            403,
            [(1114, None)],
            False,
        ),
        (
            {'X-YaEda-PartnerId': '2', 'X-Remote-IP': '127.0.0.1'},
            200,
            {'adverts': [{'id': 1114}]},
            [{'Id': 59633949}],
            200,
            [(1114, 'archived')],
            False,
        ),
        (
            {'X-YaEda-PartnerId': '2', 'X-Remote-IP': '127.0.0.1'},
            400,
            {'adverts': [{'id': 3913}]},
            [{'Id': 62034246}],
            200,
            [(3913, None)],
            False,
        ),
        (
            {'X-YaEda-PartnerId': '2', 'X-Remote-IP': '127.0.0.1'},
            500,
            {'adverts': [{'id': 1114}]},
            [{'Id': 59633949}],
            200,
            [(1114, None)],
            True,
        ),
    ],
)
@pytest.mark.now('2021-08-05T12:00:00+00:00')
async def test_archive_cpc_campaign(
        taxi_eats_restapp_marketing,
        mockserver,
        pgsql,
        headers,
        response_code,
        request_dict,
        direct_response_list,
        authorizer_code,
        expected_data,
        mock_authorizer_allowed,
        mock_auth_partner,
        mock_blackbox_one,
        eats_restapp_marketing_db,
        has_db_error,
        testpoint,
):
    fill_tabels(eats_restapp_marketing_db)

    # get ids
    ids_list = []
    for item in request_dict['adverts']:
        ids_list.append(str(item['id']))
    ids = ','.join(ids_list)

    @mockserver.json_handler('/direct/json/v5/campaignsext')
    def _campaign_handler(request):
        assert request.headers['Authorization'].count('Bearer') == 1
        return mockserver.make_response(
            status=200,
            json={'result': {'ArchiveResults': direct_response_list}},
        )

    # mock authorizer
    mock_restapp_authorizer(mockserver, authorizer_code)
    # send delete request

    @testpoint('db_error')
    def _db_error(data):
        return {'db_error': has_db_error}

    response = await taxi_eats_restapp_marketing.post(
        ARCHIVE_CPC_PATH, headers=headers, json=request_dict,
    )

    # check response
    assert response.status_code == response_code

    cursor = pgsql['eats_restapp_marketing'].cursor()
    # check removed

    print(ids)
    cursor.execute(
        'SELECT id, status FROM eats_restapp_marketing.advert '
        'WHERE id IN ({})'.format(ids),
    )
    assert list(cursor) == expected_data


@pytest.mark.pgsql('eats_tokens', files=['insert_token.sql'])
@pytest.mark.parametrize(
    'headers,'
    'response_code,'
    'request_dict,'
    'direct_response_list,'
    'authorizer_code,'
    'expected_data,'
    'has_db_error',
    [
        (
            {
                'X-YaEda-PartnerId': '123',
                'Authorization': 'new_token',
                'X-Remote-IP': '127.0.0.1',
            },
            400,
            {'adverts': [{'id': '1111'}]},
            [{'Id': 1}],
            400,
            [('1111', 'ended')],
            False,
        ),
        (
            {
                'X-YaEda-PartnerId': '123',
                'Authorization': 'new_token',
                'X-Remote-IP': '127.0.0.1',
            },
            403,
            {'adverts': [{'id': '1111'}]},
            [{'Id': 1}],
            403,
            [('1111', 'ended')],
            False,
        ),
        (
            {
                'X-YaEda-PartnerId': '2',
                'Authorization': 'new_token',
                'X-Remote-IP': '127.0.0.1',
            },
            200,
            {'adverts': [{'id': '1111'}]},
            [{'Id': 1}],
            200,
            [('1111', 'archived')],
            False,
        ),
        (
            {
                'X-YaEda-PartnerId': '2',
                'Authorization': 'new_token',
                'X-Remote-IP': '127.0.0.1',
            },
            400,
            {'adverts': [{'id': '1112'}]},
            [{'Id': 2}],
            200,
            [('1112', 'active')],
            False,
        ),
        (
            {
                'X-YaEda-PartnerId': '2',
                'Authorization': 'new_token',
                'X-Remote-IP': '127.0.0.1',
            },
            400,
            {'adverts': [{'id': '1113'}]},
            [{'Id': 3}],
            200,
            [('1113', 'ended')],
            False,
        ),
        (
            {
                'X-YaEda-PartnerId': '2',
                'Authorization': 'new_token',
                'X-Remote-IP': '127.0.0.1',
            },
            500,
            {'adverts': [{'id': '1111'}]},
            [{'Id': 1}],
            200,
            [('1111', 'ended')],
            True,
        ),
    ],
)
@pytest.mark.now('2021-08-05T12:00:00+00:00')
async def test_archive_cpm_campaign(
        taxi_eats_restapp_marketing,
        mockserver,
        pgsql,
        headers,
        response_code,
        request_dict,
        direct_response_list,
        authorizer_code,
        expected_data,
        mock_authorizer_allowed,
        mock_auth_partner,
        mock_blackbox_one,
        eats_restapp_marketing_db,
        has_db_error,
        testpoint,
):

    fill_tabels(eats_restapp_marketing_db)

    # get ids
    ids_list = []
    for item in request_dict['adverts']:
        ids_list.append(str(item['id']))
    ids = ','.join(ids_list)

    @mockserver.json_handler('/direct/json/v5/campaignsext')
    def _campaign_handler(request):
        assert request.headers['Authorization'].count('Bearer') == 1
        return mockserver.make_response(
            status=200,
            json={'result': {'ArchiveResults': direct_response_list}},
        )

    @testpoint('db_error')
    def _db_error(data):
        return {'db_error': has_db_error}

    # mock authorizer
    mock_restapp_authorizer(mockserver, authorizer_code)
    # send delete request
    response = await taxi_eats_restapp_marketing.post(
        ARCHIVE_CPM_PATH, headers=headers, json=request_dict,
    )

    # check response
    assert response.status_code == response_code

    cursor = pgsql['eats_restapp_marketing'].cursor()
    # check removed

    print(ids)
    cursor.execute(
        'SELECT id, status FROM eats_restapp_marketing.campaigns '
        'WHERE id IN (\'{}\')'.format(ids),
    )
    assert list(cursor) == expected_data
