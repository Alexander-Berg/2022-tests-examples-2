import pytest

# Constants and fixtures

DEFAULT_BODY = {
    'first_name': 'some_name',
    'last_name': 'some_last_name',
    'birth_date': '1990-01-01',
    'middle_name': ' ',
    'city': 'Москва',
}

REQUIRED_COURIER_CREATE_ARGS = [
    'park_id',
    'operation_id',
    'phone',
    'first_name',
    'last_name',
    'birth_date',
]

MOSCOW_PARKS = ['park_moscow_1', 'park_moscow_2']
ABAKAN_PARKS = ['park_abakan_1', 'park_abakan_2']
DEFAULT_PARKS = ['park_default_1', 'park_default_2']

DEFAULT_CONFIG = {
    'SELFREG_ON_FOOT_COURIER_PARKS_BY_CITY': {
        '__default__': {'parks': DEFAULT_PARKS},
        'Москва': {'parks': MOSCOW_PARKS},
        'Абакан': {'parks': ABAKAN_PARKS},
    },
    'SELFREG_COURIER_NEW_ENABLE_SAVE_INVITED_DRIVER': True,
}

CARGO_MISC_RESPONSES = {
    'fake_park_400': {
        'status': 400,
        'json': {'code': 'some_code', 'message': 'some_message'},
    },
    'fake_park_404': {'status': 404},
    'fake_park_500': {'status': 500},
}


def make_dict_response(x, response_dict, content_type, default_response):
    resp = response_dict.get(x, default_response)
    resp['content_type'] = content_type
    return resp


def response_cargo_misc(park_id):
    return make_dict_response(
        park_id,
        CARGO_MISC_RESPONSES,
        'application/json',
        {
            'status': 200,
            'json': {
                'park_id': park_id,
                'driver_id': 'new_courier',
                'car_id': 'some_car',
            },
        },
    )


# Tests


@pytest.mark.config(**DEFAULT_CONFIG)
@pytest.mark.parametrize(
    'token,fake_park,expect_code',
    [
        ('', None, 400),
        ('bad_token', None, 401),
        ('good_token', 'fake_park_400', 400),
        ('good_token', 'fake_park_404', 500),
        ('good_token', 'fake_park_500', 500),
        ('good_token', 'park_ok', 200),
    ],
)
async def test_courier_new_ok(
        mockserver,
        mock_cargo_misc,
        mock_client_notify,
        taxi_selfreg,
        token,
        fake_park,
        expect_code,
        mongo,
        mock_driver_referrals,
):
    data = DEFAULT_BODY

    @mock_client_notify('/v1/unsubscribe')
    async def _del_token(request):
        assert request.method == 'POST'
        assert request.json == {
            'client': {'client_id': 'selfreg-5a7581722016667706734a33'},
            'service': 'taximeter',
        }
        return {}

    @mock_driver_referrals('/service/save-invited-driver')
    def _handler_driver_referrals(request):
        assert request.json['park_id'] == 'park_ok'
        assert request.json['driver_id'] == 'new_courier'
        return mockserver.make_response(json={}, status=200)

    @mock_cargo_misc('/couriers/v1/create')
    def _handler_cargo_misc(request):
        body = request.json
        for arg in REQUIRED_COURIER_CREATE_ARGS:
            assert arg in body

        assert body['first_name'] == DEFAULT_BODY['first_name']
        assert body['last_name'] == DEFAULT_BODY['last_name']
        assert body['birth_date'] == DEFAULT_BODY['birth_date']
        assert body['hiring_source'] == 'selfreg'

        park_id = fake_park
        return mockserver.make_response(**response_cargo_misc(park_id))

    response = await taxi_selfreg.post(
        '/selfreg/courier/new',
        json=data,
        params={'token': token},
        headers={'Content-Type': 'application/json'},
    )
    assert response.status == expect_code
    after_profile = await mongo.selfreg_profiles.find_one({'token': token})

    if expect_code == 200:
        response_json = await response.json()
        assert response_json['park_id'] == fake_park
        assert response_json['driver_id'] == 'new_courier'
        assert after_profile['is_committed'] is True
        assert _handler_cargo_misc.times_called == 1
        assert _handler_driver_referrals.times_called == 1
        assert _del_token.times_called == 1
    elif token == 'good_token':
        assert _handler_cargo_misc.times_called >= 1
        assert _handler_driver_referrals.times_called == 0
        assert after_profile['is_committed'] is False
        assert _del_token.times_called == 0


async def test_courier_no_parks(taxi_selfreg):
    data = DEFAULT_BODY
    data['city'] = 'Москва'

    response = await taxi_selfreg.post(
        '/selfreg/courier/new',
        json=data,
        params={'token': 'good_token'},
        headers={'Content-Type': 'application/json'},
    )
    assert response.status == 500


@pytest.mark.config(**DEFAULT_CONFIG)
@pytest.mark.parametrize(
    'city,expect_parks',
    [
        ('Москва', MOSCOW_PARKS),
        ('Абакан', ABAKAN_PARKS),
        ('Мордор', DEFAULT_PARKS),
    ],
)
async def test_courier_park_selection(
        mockserver,
        mock_cargo_misc,
        mock_client_notify,
        taxi_selfreg,
        city,
        expect_parks,
        mock_driver_referrals,
):
    data = DEFAULT_BODY
    data['city'] = city

    @mock_client_notify('/v1/unsubscribe')
    async def _del_token(request):
        assert request.method == 'POST'
        assert request.json == {
            'client': {'client_id': 'selfreg-5a7581722016667706734a33'},
            'service': 'taximeter',
        }
        return {}

    @mock_driver_referrals('/service/save-invited-driver')
    def _handler_driver_referrals(request):
        assert request.json['park_id'] in expect_parks
        assert request.json['driver_id'] == 'new_courier'
        return mockserver.make_response(json={}, status=200)

    @mock_cargo_misc('/couriers/v1/create')
    def _handler(request):
        body = request.json
        park_id = body['park_id']
        assert park_id in expect_parks
        return mockserver.make_response(**response_cargo_misc(park_id))

    response = await taxi_selfreg.post(
        '/selfreg/courier/new',
        json=data,
        params={'token': 'good_token'},
        headers={'Content-Type': 'application/json'},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['park_id'] in expect_parks
    assert response_json['driver_id'] == 'new_courier'
    assert _handler_driver_referrals.times_called == 1
    assert _del_token.times_called == 1
