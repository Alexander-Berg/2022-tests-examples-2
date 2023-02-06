import pytest

DEFAULT_PARK_ID = 'db_id1'


def prepare_rq_selfreg(token, park_id=DEFAULT_PARK_ID):
    path = 'selfreg/v1/profile-view/v1/park'
    params = {'token': token, 'requested_park_id': park_id}
    headers = {'Accept-Language': 'ru', 'User-Agent': 'Taximeter 8.80 (562)'}
    return dict(path=path, params=params, headers=headers)


def prepare_rq_da(driver_authorizer, park_id):
    driver_authorizer.set_session(park_id, 'session1', 'uuid1')

    path = 'driver/profile-view/v1/park'
    params = {'park_id': park_id, 'requested_park_id': park_id}
    headers = {
        'User-Agent': 'Taximeter 8.80 (562)',
        'X-Driver-Session': 'session1',
        'Accept-Language': 'ru',
    }
    return dict(path=path, params=params, headers=headers)


def prepare_rq_da_proxy(park_id):
    path = 'driver/v1/profile-view/v1/park'
    params = {'requested_park_id': park_id}
    headers = {
        'Accept-Language': 'ru',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': 'uuid1',
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '8.80 (562)',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
    }
    return dict(path=path, params=params, headers=headers)


def prepare_rq(driver_authorizer, use_da_proxy, park_id=DEFAULT_PARK_ID):
    if use_da_proxy:
        return prepare_rq_da_proxy(park_id)
    return prepare_rq_da(driver_authorizer, park_id)


@pytest.fixture(autouse=True)
def park_contacts_request(mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/contacts')
    def _park_contacts(request):
        return {
            'drivers': {
                'phone': '88005553535',
                'address': 'test street',
                'email': 'test@email.com',
                'money_withdrawal': {'description': 'Где деньги, Лебовски?'},
                'schedule': 'С 10 до 6',
            },
        }


@pytest.fixture(autouse=True)
def parks_certifications_request(mockserver):
    @mockserver.json_handler(
        '/parks-certifications/v1/parks/certifications/list',
    )
    def _parks_certifications(request):
        return {
            'certifications': [{'park_id': 'db_id1', 'is_certified': True}],
        }


@pytest.fixture(autouse=True)
def fleet_offers_request(mockserver):
    @mockserver.json_handler(
        '/fleet-offers/internal/v1/fleet-offers/v1/not-signed/count',
    )
    def _not_signed_count(request):
        return {'count': 1}


# Tests


async def test_driver_park_profile_bad_user_agent(
        taxi_driver_profile_view, driver_authorizer,
):
    request_data = prepare_rq_da(driver_authorizer, DEFAULT_PARK_ID)
    request_data['headers']['User-Agent'] = 'Bad user agent'
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Bad user agent'}


@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': True,
            'money_withdrawal': True,
            'short_desc': True,
            'full_desc': True,
            'phone': True,
            'schedule': True,
            'email': True,
            'address': True,
        },
        'park': {},
        'country': {},
        'city': {},
    },
)
@pytest.mark.parametrize(
    'token,expect_code',
    [('', 400), ('token_bad', 401), ('token_500', 500), ('token_ok', 200)],
)
async def test_selfreg_park_profile(
        taxi_driver_profile_view,
        mock_fleet_parks_list,
        parks,
        mockserver,
        token,
        expect_code,
        load_json,
):
    @mockserver.json_handler('/selfreg/validate_token')
    def _validate_token(request):
        assert request.method == 'POST'
        token = request.json['token']
        if token == 'token_500':
            return mockserver.make_response(status=500)
        valid = bool(token == 'token_ok')
        return {'valid': valid}

    request_data = prepare_rq_selfreg(token)
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == expect_code
    if expect_code == 200:
        response_json = response.json()
        assert response_json == load_json('expected_response.json')


@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': True,
            'money_withdrawal': True,
            'short_desc': True,
            'full_desc': True,
            'phone': True,
            'schedule': True,
            'email': True,
            'address': True,
        },
        'park': {},
        'country': {},
        'city': {},
    },
)
@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_driver_park_profile(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    request_data = prepare_rq(driver_authorizer, use_da_proxy)
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == load_json('expected_response.json')


@pytest.mark.experiments3(
    is_config=True,
    name='fleet_offers_documents_menu_item',
    consumers=['driver_profile_view'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': True,
            'money_withdrawal': True,
            'short_desc': True,
            'full_desc': True,
            'phone': True,
            'schedule': True,
            'email': True,
            'address': True,
        },
        'park': {},
        'country': {},
        'city': {},
    },
)
@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_driver_park_profile_fleet_offers(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    request_data = prepare_rq(driver_authorizer, use_da_proxy)
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == (
        load_json('expected_response_fleet_offers.json')
        if use_da_proxy
        else load_json('expected_response.json')
    )


@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': False,
            'money_withdrawal': True,
            'short_desc': True,
            'full_desc': True,
            'phone': True,
            'schedule': True,
            'email': True,
            'address': True,
        },
        'park': {},
        'country': {},
        'city': {},
    },
)
@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_driver_park_profile_no_cert_elem(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    request_data = prepare_rq(driver_authorizer, use_da_proxy)
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    expected_response = load_json('expected_response.json')
    del expected_response['items'][1]
    assert response_json == expected_response


@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': True,
            'money_withdrawal': True,
            'short_desc': True,
            'full_desc': True,
            'phone': True,
            'schedule': True,
            'email': True,
            'address': True,
        },
        'park': {
            'db_id1': {
                'certification': False,
                'money_withdrawal': True,
                'short_desc': True,
                'full_desc': True,
                'phone': True,
                'schedule': True,
                'email': True,
                'address': True,
            },
        },
        'country': {},
        'city': {},
    },
)
@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_driver_park_profile_no_certification_for_park(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    request_data = prepare_rq(driver_authorizer, use_da_proxy)
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    expected_response = load_json('expected_response.json')
    del expected_response['items'][1]
    assert response_json == expected_response


@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': False,
            'money_withdrawal': True,
            'short_desc': True,
            'full_desc': True,
            'phone': True,
            'schedule': True,
            'email': True,
            'address': True,
        },
        'park': {
            'db_id1': {
                'certification': True,
                'money_withdrawal': True,
                'short_desc': True,
                'full_desc': True,
                'phone': True,
                'schedule': True,
                'email': True,
                'address': True,
            },
        },
        'country': {},
        'city': {},
    },
)
@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_driver_park_certification_enabled_for_park(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    request_data = prepare_rq(driver_authorizer, use_da_proxy)
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    expected_response = load_json('expected_response.json')
    assert response_json == expected_response


@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': True,
            'money_withdrawal': True,
            'short_desc': False,
            'full_desc': True,
            'phone': True,
            'schedule': True,
            'email': True,
            'address': True,
        },
        'park': {},
        'country': {},
        'city': {},
    },
)
@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_driver_park_profile_no_short_desc(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    request_data = prepare_rq(driver_authorizer, use_da_proxy)
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    expected_response = load_json('expected_response.json')
    del expected_response['items'][3]
    assert response_json == expected_response


@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': True,
            'money_withdrawal': True,
            'short_desc': True,
            'full_desc': False,
            'phone': True,
            'schedule': True,
            'email': True,
            'address': True,
        },
        'park': {},
        'country': {},
        'city': {},
    },
)
@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_driver_park_profile_no_full_desc(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    request_data = prepare_rq(driver_authorizer, use_da_proxy)
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    expected_response = load_json('expected_response.json')
    del expected_response['items'][4]
    assert response_json == expected_response


@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': True,
            'money_withdrawal': True,
            'short_desc': True,
            'full_desc': True,
            'phone': False,
            'schedule': True,
            'email': True,
            'address': True,
        },
        'park': {},
        'country': {},
        'city': {},
    },
)
@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_driver_park_profile_no_phone(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    request_data = prepare_rq(driver_authorizer, use_da_proxy)
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    expected_response = load_json('expected_response.json')
    del expected_response['items'][6]
    assert response_json == expected_response


@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': True,
            'money_withdrawal': True,
            'short_desc': True,
            'full_desc': True,
            'phone': True,
            'schedule': True,
            'email': True,
            'address': False,
        },
        'park': {},
        'country': {},
        'city': {},
    },
)
@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_driver_park_profile_no_address(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    request_data = prepare_rq(driver_authorizer, use_da_proxy)
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    expected_response = load_json('expected_response.json')
    del expected_response['items'][9]
    assert response_json == expected_response


@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': True,
            'money_withdrawal': True,
            'short_desc': True,
            'full_desc': True,
            'phone': True,
            'schedule': True,
            'email': False,
            'address': True,
        },
        'park': {},
        'country': {},
        'city': {},
    },
)
@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_driver_park_profile_no_email(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    request_data = prepare_rq(driver_authorizer, use_da_proxy)
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    expected_response = load_json('expected_response.json')
    del expected_response['items'][8]
    assert response_json == expected_response


@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': True,
            'money_withdrawal': False,
            'short_desc': True,
            'full_desc': True,
            'phone': True,
            'schedule': True,
            'email': True,
            'address': True,
        },
        'park': {},
        'country': {},
        'city': {},
    },
)
@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_driver_park_profile_no_money_withdrawal(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    request_data = prepare_rq(driver_authorizer, use_da_proxy)
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    expected_response = load_json('expected_response.json')
    del expected_response['items'][2]
    assert response_json == expected_response


@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': True,
            'money_withdrawal': True,
            'short_desc': True,
            'full_desc': True,
            'phone': True,
            'schedule': True,
            'email': True,
            'address': True,
        },
        'park': {},
        'country': {},
        'city': {},
    },
)
@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_driver_park_profile_no_phone_and_money_withdrawal_from_contacts(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/contacts')
    def _park_contacts(request):
        return {
            'drivers': {
                'email': 'test@email.com',
                'address': 'test street',
                'schedule': 'С 10 до 6',
            },
        }

    request_data = prepare_rq(driver_authorizer, use_da_proxy)
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    expected_response = load_json('expected_response.json')
    del expected_response['items'][2]
    del expected_response['items'][5]
    assert response_json == expected_response


@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': True,
            'money_withdrawal': True,
            'short_desc': True,
            'full_desc': True,
            'phone': True,
            'schedule': True,
            'email': True,
            'address': True,
        },
        'park': {},
        'country': {},
        'city': {},
    },
)
@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_driver_park_profile_no_contacts(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/contacts')
    def _park_contacts(request):
        return {}

    request_data = prepare_rq(driver_authorizer, use_da_proxy)
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    expected_response = load_json('expected_response_no_park_contacts.json')
    del expected_response['items'][2]
    assert response_json == expected_response


@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': True,
            'money_withdrawal': True,
            'short_desc': True,
            'full_desc': True,
            'phone': True,
            'schedule': True,
            'email': True,
            'address': True,
        },
        'park': {},
        'country': {},
        'city': {},
    },
)
@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_driver_park_not_found(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    request_data = prepare_rq(driver_authorizer, use_da_proxy, 'db_id2')
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'park_not_found',
        'message': 'Park not found',
    }


@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_individual_entrepreneur_park_profile(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    request_data = prepare_rq(driver_authorizer, use_da_proxy, 'db_id41')
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == load_json('expected_response_ie.json')


@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_self_employed_park_profile(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    request_data = prepare_rq(driver_authorizer, use_da_proxy, 'db_id42')
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == load_json('expected_response_se.json')


@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': True,
            'money_withdrawal': True,
            'short_desc': True,
            'full_desc': True,
            'phone': False,
            'schedule': False,
            'email': False,
            'address': False,
        },
        'park': {},
        'country': {},
        'city': {},
    },
)
@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_driver_park_profile_no_park_contacts(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    request_data = prepare_rq(driver_authorizer, use_da_proxy)
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == load_json(
        'expected_response_no_park_contacts.json',
    )


@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': True,
            'money_withdrawal': True,
            'short_desc': True,
            'full_desc': True,
            'phone': True,
            'schedule': True,
            'email': True,
            'address': True,
        },
        'park': {},
        'country': {},
        'city': {},
    },
)
@pytest.mark.parametrize('use_da_proxy', [True, False])
async def test_driver_park_profile_empty_desc(
        taxi_driver_profile_view,
        driver_authorizer,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
        parks,
        load_json,
):
    request_data = prepare_rq(driver_authorizer, use_da_proxy, 'db_id88')
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_no_desc.json')


@pytest.mark.parametrize('use_da_proxy', [True, False])
@pytest.mark.config(
    PARK_PROFILE_SHOW_SETTINGS={
        '__default__': {
            'certification': False,
            'money_withdrawal': False,
            'short_desc': False,
            'full_desc': False,
            'phone': False,
            'schedule': False,
            'email': False,
            'address': True,
        },
        'park': {},
        'country': {},
        'city': {},
    },
)
async def test_driver_park_profile_address_coordinates(
        taxi_driver_profile_view,
        driver_authorizer,
        mock_fleet_parks_list,
        mockserver,
        parks,
        use_da_proxy,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/contacts')
    def _park_contacts(request):
        return {
            'drivers': {
                'phone': '88005553535',
                'address': 'test street',
                'address_coordinates': {
                    'lon': '37.59929276',
                    'lat': '55.7518158',
                },
                'email': 'test@email.com',
                'money_withdrawal': {'description': 'Где деньги, Лебовски?'},
                'schedule': 'С 10 до 6',
            },
        }

    request_data = prepare_rq(driver_authorizer, use_da_proxy)
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    addres_item = response_json['items'][2]
    assert 'payload' in addres_item
    assert addres_item == {
        'type': 'detail',
        'reverse': True,
        'payload': {
            'type': 'navigate_geo_point',
            'geopoint': {'lon': 37.59929276, 'lat': 55.7518158},
        },
        'horizontal_divider_type': 'bottom_gap',
        'right_icon': 'navigate',
        'title': 'Адрес',
        'subtitle': 'test street',
    }


@pytest.mark.parametrize(
    'city_disabled,country_disabled,use_da_proxy',
    [
        (False, True, True),
        (True, False, True),
        (False, True, False),
        (True, False, False),
    ],
)
async def test_driver_park_profile_disabled_in_area(
        taxi_driver_profile_view,
        driver_authorizer,
        taxi_config,
        country_disabled,
        city_disabled,
        use_da_proxy,
        mock_fleet_parks_list,
        mockserver,
):

    display_all = {
        'certification': True,
        'money_withdrawal': True,
        'short_desc': True,
        'full_desc': True,
        'phone': True,
        'schedule': True,
        'email': True,
        'address': True,
    }
    disable_all = {k: False for k in display_all}
    taxi_config.set_values(
        dict(
            PARK_PROFILE_SHOW_SETTINGS={
                '__default__': display_all,
                'park': {},
                'country': {'rus': disable_all} if country_disabled else {},
                'city': {'Москва': disable_all} if city_disabled else {},
            },
        ),
    )
    request_data = prepare_rq(driver_authorizer, use_da_proxy)
    response = await taxi_driver_profile_view.get(**request_data)
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['items']) == 3
