import pytest

# pylint: disable=too-many-lines

MOSCOW_DEMO_LAVKA_LOCATION = [37.655490, 55.737557]  # Moscow
PARIS_DEMO_LAVKA_LOCATION = [2.313999, 48.880812]  # Paris
FRANCE_DEMO_LAVKA_LOCATION = [2.313945, 48.88045]  # Paris
EMPTY_RESPONSE = {'location': [0, 0], 'place_id': ''}

MOSCOW_LOCATION = [37.620963, 55.737982]
LONDON_LOCATION = [-0.103502, 51.504703]
TEL_AVIV_LOCATION = [34.782447, 32.083506]

ADDRESSES_LIMIT = 50

GROCERY_API_DEFAULT_DEPOT_LOCATION = pytest.mark.experiments3(
    name='grocery_api_default_depot_location',
    consumers=['grocery-api/startup'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Moscow',
            'predicate': {
                'init': {
                    'value': 213,
                    'arg_name': 'city_id',
                    'arg_type': 'int',
                },
                'type': 'eq',
            },
            'value': {'location': MOSCOW_DEMO_LAVKA_LOCATION},
        },
        {
            'title': 'London',
            'predicate': {
                'init': {
                    'value': 10393,
                    'arg_name': 'city_id',
                    'arg_type': 'int',
                },
                'type': 'eq',
            },
            'value': {'location': LONDON_LOCATION},
        },
        {
            'title': 'Paris',
            'predicate': {
                'init': {
                    'value': 10502,
                    'arg_name': 'city_id',
                    'arg_type': 'int',
                },
                'type': 'eq',
            },
            'value': {'location': PARIS_DEMO_LAVKA_LOCATION},
        },
        {
            'title': 'France',
            'predicate': {
                'init': {
                    'value': 124,
                    'arg_name': 'country_id',
                    'arg_type': 'int',
                },
                'type': 'eq',
            },
            'value': {'location': FRANCE_DEMO_LAVKA_LOCATION},
        },
    ],
    default_value={'location': MOSCOW_DEMO_LAVKA_LOCATION},
    is_config=True,
)

GROCERY_API_HISTORY_STICKY = pytest.mark.experiments3(
    name='grocery_api_history_sticky',
    consumers=['grocery-api/startup'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Other',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    is_config=True,
)


@GROCERY_API_DEFAULT_DEPOT_LOCATION
@pytest.mark.now('2021-04-01T00:00:00+0000')
@pytest.mark.parametrize(
    'session,eats_location,taxi_location,other_uri,without_uri',
    [
        pytest.param(
            'eats:eatssess',
            [35.0, 53.0],
            [35.1, 52.8],
            False,
            False,
            id='eats location closer, same uri with taxi',
        ),
        pytest.param(
            'eats:eatssess',
            [35.0, 53.0],
            [35.1, 52.8],
            False,
            True,
            id='eats location closer, same uri with taxi, without uri',
        ),
        pytest.param(
            'eats:eatssess',
            [35.0, 53.0],
            [35.1, 52.8],
            True,
            False,
            id='eats location closer, other uri',
        ),
        pytest.param(
            'taxi:taxisess',
            [35.5, 53.7],
            [35.1, 52.8],
            True,
            False,
            id='taxi location closer',
        ),
        pytest.param(
            'taxi:taxisess',
            [35.5, 53.7],
            [35.1, 52.8],
            True,
            True,
            id='taxi location closer, without uri',
        ),
        pytest.param(
            'outofrange',
            [33.5, 53.7],
            [33.1, 52.8],
            True,
            False,
            id='taxi location closer, but both outh of range',
        ),
        pytest.param(
            'outofrange',
            [33.5, 53.7],
            [33.1, 52.8],
            True,
            True,
            id='taxi location closer, but both outh of range, without uri',
        ),
        pytest.param(
            'taxi:somesess',
            None,
            [35.0, 53.0],
            True,
            False,
            id='no eats location',
        ),
        pytest.param(
            'eats:somesess',
            [35.0, 53.0],
            None,
            True,
            False,
            id='no taxi location',
        ),
        pytest.param(
            'nohistory', None, None, True, False, id='no good response',
        ),
        pytest.param('demolavka', None, None, True, True, id='demo lavka'),
    ],
)
async def test_basic(
        taxi_grocery_api,
        yamaps_local,
        persuggest,
        eats_core_integrations,
        routehistory,
        load_json,
        taxi_config,
        session,
        eats_location,
        taxi_location,
        other_uri,
        without_uri,
):

    taxi_config.set_values(
        {
            'GROCERY_API_ADDRESS_SEARCH_BY_COUNTRY': {
                '__default__': {'search_radius': 25},
                'RU': {'search_radius': 85000},
            },
        },
    )

    uid = '80085'
    bound_uid = 'some_other_uid'
    country = 'Russian Federation'
    country_code = 'RU'
    postal_code = '123112'
    house = '141'
    location = [35.0, 53.0]
    place_id = 'ymapsbm1://some_uri'
    place_id_response = place_id
    persuggest_building_id = 'some_persuggest_building_id'
    if other_uri:
        place_id_response = place_id_response + '_other'
    eats_comment = 'Its a trap!'
    taxi_comment = 'Never gonna give you up!'

    eats_core_integrations.set_data(
        uid=uid,
        bound_uid=bound_uid,
        addresses=[
            {
                'location': eats_location,
                'comment': eats_comment,
                'floor': '11',
            },
        ],
    )

    routehistory.set_data(
        created_since='2021-03-01T00:00:00+0000',
        results=[
            {
                'order_id': 'order_id',
                'yandex_uid': uid,
                'created': '2021-03-02T00:00:00+0000',
                'position': taxi_location,
                'uri': place_id_response,
                'comment_courier': taxi_comment,
            },
        ],
    )

    persuggest_place_id = place_id_response
    if without_uri:
        persuggest_place_id = place_id
    persuggest.set_data(
        building_id=persuggest_building_id,
        place_id=persuggest_place_id,
        country=country,
        country_code=country_code,
        postal_code=postal_code,
        house=house,
    )

    request_json = {}
    if without_uri:
        if not session.startswith('demolavka'):
            request_json = {'position': {'location': location}}
    else:
        request_json = {
            'position': {'location': location, 'place_id': place_id},
        }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v2/get-address',
        json=request_json,
        headers={
            'X-YaTaxi-Session': session,
            'X-Yandex-UID': uid,
            'X-YaTaxi-Bound-Uids': uid + ',' + bound_uid,
            'X-Request-Language': 'en',
        },
    )

    assert response.status_code == 200

    geocoder_address = load_json('geocoder-response.json')['geocoder'][
        'address'
    ]
    if session.startswith('eats:'):
        if other_uri:
            assert response.json()['location'] == eats_location
            assert response.json()['comment'] == eats_comment
            assert response.json()['address_source'] == 'eats'
            assert response.json()['place_id'] == place_id_response
            assert not response.json()['need_confirm']
            assert not response.json()['is_new_address']
        else:
            assert response.json()['location'] == taxi_location
            assert response.json()['comment'] == taxi_comment
            assert response.json()['address_source'] == 'routehistory'
            assert response.json()['place_id'] == place_id_response
            assert not response.json()['need_confirm']
            assert not response.json()['is_new_address']
        assert response.json()['country'] == country
        assert response.json()['country_iso2'] == country_code
        assert response.json()['postal_code'] == postal_code
        assert eats_core_integrations.times_called == 1
    elif session.startswith('taxi:'):
        assert response.json()['location'] == taxi_location
        assert response.json()['house'] == geocoder_address['house']
        assert response.json()['place_id'] == place_id_response
        assert response.json()['country'] == country
        assert response.json()['country_iso2'] == country_code
        assert response.json()['postal_code'] == postal_code
        assert response.json()['comment'] == taxi_comment
        assert response.json()['address_source'] == 'routehistory'
        assert response.json()['street'] == geocoder_address['street']
        assert not response.json()['need_confirm']
        assert not response.json()['is_new_address']
        assert yamaps_local.times_called() == 2
        assert routehistory.times_called == 1
    elif session.startswith('outofrange') or session.startswith('nohistory'):
        assert response.json()['location'] == location
        assert response.json()['place_id'] == place_id
        assert response.json()['city'] == geocoder_address['locality']
        assert response.json()['house'] == house
        assert response.json()['street'] == geocoder_address['street']
        assert response.json()['country'] == country
        assert response.json()['country_iso2'] == country_code
        assert response.json()['postal_code'] == postal_code
        assert response.json()['need_confirm']
        assert response.json()['is_new_address']
    else:  # demo lavka
        assert response.json()['location'] == MOSCOW_DEMO_LAVKA_LOCATION
        assert response.json()['country'] == country
        assert response.json()['country_iso2'] == country_code
        assert response.json()['postal_code'] == postal_code
        assert response.json()['is_demo_lavka']
        assert response.json()['need_confirm']
        assert response.json()['is_new_address']
        assert persuggest.times_called == 1


async def test_not_authorized(taxi_grocery_api, persuggest):
    country = 'Russian Federation'
    country_code = 'RU'
    postal_code = '123112'
    house = '141'
    location = [35.0, 53.0]
    place_id = 'ymapsbm1://some_uri'
    persuggest_building_id = 'some_persuggest_building_id'

    persuggest.set_data(
        building_id=persuggest_building_id,
        place_id=place_id,
        country=country,
        country_code=country_code,
        postal_code=postal_code,
        house=house,
    )

    request_json = {'position': {'location': location, 'place_id': place_id}}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v2/get-address',
        json=request_json,
        headers={'X-Request-Language': 'en'},
    )

    assert response.status_code == 200
    assert 'is_demo_lavka' not in response.json()


@pytest.mark.now('2021-04-01T00:00:00+0000')
@pytest.mark.parametrize(
    'ip_address, expected_location',
    [
        pytest.param('81.195.17.222', MOSCOW_LOCATION, id='Moscow'),
        pytest.param('134.213.201.140', LONDON_LOCATION, id='London'),
        pytest.param(
            '77.111.250.174',
            PARIS_DEMO_LAVKA_LOCATION,
            id='Paris, but have no orders',
        ),
        pytest.param(
            '139.124.0.0',
            FRANCE_DEMO_LAVKA_LOCATION,
            id='France, but have no orders',
        ),
    ],
)
@GROCERY_API_DEFAULT_DEPOT_LOCATION
async def test_authorized_without_position(
        taxi_grocery_api,
        eats_core_integrations,
        routehistory,
        persuggest,
        ip_address,
        expected_location,
):
    uid = '80085'
    bound_uid = 'some_other_uid'
    session = 'taxi:taxisess'
    country = 'Russian Federation'
    country_code = 'RU'
    house = '141'
    postal_code = '123112'
    place_id = 'ymapsbm1://some_uri'
    persuggest_building_id = 'some_persuggest_building_id'

    eats_core_integrations.set_data(
        uid=uid,
        bound_uid=bound_uid,
        addresses=[
            {
                'location': [35.5, 53.7],
                'comment': 'eats_comment',
                'floor': '11',
            },
        ],
    )

    routehistory.set_data(
        created_since='2021-03-01T00:00:00+0000',
        results=[
            {
                'order_id': 'order_id',
                'yandex_uid': uid,
                'created': '2021-03-02T00:00:00+0000',
                'position': MOSCOW_LOCATION,  # Moscow
                'uri': 'place_id_moscow1',
                'comment_courier': 'taxi_comment',
            },
            {
                'order_id': 'order_id',
                'yandex_uid': uid,
                'created': '2021-03-01T00:00:00+0000',
                'position': [37.620962, 55.737982],  # Moscow
                'uri': 'place_id_moscow2',
                'comment_courier': 'taxi_comment',
            },
            {
                'order_id': 'order_id',
                'yandex_uid': uid,
                'created': '2021-03-01T00:00:00+0000',
                'position': LONDON_LOCATION,  # London
                'uri': 'place_id_london',
                'comment_courier': 'taxi_comment',
            },
        ],
    )

    persuggest.set_data(
        building_id=persuggest_building_id,
        place_id=place_id,
        country=country,
        country_code=country_code,
        postal_code=postal_code,
        house=house,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v2/get-address',
        json={},
        headers={
            'X-YaTaxi-Session': session,
            'X-Yandex-UID': uid,
            'X-YaTaxi-Bound-Uids': uid + ',' + bound_uid,
            'X-Remote-IP': ip_address,
            'X-Request-Language': 'en',
        },
    )

    assert response.status_code == 200
    assert routehistory.times_called == 1
    assert eats_core_integrations.times_called == 1
    assert response.json()['location'] == expected_location


@pytest.mark.now('2021-03-10T00:00:00+0000')
@GROCERY_API_HISTORY_STICKY
@pytest.mark.parametrize(
    'request_json, expected_location',
    [
        pytest.param(
            {'region_id': 131, 'history_sticky': True},  # Tel Aviv
            TEL_AVIV_LOCATION,
            id='Tel Aviv',
        ),
        pytest.param(
            {
                'position': {'location': [-0.103502, 51.454703]},
                'history_sticky': True,
            },
            LONDON_LOCATION,
            id='London',
        ),
    ],
)
async def test_region_id_without_ip(
        taxi_grocery_api,
        eats_core_integrations,
        routehistory,
        persuggest,
        request_json,
        expected_location,
):
    uid = '80085'
    bound_uid = 'some_other_uid'
    session = 'taxi:taxisess'
    country = 'Russian Federation'
    country_code = 'RU'
    house = '141'
    postal_code = '123112'
    place_id = 'ymapsbm1://some_uri'
    persuggest_building_id = 'some_persuggest_building_id'

    eats_core_integrations.set_data(
        uid=uid,
        bound_uid=bound_uid,
        addresses=[
            {
                'location': [35.5, 53.7],
                'comment': 'eats_comment',
                'floor': '11',
            },
        ],
    )

    routehistory.set_data(
        created_since='2021-02-07T00:00:00+0000',
        results=[
            {
                'order_id': 'order_id',
                'yandex_uid': uid,
                'created': '2021-03-02T00:00:00+0000',
                'position': MOSCOW_LOCATION,
                'uri': 'place_id_moscow',
                'comment_courier': 'taxi_comment',
            },
            {
                'order_id': 'order_id',
                'yandex_uid': uid,
                'created': '2021-03-03T00:00:00+0000',
                'position': TEL_AVIV_LOCATION,
                'uri': 'place_id_tel_aviv',
                'comment_courier': 'taxi_comment',
            },
            {
                'order_id': 'order_id',
                'yandex_uid': uid,
                'created': '2021-03-01T00:00:00+0000',
                'position': LONDON_LOCATION,
                'uri': 'place_id_london',
                'comment_courier': 'taxi_comment',
            },
        ],
    )

    persuggest.set_data(
        building_id=persuggest_building_id,
        place_id=place_id,
        country=country,
        country_code=country_code,
        postal_code=postal_code,
        house=house,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v2/get-address',
        json=request_json,
        headers={
            'X-YaTaxi-Session': session,
            'X-Yandex-UID': uid,
            'X-YaTaxi-Bound-Uids': uid + ',' + bound_uid,
            'X-Remote-IP': '81.195.17.222',  # Moscow
            'X-Request-Language': 'en',
        },
    )

    assert response.status_code == 200
    assert routehistory.times_called == 1
    assert eats_core_integrations.times_called == 1
    assert response.json()['location'] == expected_location


@pytest.mark.now('2021-04-01T00:00:00+0000')
@GROCERY_API_HISTORY_STICKY
async def test_history_sticky(
        taxi_grocery_api, persuggest, eats_core_integrations, routehistory,
):
    uid = '80085'
    bound_uid = 'some_other_uid'
    session = 'taxi:taxisess'
    country = 'Russian Federation'
    country_code = 'RU'
    house = '141'
    postal_code = '123112'
    place_id = 'ymapsbm1://some_uri'
    persuggest_building_id = 'some_persuggest_building_id'

    eats_core_integrations.set_data(
        uid=uid,
        bound_uid=bound_uid,
        addresses=[
            {
                'location': [35.5, 53.7],
                'comment': 'eats_comment',
                'floor': '11',
            },
        ],
    )

    routehistory.set_data(
        created_since='2021-03-01T00:00:00+0000',
        results=[
            {
                'order_id': 'order_id',
                'yandex_uid': uid,
                'created': '2021-03-02T00:00:00+0000',
                'position': MOSCOW_LOCATION,
                'uri': 'place_id',
                'comment_courier': 'taxi_comment',
            },
            {
                'order_id': 'order_id_2',
                'yandex_uid': uid,
                'created': '2021-03-03T00:00:00+0000',
                'position': LONDON_LOCATION,
                'uri': 'other_place_id',
                'comment_courier': 'taxi_comment',
            },
        ],
    )

    persuggest.set_data(
        building_id=persuggest_building_id,
        place_id=place_id,
        country=country,
        country_code=country_code,
        postal_code=postal_code,
        house=house,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v2/get-address',
        json={
            'position': {
                'location': [30.325961, 59.939233],
                'place_id': place_id,
            },  # SPB location
            'history_sticky': True,
        },
        headers={
            'X-YaTaxi-Session': session,
            'X-Yandex-UID': uid,
            'X-YaTaxi-Bound-Uids': uid + ',' + bound_uid,
            'X-Request-Language': 'en',
        },
    )

    assert response.status_code == 200
    assert routehistory.times_called == 1
    assert eats_core_integrations.times_called == 1
    assert response.json()['location'] == MOSCOW_LOCATION


@GROCERY_API_DEFAULT_DEPOT_LOCATION
@pytest.mark.parametrize('locale', ['ru', 'en'])
async def test_persuggest_locale(taxi_grocery_api, persuggest, locale):
    persuggest.set_data(
        building_id='some_building_id',
        place_id='some_place_id',
        country='Россия',
        country_code='country_code',
        postal_code='postal_code',
        house='141',
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v2/get-address',
        json={},
        headers={'X-Request-Language': locale},
    )

    assert response.status_code == 200
    assert response.json()['city'] == persuggest.address_info[locale]['city']


@pytest.mark.now('2021-04-01T00:00:00+0000')
async def test_persuggest_error(taxi_grocery_api, persuggest, taxi_config):
    taxi_config.set_values(
        {'GROCERY_API_ADDRESS_DETAILS_SEARCH_DISTANCE': 85000},
    )

    persuggest.set_data(status=500)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v2/get-address',
        json={},
        headers={'X-Request-Language': 'en'},
    )

    assert response.status_code == 500


@pytest.mark.now('2021-04-01T00:00:00+0000')
async def test_routehistory_ordering(
        taxi_grocery_api,
        yamaps_local,
        persuggest,
        taxi_config,
        eats_core_integrations,
        routehistory,
):
    taxi_config.set_values(
        {'GROCERY_API_ADDRESS_DETAILS_SEARCH_DISTANCE': 85000},
    )

    uid = '80085'
    bound_uid = 'some_other_uid'
    location = [35.0, 53.0]
    place_id = 'ymapsbm1://some_uri'
    place_id_response = place_id
    persuggest_building_id = (
        'd9bca8d3481a06b760b838907b844210232246bf58ea9f31ee890feda38e53c1'
    )
    session = 'some-sess'
    old_comment = 'Its a trap!'
    new_comment = 'Never gonna give you up!'

    eats_core_integrations.set_data(uid=uid, bound_uid=bound_uid, addresses=[])

    routehistory.set_data(
        created_since='2021-03-01T00:00:00+0000',
        results=[
            {
                'order_id': 'order_id',
                'yandex_uid': uid,
                'created': '2021-03-02T00:00:00+0000',
                'position': [35.0, 53.0],
                'uri': place_id_response,
                'comment_courier': old_comment,
            },
            {
                'order_id': 'order_id',
                'yandex_uid': uid,
                'created': '2021-03-02T00:00:01+0000',
                'position': [35.0, 53.0],
                'uri': place_id_response,
                'comment_courier': new_comment,
            },
        ],
    )

    persuggest.set_data(persuggest_building_id, place_id_response)

    request_json = {'position': {'location': location, 'place_id': place_id}}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v2/get-address',
        json=request_json,
        headers={
            'X-YaTaxi-Session': session,
            'X-Yandex-UID': uid,
            'X-YaTaxi-Bound-Uids': uid + ',' + bound_uid,
            'X-Request-Language': 'en',
        },
    )

    assert response.status_code == 200

    assert routehistory.times_called == 1
    assert eats_core_integrations.times_called == 1
    assert persuggest.times_called == 2

    assert response.json()['comment'] == new_comment


@pytest.mark.now('2021-04-01T00:00:00+0000')
@pytest.mark.parametrize(
    'session,eats_location,taxi_location,other_uri',
    [
        pytest.param(
            'eats:eatssess',
            [35.0, 53.0],
            [35.1, 52.8],
            False,
            id='eats location closer, same uri with taxi',
        ),
        pytest.param(
            'eats:eatssess',
            [35.0, 53.0],
            [35.1, 52.8],
            True,
            id='eats location closer, other uri',
        ),
        pytest.param(
            'taxi:taxisess',
            [35.5, 53.7],
            [35.1, 52.8],
            True,
            id='taxi location closer',
        ),
        pytest.param(
            'eats:badsess',
            [33.5, 53.7],
            [33.1, 52.8],
            True,
            id='taxi location closer, but both outh of range',
        ),
        pytest.param(
            'taxi:somesess', None, [35.0, 53.0], True, id='no eats location',
        ),
        pytest.param(
            'eats:somesess', [35.0, 53.0], None, True, id='no taxi location',
        ),
        pytest.param('eats:badsess', None, None, True, id='no good response'),
    ],
)
async def test_basic_v1(
        taxi_grocery_api,
        yamaps_local,
        load_json,
        taxi_config,
        eats_core_integrations,
        routehistory,
        session,
        eats_location,
        taxi_location,
        other_uri,
        now,
):

    taxi_config.set_values(
        {
            'GROCERY_API_ADDRESS_SEARCH_BY_COUNTRY': {
                '__default__': {'search_radius': 25},
                'RU': {'search_radius': 85000},
            },
        },
    )

    uid = '80085'
    bound_uid = 'some_other_uid'
    location = [35.0, 53.0]
    place_id = 'ymapsbm1://some_uri'
    place_id_response = place_id
    if other_uri:
        place_id_response = place_id_response + '_other'
    eats_comment = 'Its a trap!'
    taxi_comment = 'Never gonna give you up!'

    eats_core_integrations.set_data(
        uid=uid,
        bound_uid=bound_uid,
        addresses=[
            {
                'location': eats_location,
                'comment': eats_comment,
                'floor': '11',
            },
        ],
    )

    routehistory.set_data(
        created_since='2021-03-01T00:00:00+0000',
        results=[
            {
                'order_id': 'order_id',
                'yandex_uid': uid,
                'created': '2021-03-02T00:00:00+0000',
                'position': taxi_location,
                'uri': place_id_response,
                'comment_courier': taxi_comment,
            },
        ],
    )

    request_json = {'location': location, 'place_id': place_id}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/get-address',
        json=request_json,
        headers={
            'X-YaTaxi-Session': session,
            'X-Yandex-UID': uid,
            'X-YaTaxi-Bound-Uids': uid + ',' + bound_uid,
            'X-Request-Language': 'en',
        },
    )

    assert response.status_code == 200

    if session.startswith('eats:bad'):
        geocoder_address = load_json('geocoder-response.json')['geocoder'][
            'address'
        ]
        assert response.json() == {
            'location': [0.0, 0.0],
            'place_id': '',
            'city': geocoder_address['locality'],
            'house': geocoder_address['house'],
            'street': geocoder_address['street'],
        }
    elif session.startswith('eats:'):
        if not other_uri:
            assert response.json()['location'] == taxi_location
            assert response.json()['comment'] == taxi_comment
            assert response.json()['address_source'] == 'routehistory'
        else:
            assert response.json()['location'] == eats_location
            assert response.json()['comment'] == eats_comment
            assert response.json()['address_source'] == 'eats'
        assert eats_core_integrations.times_called == 1
    else:  # taxi
        assert response.json()['location'] == taxi_location
        assert response.json()['place_id'] == place_id_response
        assert response.json()['comment'] == taxi_comment
        assert response.json()['address_source'] == 'routehistory'
        geocoder_address = load_json('geocoder-response.json')['geocoder'][
            'address'
        ]
        assert response.json()['street'] == geocoder_address['street']
        assert yamaps_local.times_called() == 4
        assert routehistory.times_called == 1


@pytest.mark.now('2021-04-01T00:00:00+0000')
async def test_routehistory_ordering_v1(
        taxi_grocery_api, taxi_config, eats_core_integrations, routehistory,
):

    taxi_config.set_values(
        {'GROCERY_API_ADDRESS_DETAILS_SEARCH_DISTANCE': 85000},
    )

    uid = '80085'
    bound_uid = 'some_other_uid'
    location = [35.0, 53.0]
    place_id = 'ymapsbm1://some_uri'
    place_id_response = place_id
    session = 'some-sess'
    old_comment = 'Its a trap!'
    new_comment = 'Never gonna give you up!'

    eats_core_integrations.set_data(uid=uid, bound_uid=bound_uid, addresses=[])

    routehistory.set_data(
        created_since='2021-03-01T00:00:00+0000',
        results=[
            {
                'order_id': 'order_id',
                'yandex_uid': uid,
                'created': '2021-03-02T00:00:00+0000',
                'position': [35.0, 53.0],
                'uri': place_id_response,
                'comment_courier': old_comment,
            },
            {
                'order_id': 'order_id',
                'yandex_uid': uid,
                'created': '2021-03-02T00:00:01+0000',
                'position': [35.0, 53.0],
                'uri': place_id_response,
                'comment_courier': new_comment,
            },
        ],
    )

    request_json = {'location': location, 'place_id': place_id}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/get-address',
        json=request_json,
        headers={
            'X-YaTaxi-Session': session,
            'X-Yandex-UID': uid,
            'X-YaTaxi-Bound-Uids': uid + ',' + bound_uid,
            'X-Request-Language': 'en',
        },
    )

    assert response.status_code == 200

    assert routehistory.times_called == 1
    assert eats_core_integrations.times_called == 1

    assert response.json()['comment'] == new_comment


@GROCERY_API_DEFAULT_DEPOT_LOCATION
@pytest.mark.parametrize(
    'region_id, expected_location',
    [
        pytest.param(None, MOSCOW_DEMO_LAVKA_LOCATION, id='Moscow'),
        pytest.param(10393, LONDON_LOCATION, id='London'),
    ],
)
async def test_region_id(
        taxi_grocery_api, persuggest, region_id, expected_location,
):
    persuggest.set_data(
        building_id='some_persuggest_building_id',
        place_id='ymapsbm1://some_uri',
        country='Russian Federation',
        country_code='RU',
        postal_code='123112',
        house='141',
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v2/get-address',
        json={'region_id': region_id},
        headers={'X-Request-Language': 'en'},
    )

    assert response.status_code == 200
    assert response.json()['location'] == expected_location


@pytest.mark.now('2021-04-01T00:00:00+0000')
@pytest.mark.config(GROCERY_API_ADDRESS_SEARCH_LIMIT=ADDRESSES_LIMIT)
async def test_addresses_limit(
        taxi_grocery_api, routehistory, persuggest, eats_core_integrations,
):
    uid = '80085'
    bound_uid = 'some_other_uid'
    session = 'some-sess'

    routehistory.set_data(
        created_since='2021-03-01T00:00:00+0000',
        results=[],
        max_results=ADDRESSES_LIMIT,
    )

    eats_core_integrations.set_data(uid=uid, bound_uid=bound_uid, addresses=[])

    persuggest.set_data(
        building_id='some_persuggest_building_id',
        place_id='ymapsbm1://some_uri',
        country='Russian Federation',
        country_code='RU',
        postal_code='123112',
        house='141',
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v2/get-address',
        json={},
        headers={
            'X-YaTaxi-Session': session,
            'X-Yandex-UID': uid,
            'X-YaTaxi-Bound-Uids': uid + ',' + bound_uid,
            'X-Request-Language': 'en',
        },
    )

    assert response.status_code == 200


@pytest.mark.now('2021-04-01T00:00:00+0000')
async def test_uri_change(
        taxi_grocery_api,
        yamaps_local,
        persuggest,
        taxi_config,
        eats_core_integrations,
        routehistory,
):
    taxi_config.set_values(
        {'GROCERY_API_ADDRESS_DETAILS_SEARCH_DISTANCE': 85000},
    )

    uid = '80085'
    bound_uid = 'some_other_uid'
    location = [35.0, 53.0]
    place_id = 'ymapsbm1://some_uri'
    persuggest_building_id = (
        'd9bca8d3481a06b760b838907b844210232246bf58ea9f31ee890feda38e53c1'
    )
    session = 'some-sess'

    eats_core_integrations.set_data(uid=uid, bound_uid=bound_uid, addresses=[])

    routehistory.set_data(
        created_since='2021-03-01T00:00:00+0000',
        results=[
            {
                'order_id': 'order_id',
                'yandex_uid': uid,
                'created': '2021-03-02T00:00:00+0000',
                'position': [35.0, 53.0],
                'uri': place_id,
                'comment_courier': 'comment',
            },
        ],
    )

    yamaps_place_id = 'yamaps_place_id'
    yamaps_local.set_data(place_id=yamaps_place_id)

    persuggest.set_data(persuggest_building_id, place_id)

    request_json = {'position': {'location': location, 'place_id': place_id}}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v2/get-address',
        json=request_json,
        headers={
            'X-YaTaxi-Session': session,
            'X-Yandex-UID': uid,
            'X-YaTaxi-Bound-Uids': uid + ',' + bound_uid,
            'X-Request-Language': 'en',
        },
    )

    assert response.status_code == 200

    assert routehistory.times_called == 1

    assert response.json()['place_id'] == yamaps_place_id
