import pytest

from taxi.clients import tvm

from test_passenger_profile import common


@pytest.mark.parametrize(
    ['application', 'expected_name', 'expected_rating'],
    [
        # Yandex.Taxi apps
        ['iphone', 'Алексей', '4.90'],
        ['android', 'Алексей', '4.90'],
        # Uber apps
        ['uber_android', 'Лёха', '4.10'],
        ['uber_iphone', 'Лёха', '4.10'],
    ],
)
@pytest.mark.config(
    APPLICATION_MAP_BRAND={
        'iphone': 'yataxi',
        'android': 'yataxi',
        'uber_android': 'yauber',
        'uber_iphone': 'yauber',
    },
)
@common.mark_passenger_profile_experiment(yandex_uid='10002')
async def test_get_profile(
        web_app_client, application, expected_name, expected_rating,
):
    # Passenger profiles should be separated by brand
    # (y.taxi, uber, yango, vezet, rutaxi)

    query = {'yandex_uid': '10002', 'application': application}
    response = await web_app_client.get(
        '/passenger-profile/v1/profile', params=query,
    )
    assert response.status == 200

    response_data = await response.json()
    assert response_data == {
        'first_name': expected_name,
        'rating': expected_rating,
    }


@pytest.mark.config(APPLICATION_MAP_BRAND={'__default__': None})
@common.mark_passenger_profile_experiment(yandex_uid='10002')
async def test_get_profile_invalid_application(web_app_client):
    query = {'yandex_uid': '10002', 'application': 'invalid application'}
    response = await web_app_client.get(
        '/passenger-profile/v1/profile', params=query,
    )
    assert response.status == 400

    response_data = await response.json()
    assert response_data == {
        'code': 'validation_error',
        'message': (
            'Unknown application. Check the APPLICATION_MAP_BRAND config'
        ),
    }


@pytest.mark.parametrize(
    'activate_experiment,success',
    [
        pytest.param(
            False,
            False,
            id='Test with no disabled services and no active experiments',
        ),
        pytest.param(
            True,
            True,
            id='Test with disabled service and an active experiment',
        ),
    ],
)
async def test_get_profile_active_experiment(
        web_app_client,
        mockserver,
        taxi_config,
        add_passenger_profile_experiment,
        patch,
        activate_experiment,
        success,
):
    if activate_experiment:
        add_passenger_profile_experiment(yandex_uid='10002')

    query = {'yandex_uid': '10002', 'application': 'iphone'}
    response = await web_app_client.get(
        '/passenger-profile/v1/profile', params=query,
    )

    response_data = await response.json()
    if success:
        assert response.status == 200
        assert response_data == {'first_name': 'Алексей', 'rating': '4.90'}
    else:
        assert response.status == 403
        assert response_data == {
            'code': 'access_denied',
            'message': (
                'Access to passenger profile'
                f' was not allowed by experiment'
                f' "passenger_profile"'
            ),
        }


def make_experiment_request(
        args, yandex_uid='10002', add_transformations=False,
):
    request_args = [
        {'name': 'uid', 'type': 'string', 'value': yandex_uid},
        {
            'name': 'src_service_name',
            'type': 'string',
            'value': 'test_service',
        },
    ] + args
    request = {'consumer': 'protocol/launch', 'args': request_args}
    if add_transformations:
        request['kwargs_transformations'] = [
            {
                'dst_kwarg': 'country_code',
                'preserve_src_kwargs': True,
                'src_kwargs': ['remote_ip'],
                'type': 'country_by_ip',
            },
        ]
    return request


@pytest.mark.config(APPLICATION_MAP_BRAND={'__default__': 'yataxi'})
async def test_get_profile_headers_to_experiment(
        web_app_client, mockserver, add_passenger_profile_experiment, patch,
):
    add_passenger_profile_experiment(
        yandex_uid='10002',
        src_service_name='test_service',
        phone_id='5e7a2d877984b5db628410a3',
        remote_ip='127.0.0.1',
        add_application_args=True,
    )

    @patch('taxi.clients.tvm.check_tvm')
    async def _check_tvm(*args, **kwargs):
        return tvm.CheckResult(src_service_name='test_service')

    query = {'yandex_uid': '10002', 'application': 'iphone'}
    headers = {
        'X-YaTaxi-PhoneId': '5e7a2d877984b5db628410a3',
        'X-Remote-IP': '127.0.0.1',
        'X-Request-Application': (
            'app_brand=yataxi,app_build=release,'
            'app_name=android,platform_ver1=9,'
            'app_ver1=3,app_ver2=152,app_ver3=0'
        ),
    }
    response = await web_app_client.get(
        '/passenger-profile/v1/profile', params=query, headers=headers,
    )
    assert response.status == 200


@pytest.mark.config(APPLICATION_MAP_BRAND={'__default__': 'yataxi'})
@common.mark_passenger_profile_experiment(yandex_uid='10002')
async def test_get_profile_default_brand(web_app_client):

    query = {'yandex_uid': '10002', 'application': 'android'}
    response = await web_app_client.get(
        '/passenger-profile/v1/profile', params=query,
    )
    assert response.status == 200

    response_data = await response.json()
    assert response_data == {'first_name': 'Алексей', 'rating': '4.90'}


@pytest.mark.config(PASSENGER_PROFILE_DEFAULT_RATING=4.87)
@common.mark_passenger_profile_experiment(yandex_uid='1000003')
async def test_get_profile_default_rating(web_app_client):
    # In case there is no profile yet for a given uid, we should
    # return the default value of rating,
    # set by the PASSENGER_PROFILE_DEFAULT_RATING config

    query = {
        'yandex_uid': '1000003',  # there is no such uid in the db
        'application': 'iphone',
    }
    response = await web_app_client.get(
        '/passenger-profile/v1/profile', params=query,
    )
    assert response.status == 200

    response_data = await response.json()
    assert response_data == {'rating': '4.87'}


@common.mark_passenger_profile_experiment(yandex_uid='1000005')
async def test_get_profile_empty_name(web_app_client):
    query = {'yandex_uid': '1000005', 'application': 'iphone'}
    response = await web_app_client.get(
        '/passenger-profile/v1/profile', params=query,
    )
    assert response.status == 200

    response_data = await response.json()
    assert response_data == {'rating': '4.90'}
