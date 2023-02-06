import pytest

DELETE_PATH: str = '/4.0/restapp-front/marketing/v1/ad/delete'
DELETE_YUID_PATH: str = '/4.0/restapp-front/marketing/v1/ad/delete_for_user'


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


@pytest.mark.pgsql('eats_restapp_marketing', files=['insert_adverts.sql'])
@pytest.mark.parametrize(
    'headers,response_code,request_dict,authorizer_code,remove_data',
    [
        ({}, 400, {'adverts': [{'id': 1114}]}, 400, [(1114, 329210)]),
        (
            {'X-YaEda-PartnerId': '123'},
            403,
            {'adverts': [{'id': 1114}]},
            403,
            [(1114, 329210)],
        ),
        (
            {'X-YaEda-PartnerId': '123'},
            200,
            {'adverts': [{'id': 1114}]},
            200,
            [(1114, 329210)],
        ),
        (
            {'X-YaEda-PartnerId': '123'},
            200,
            {'adverts': [{'id': 1114}, {'id': 3913}]},
            200,
            [(1114, 329210), (3913, 403354)],
        ),
    ],
)
@pytest.mark.now('2021-08-05T12:00:00+00:00')
async def test_delete_advert_campaign(
        taxi_eats_restapp_marketing,
        mockserver,
        pgsql,
        headers,
        response_code,
        request_dict,
        authorizer_code,
        remove_data,
):
    # get ids
    ids_list = []
    for item in request_dict['adverts']:
        ids_list.append(str(item['id']))
    ids = ','.join(ids_list)

    # check advert
    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        'SELECT id,place_id FROM eats_restapp_marketing.advert '
        'WHERE id IN ({})'.format(ids),
    )
    assert list(cursor) == remove_data

    # mock authorizer
    mock_restapp_authorizer(mockserver, authorizer_code)
    # send delete request
    response = await taxi_eats_restapp_marketing.post(
        DELETE_PATH, headers=headers, json=request_dict,
    )

    # check response
    assert response.status_code == response_code

    # check removed
    cursor.execute(
        'SELECT id,place_id FROM eats_restapp_marketing.advert '
        'WHERE id IN ({})'.format(ids),
    )
    if authorizer_code == 200:
        assert list(cursor) == []
    else:
        assert list(cursor) == remove_data

    # check moved adverts
    cursor.execute(
        'SELECT id,place_id FROM eats_restapp_marketing.deleted_adverts '
        'WHERE id IN ({})'.format(ids),
    )
    if authorizer_code == 200:
        assert list(cursor) == remove_data
    else:
        assert list(cursor) == []


@pytest.mark.pgsql('eats_restapp_marketing', files=['insert_adverts.sql'])
@pytest.mark.parametrize(
    'headers,response_code,request_dict,authorizer_code,place_ids,remove_data',
    [
        ({}, 400, {'yandex_uid': '123123'}, 400, [11111, 11112], []),
        (
            {'X-YaEda-PartnerId': '123'},
            200,
            {'yandex_uid': '123123'},
            200,
            [11111, 11112],
            [],
        ),
        (
            {'X-YaEda-PartnerId': '111'},
            403,
            {'yandex_uid': '111111'},
            403,
            [1114, 329210],
            [(1114, 329210)],
        ),
        (
            {'X-YaEda-PartnerId': '123'},
            200,
            {'yandex_uid': '111111'},
            200,
            [1114, 11112, 329210],
            [(1114, 329210)],
        ),
    ],
)
@pytest.mark.now('2021-08-05T12:00:00+00:00')
async def test_delete_for_user_advert_campaign(
        taxi_eats_restapp_marketing,
        mockserver,
        pgsql,
        headers,
        response_code,
        request_dict,
        authorizer_code,
        place_ids,
        remove_data,
):
    place_ids_a = []
    for i in place_ids:
        place_ids_a.append(str(i))
    place_ids_str = ','.join(place_ids_a)

    # check advert
    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        'SELECT id,place_id FROM eats_restapp_marketing.advert '
        'WHERE place_id IN ({})'.format(place_ids_str),
    )
    assert list(cursor) == remove_data

    # mock authorizer
    mock_restapp_authorizer(mockserver, authorizer_code)
    mock_restapp_authorizer_list(mockserver, place_ids)

    # send delete request
    response = await taxi_eats_restapp_marketing.post(
        DELETE_YUID_PATH, headers=headers, json=request_dict,
    )

    # check response
    assert response.status_code == response_code

    # check removed
    cursor.execute(
        'SELECT id,place_id FROM eats_restapp_marketing.advert '
        'WHERE place_id IN ({})'.format(place_ids_str),
    )
    if authorizer_code == 200:
        assert list(cursor) == []
    else:
        assert list(cursor) == remove_data

    # check moved adverts
    cursor.execute(
        'SELECT id,place_id FROM eats_restapp_marketing.deleted_adverts '
        'WHERE place_id IN ({})'.format(place_ids_str),
    )
    if authorizer_code == 200:
        assert list(cursor) == remove_data
    else:
        assert list(cursor) == []
