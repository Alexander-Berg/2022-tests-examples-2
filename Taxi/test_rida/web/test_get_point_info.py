import datetime
from typing import Optional

import pytest

from test_rida import experiments_utils
from test_rida import helpers
from test_rida import maps_utils

_NOW = datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc)


_LAT = 9.137561
_LON = 7.380758699999999


def _build_point_response(
        address: str = 'Estate business center 5',
        lower_corner: str = '9.136230219708498,7.379406369708497',
        upper_corner: str = '9.138928180291503,7.382104330291502',
        is_expected_subtitle: bool = False,
):
    response = {
        'lowerCorner': lower_corner,
        'upperCorner': upper_corner,
        'zone_id': 3,
        'address': address,
        'lat': _LAT,
        'lng': _LON,
    }
    if is_expected_subtitle:
        response['address'] = ', '.join([address, 'subtitle'])
    return response


def _build_google_result(
        unexpected_field: str = None,
        plus_code: str = None,
        street_address: str = None,
        valid_address: str = None,
):
    address_components = [
        {
            'long_name': 'Abuja',
            'short_name': 'Abuja',
            'types': ['locality', 'political'],
        },
        {
            'long_name': 'Abuja Municipal Area Council',
            'short_name': 'AMAC',
            'types': ['administrative_area_level_2', 'political'],
        },
        {
            'long_name': 'Federal Capital Territory',
            'short_name': 'Federal Capital Territory',
            'types': ['administrative_area_level_1', 'political'],
        },
        {
            'long_name': 'Nigeria',
            'short_name': 'NG',
            'types': ['country', 'political'],
        },
        {
            'long_name': '901101',
            'short_name': '901101',
            'types': ['postal_code'],
        },
    ]

    geometry = {
        'bounds': {
            'northeast': {'lat': 9.1376621, 'lng': 7.380840699999999},
            'southwest': {'lat': 9.1374963, 'lng': 7.38067},
        },
        'location': {'lat': _LAT, 'lng': _LON},
        'location_type': 'ROOFTOP',
        'viewport': {
            'northeast': {'lat': 9.138928180291503, 'lng': 7.382104330291502},
            'southwest': {'lat': 9.136230219708498, 'lng': 7.379406369708497},
        },
    }

    types = ['premise', 'locality']
    address = ['901101', 'Abuja', 'Nigeria']
    if unexpected_field:
        address.insert(0, unexpected_field)
    if plus_code:
        address.insert(0, plus_code)
        address_components.append(
            {
                'long_name': plus_code,
                'short_name': plus_code,
                'types': ['plus_code'],
            },
        )

    if street_address:
        address.insert(0, street_address)
        types.append('street_address')
        address_components.append(
            {
                'long_name': street_address,
                'short_name': street_address,
                'types': ['street_address'],
            },
        )

    if valid_address:
        address.insert(0, valid_address)

    formatted_address = ', '.join(address)

    result = {
        'address_components': address_components,
        'geometry': geometry,
        'place_id': 'ChIJ47jDLxPfTRAR0NzH1J0HIqE',
        'types': types,
        'formatted_address': formatted_address,
    }
    return result


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    ['header', 'response_google', 'expected_result'],
    [
        pytest.param(
            helpers.get_auth_headers(1234),
            [_build_google_result(street_address='Estate business center 5')],
            _build_point_response(),
            id='authorized-used',
        ),
        pytest.param(
            {},
            [_build_google_result(street_address='Estate business center 5')],
            _build_point_response(),
            id='unauthorized-user',
        ),
        pytest.param(
            {},
            [_build_google_result(plus_code='49QJ+28R')],
            _build_point_response(address='Unnamed road'),
            id='undefined-exact-position',
        ),
        pytest.param(
            helpers.get_auth_headers(1234),
            [],
            {'lowerCorner': '0.0,0.0', 'upperCorner': '0.0,0.0', 'zone_id': 0},
            id='google-zero-results',
        ),
        pytest.param(
            {},
            [
                _build_google_result(
                    plus_code='49QJ+28R', unexpected_field='Wuse',
                ),
            ],
            _build_point_response(address='Wuse'),
            id='unexpected-field',
        ),
        pytest.param(
            {},
            [
                _build_google_result(valid_address='Estate business center 5'),
                _build_google_result(
                    valid_address='Estate business center 18',
                ),
                _build_google_result(valid_address='Estate business center'),
            ],
            _build_point_response(),
            id='no-street-address',
        ),
        pytest.param(
            {},
            [
                _build_google_result(
                    street_address='Estate business center 5',
                ),
                _build_google_result(
                    street_address='Estate business center 18',
                ),
                _build_google_result(street_address='Estate business center'),
            ],
            _build_point_response(),
            id='several-street-addresses',
        ),
        pytest.param(
            {},
            [
                _build_google_result(valid_address='Estate business center'),
                _build_google_result(
                    valid_address='Estate business center 18',
                ),
                _build_google_result(
                    street_address='Estate business center 5',
                ),
            ],
            _build_point_response(),
            id='street-and-valid-addresses',
        ),
    ],
)
@pytest.mark.parametrize(
    ['request_point_info', 'zone_id', 'country_id'],
    [
        pytest.param(
            {
                'handler': '/v1/maps/getPointInfo',
                'request_body': {'lat': f'{_LAT}', 'lng': f'{_LON}'},
            },
            3,
            None,
        ),
        pytest.param(
            {
                'handler': '/v1/maps/getPointInfoFromPlaceId',
                'request_body': {'place_id': 'ChIJ47jDLxPfTRAR0NzH1J0HIqE'},
            },
            0,
            'ng',
        ),
    ],
)
async def test_get_point_logic(
        web_app_client,
        mockserver,
        header,
        request_point_info,
        zone_id,
        response_google,
        expected_result,
        country_id: Optional[str],
):
    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/geocode/json',
    )
    def _mock_google_maps(request):
        return mockserver.make_response(
            status=200,
            json=maps_utils.make_gmaps_point_response(response_google),
        )

    if not response_google:
        expected_result['zone_id'] = zone_id
    if country_id is not None and response_google:
        expected_result['pointCountryCode'] = country_id

    response = await web_app_client.post(
        path=request_point_info['handler'],
        headers=header,
        json=request_point_info['request_body'],
    )

    data = await response.json()
    assert data['status'] == 'OK' and expected_result == data['data']


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    ['request_body_as_query'],
    [
        pytest.param(False, id='request_body_as_json'),
        pytest.param(True, id='request_body_as_query'),
    ],
)
@pytest.mark.parametrize(
    ['request_point_info'],
    [
        pytest.param(
            {
                'handler': '/v1/maps/getPointInfo',
                'request_body': {'lat': f'{_LAT}', 'lng': f'{_LON}'},
            },
        ),
        pytest.param(
            {
                'handler': '/v1/maps/getPointInfoFromPlaceId',
                'request_body': {'place_id': 'ChIJ47jDLxPfTRAR0NzH1J0HIqE'},
            },
        ),
    ],
)
async def test_get_point_format(
        web_app_client, mockserver, request_body_as_query, request_point_info,
):
    header = helpers.get_auth_headers(1234)

    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/geocode/json',
    )
    def _mock_google_maps(request):
        return mockserver.make_response(
            status=200,
            json=maps_utils.make_gmaps_point_response(
                results=[
                    _build_google_result(
                        street_address='Estate business center 5',
                    ),
                ],
            ),
        )

    if request_body_as_query:
        request_params = {'data': request_point_info['request_body']}
        header['Content-Type'] = 'application/x-www-form-urlencoded'
    else:
        request_params = {'json': request_point_info['request_body']}
        header['Content-Type'] = 'application/json'

    request_params['headers'] = header
    response = await web_app_client.post(
        request_point_info['handler'], **request_params,
    )
    data = await response.json()
    assert data['data']['lat'] == _LAT and data['data']['lng'] == _LON


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    ['error'],
    [
        pytest.param('network', id='network-error'),
        pytest.param('timeout', id='timeout-error'),
    ],
)
@pytest.mark.parametrize(
    ['request_point_info'],
    [
        pytest.param(
            {
                'handler': '/v1/maps/getPointInfo',
                'request_body': {'lat': f'{_LAT}', 'lng': f'{_LON}'},
            },
        ),
        pytest.param(
            {
                'handler': '/v1/maps/getPointInfoFromPlaceId',
                'request_body': {'place_id': 'ChIJ47jDLxPfTRAR0NzH1J0HIqE'},
            },
        ),
    ],
)
async def test_get_point_error(
        web_app_client, mockserver, error, request_point_info,
):
    header = helpers.get_auth_headers(1234)

    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/geocode/json',
    )
    def _mock_google_maps(request):
        if error == 'network':
            raise mockserver.NetworkError()
        elif error == 'timeout':
            raise mockserver.TimeoutError()

    response = await web_app_client.post(
        path=request_point_info['handler'],
        headers=header,
        json=request_point_info['request_body'],
    )
    data = await response.json()
    assert data['status'] == 'INVALID_DATA'
    assert response.status == 500


_PERSUGGEST_PINDROP_RESPONSE = {
    'results': [helpers.create_persuggest_element(_LAT, _LON)],
    'zones': {'nearest_zones': []},
    'points': [],
    'points_icon_image_tag': 'custom_pp_icon_black_test',
    'services': {'taxi': {'available': True}},
    'typed_experiments': {'version': 1149418, 'items': []},
}


@experiments_utils.get_geocoding_exp('persuggest', 'v1/maps/getPointInfo')
@pytest.mark.parametrize(
    ['is_expected_subtitle'],
    [
        pytest.param(False),
        pytest.param(
            True, marks=pytest.mark.config(RIDA_PERSUGGEST_ADD_SUBTITLE=True),
        ),
    ],
)
async def test_get_point_persuggest(
        web_app_client, mockserver, is_expected_subtitle: bool,
):
    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/finalsuggest')
    def _mock_persuggest(request):
        json = request.json
        assert json == {
            'action': 'pin_drop',
            'state': {'accuracy': 0, 'has_special_requirements': False},
            'position': [_LON, _LAT],
            'sticky': False,
        }
        return mockserver.make_response(
            status=200, json=_PERSUGGEST_PINDROP_RESPONSE,
        )

    response = await web_app_client.post(
        path='/v1/maps/getPointInfo',
        headers=helpers.get_auth_headers(1234),
        json={'lat': f'{_LAT}', 'lng': f'{_LON}', 'country_code': 'ng'},
    )

    data = await response.json()
    assert data['status'] == 'OK'
    expected = _build_point_response(
        lower_corner=f'{_LAT},{_LON}',
        upper_corner=f'{_LAT},{_LON}',
        is_expected_subtitle=is_expected_subtitle,
    )
    expected['pointCountryCode'] = 'ng'
    assert data['data'] == expected


@experiments_utils.get_geocoding_exp(
    'persuggest', 'v1/maps/getPointInfoFromPlaceId',
)
async def test_get_point_from_place_id_persuggest(web_app_client, mockserver):
    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/finalsuggest')
    def _mock_persuggest(request):
        json = request.json
        assert json == {
            'action': 'finalize',
            'state': {'accuracy': 0, 'has_special_requirements': False},
            'position': [_LON, _LAT],
            'sticky': False,
            'prev_log': 'super_place_id',
        }
        return mockserver.make_response(
            status=200, json=_PERSUGGEST_PINDROP_RESPONSE,
        )

    response = await web_app_client.post(
        path='/v1/maps/getPointInfoFromPlaceId',
        headers=helpers.get_auth_headers(1234),
        json={
            'place_id': f'{_LAT}|{_LON}|super_place_id',
            'country_code': 'ng',
        },
    )

    data = await response.json()
    assert data['status'] == 'OK'
    expected = _build_point_response(
        lower_corner=f'{_LAT},{_LON}', upper_corner=f'{_LAT},{_LON}',
    )
    expected['pointCountryCode'] = 'ng'
    assert data['data'] == expected
