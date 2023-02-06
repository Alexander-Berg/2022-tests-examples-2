import pytest


@pytest.mark.now('2021-04-01T00:00:00+0000')
@pytest.mark.parametrize(
    'max_addresses,has_routehistory,has_eats,same_address,response_size',
    [
        pytest.param(2, True, True, False, 2, id='both have answers'),
        pytest.param(2, True, False, False, 1, id='only routehistory'),
        pytest.param(2, False, True, False, 1, id='only eats'),
        pytest.param(2, False, False, False, 0, id='none'),
        pytest.param(2, True, True, True, 1, id='both but same answer'),
        pytest.param(1, True, True, False, 1, id='both but limit'),
    ],
)
async def test_basic(
        taxi_grocery_api,
        yamaps_local,
        load_json,
        taxi_config,
        mockserver,
        has_routehistory,
        has_eats,
        same_address,
        response_size,
        max_addresses,
        now,
):

    uid = '80085'
    bound_uid = 'some_other_uid'
    location = [35.0, 53.0]
    place_id = 'ymapsbm1://some_uri'
    eats_comment = 'Its a trap!'
    taxi_comment = 'Never gonna give you up!'
    days_count = 31
    eats_floor = '11'

    eats_response = {
        'addresses': [
            {
                'location': location,
                'comment': eats_comment,
                'floor': eats_floor,
            },
        ],
    }
    routehistory_response = {
        'results': [
            {
                'order_id': 'order_id',
                'yandex_uid': uid,
                'created': '2021-03-02T00:00:00+0000',
                'position': location,
                'uri': place_id,
                'comment_courier': taxi_comment,
            },
        ],
    }

    geocoder_address = load_json('geocoder-response.json')['geocoder'][
        'address'
    ]

    @mockserver.json_handler('/eats-core-integrations/users/addresses')
    def mock_eats_core(request):
        assert request.json['user_identity']['yandex_uid'] == uid
        assert set(request.json['user_identity']['bound_yandex_uids']) == set(
            [uid, bound_uid],
        )

        if not has_eats:
            return mockserver.make_response(status=500)

        if same_address:
            eats_response['addresses'][0]['city'] = (
                geocoder_address['locality'],
            )
            eats_response['addresses'][0]['house'] = (
                geocoder_address['house'],
            )
            eats_response['addresses'][0]['street'] = geocoder_address[
                'street'
            ]
            return mockserver.make_response(json=eats_response, status=200)

        return mockserver.make_response(json=eats_response, status=200)

    @mockserver.json_handler('/routehistory/routehistory/grocery-get')
    def mock_routehistory(request):
        assert request.json['created_since'] == '2021-03-01T00:00:00+0000'

        if not has_routehistory:
            return mockserver.make_response(
                json={'code': 'GIT_GUD', 'message': 'you died'}, status=500,
            )

        return mockserver.make_response(json=routehistory_response, status=200)

    request_json = {'days_count': days_count, 'addresses_count': max_addresses}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/get-history-addresses',
        json=request_json,
        headers={
            'X-YaTaxi-Session': 'taxi:session',
            'X-Yandex-UID': uid,
            'X-YaTaxi-Bound-Uids': uid + ',' + bound_uid,
        },
    )

    assert response.status_code == 200

    assert response_size == len(response.json()['addresses'])

    # Retries mess up counters by config
    if has_eats:
        assert mock_eats_core.times_called == 1
    if has_routehistory:
        assert mock_routehistory.times_called == 1

    if has_routehistory:
        assert response.json()['addresses'][0] == {
            'location': location,
            'place_id': place_id,
            'city': geocoder_address['locality'],
            'house': geocoder_address['house'],
            'street': geocoder_address['street'],
            'comment': taxi_comment,
            'address_source': 'routehistory',
        }
    if not has_routehistory and has_eats:
        assert response.json()['addresses'][0] == {
            'place_id': '',
            'location': location,
            'comment': eats_comment,
            'floor': eats_floor,
            'address_source': 'eats',
        }
