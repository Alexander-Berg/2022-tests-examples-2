from urllib import parse

import pytest


AUTH_PARAMS = {'db': 'db_id1', 'session': 'session1'}
HEADERS = {'User-Agent': 'Taximeter 8.80 (562)', 'Accept-Language': 'ru'}
HEADERS_V2 = {
    'User-Agent': 'Taximeter 8.80 (562)',
    'Accept-Language': 'ru',
    'X-YaTaxi-Park-Id': 'db_id1',
    'X-YaTaxi-Driver-Profile-Id': 'uuid1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.77 (456)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


@pytest.mark.config(
    DRIVER_BANNERS_URL_OVERRIDE=[
        {
            'banner_id': 'id_1',
            'url': 'redirected_url',
            'params': [
                {'id': 'park_id', 'required': True, 'arg_name': 'db_id'},
                {
                    'id': 'driver_profile_id',
                    'required': True,
                    'arg_name': 'uuid',
                },
                {
                    'id': 'first_name',
                    'required': True,
                    'arg_name': 'first_name',
                },
                {'id': 'last_name', 'required': True, 'arg_name': 'last_name'},
                {
                    'id': 'middle_name',
                    'required': True,
                    'arg_name': 'middle_name',
                },
                {'id': 'phone', 'required': True, 'arg_name': 'phone'},
                {
                    'id': 'driver_license',
                    'required': True,
                    'arg_name': 'driver_license',
                },
                {
                    'id': 'unique_driver_id',
                    'required': False,
                    'arg_name': 'unique_driver_id',
                },
                {'id': 'clid', 'required': False, 'arg_name': 'clid'},
            ],
        },
    ],
)
async def test_banners_redirect(
        taxi_driver_profile_view,
        driver_authorizer,
        mockserver,
        parks_commute,
        unique_drivers_mocks,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        return {
            'profiles': [
                {
                    'data': {
                        'license': {'pd_id': 'license_pd_id1'},
                        'full_name': {
                            'first_name': 'Иван',
                            'last_name': 'Иванов',
                            'middle_name': 'Иванович',
                        },
                        'phone_pd_ids': [{'pd_id': 'phone_pd_id1'}],
                    },
                    'park_driver_profile_id': 'db_id1_uuid1',
                },
            ],
        }

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_personal_phones(request):
        assert request.json == {'id': 'phone_pd_id1', 'primary_replica': False}
        return {'id': 'phone_pd_id', 'value': '+71234567890'}

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def _mock_personal_licenses(request):
        assert request.json == {
            'id': 'license_pd_id1',
            'primary_replica': False,
        }
        return {'id': 'phone_pd_id', 'value': 'LICENSE1'}

    parks_commute.set_clid_mapping({'db_id1': 'clid1'})
    unique_drivers_mocks.set_unique_driver_id(
        'db_id1', 'uuid1', 'unique_driver_id1',
    )

    driver_authorizer.set_session('db_id1', 'session1', 'uuid1')
    response = await taxi_driver_profile_view.get(
        '/driver/profile-view/v1/banners-redirect?id=id_1',
        params=AUTH_PARAMS,
        headers=HEADERS,
        allow_redirects=False,
    )
    assert response.status_code == 302
    response_url = parse.urlparse(parse.unquote(response.headers['location']))
    params_raw = response_url.query.split('&')
    params = dict()
    for param in params_raw:
        key, value = param.split('=')
        params[key] = value
    assert response_url.path == 'redirected_url'
    assert params == {
        'driver_license': 'LICENSE1',
        'phone': '+71234567890',
        'db_id': 'db_id1',
        'uuid': 'uuid1',
        'first_name': 'Иван',
        'middle_name': 'Иванович',
        'last_name': 'Иванов',
        'clid': 'clid1',
        'unique_driver_id': 'unique_driver_id1',
    }
    response = await taxi_driver_profile_view.get(
        '/driver/v1/profile-view/v2/banners-redirect?id=id_1',
        headers=HEADERS_V2,
        allow_redirects=False,
    )
    assert response.status_code == 302
    response_url = parse.urlparse(parse.unquote(response.headers['location']))
    params_raw = response_url.query.split('&')
    params = dict()
    for param in params_raw:
        key, value = param.split('=')
        params[key] = value
    assert response_url.path == 'redirected_url'
    assert params == {
        'driver_license': 'LICENSE1',
        'phone': '+71234567890',
        'db_id': 'db_id1',
        'uuid': 'uuid1',
        'first_name': 'Иван',
        'middle_name': 'Иванович',
        'last_name': 'Иванов',
        'clid': 'clid1',
        'unique_driver_id': 'unique_driver_id1',
    }


@pytest.mark.config(
    DRIVER_BANNERS_URL_OVERRIDE=[
        {
            'banner_id': 'id_1',
            'url': 'redirected_url',
            'params': [
                {'id': 'park_id', 'required': False, 'arg_name': 'db_id'},
                {
                    'id': 'driver_profile_id',
                    'required': False,
                    'arg_name': 'uuid',
                },
                {
                    'id': 'first_name',
                    'required': False,
                    'arg_name': 'first_name',
                },
                {
                    'id': 'last_name',
                    'required': False,
                    'arg_name': 'last_name',
                },
                {
                    'id': 'middle_name',
                    'required': False,
                    'arg_name': 'middle_name',
                },
                {'id': 'phone', 'required': False, 'arg_name': 'phone'},
                {
                    'id': 'driver_license',
                    'required': False,
                    'arg_name': 'driver_license',
                },
            ],
        },
    ],
)
async def test_banners_redirect_optional(
        taxi_driver_profile_view, driver_authorizer, mockserver,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        return {
            'profiles': [
                {'data': {}, 'park_driver_profile_id': 'db_id1_uuid1'},
            ],
        }

    driver_authorizer.set_session('db_id1', 'session1', 'uuid1')
    response = await taxi_driver_profile_view.get(
        '/driver/profile-view/v1/banners-redirect?id=id_1',
        params=AUTH_PARAMS,
        headers=HEADERS,
        allow_redirects=False,
    )
    assert response.status_code == 302
    assert (
        response.headers['location']
        == 'redirected_url?uuid=uuid1&db_id=db_id1'
    )
    response = await taxi_driver_profile_view.get(
        '/driver/v1/profile-view/v2/banners-redirect?id=id_1',
        headers=HEADERS_V2,
        allow_redirects=False,
    )
    assert response.status_code == 302
    assert (
        response.headers['location']
        == 'redirected_url?uuid=uuid1&db_id=db_id1'
    )


@pytest.mark.config(
    DRIVER_BANNERS_URL_OVERRIDE=[
        {
            'banner_id': 'id_1',
            'url': 'redirected_url',
            'params': [
                {
                    'id': 'first_name',
                    'required': False,
                    'arg_name': 'first_name',
                    'default': 'default_name',
                },
                {
                    'id': 'const',
                    'required': False,
                    'arg_name': 'key1',
                    'default': 'value1',
                },
            ],
        },
    ],
)
async def test_banners_redirect_default(
        taxi_driver_profile_view, driver_authorizer, mockserver,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        return {
            'profiles': [
                {'data': {}, 'park_driver_profile_id': 'db_id1_uuid1'},
            ],
        }

    driver_authorizer.set_session('db_id1', 'session1', 'uuid1')
    response = await taxi_driver_profile_view.get(
        '/driver/profile-view/v1/banners-redirect?id=id_1',
        params=AUTH_PARAMS,
        headers=HEADERS,
        allow_redirects=False,
    )
    assert response.status_code == 302
    assert (
        response.headers['location']
        == 'redirected_url?key1=value1&first_name=default_name'
    )
    response = await taxi_driver_profile_view.get(
        '/driver/v1/profile-view/v2/banners-redirect?id=id_1',
        headers=HEADERS_V2,
        allow_redirects=False,
    )
    assert response.status_code == 302
    assert (
        response.headers['location']
        == 'redirected_url?key1=value1&first_name=default_name'
    )
