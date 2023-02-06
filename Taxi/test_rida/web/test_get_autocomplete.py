from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pytest

from rida import consts
from test_rida import experiments_utils
from test_rida import helpers
from test_rida import maps_utils


def _build_predictions_response(predictions: List[Dict[str, str]]):
    return [
        {'place_id': prediction['place_id'], 'name': prediction['description']}
        for prediction in predictions
    ]


GOOGLE_PREDICTIONS_RESPONSE = [
    {'place_id': 'xxxx', 'description': 'Main'},
    {'place_id': 'yyyy', 'description': 'Minor'},
]
SERVICE_PREDICTION_RESPONSE = _build_predictions_response(
    GOOGLE_PREDICTIONS_RESPONSE,
)


@pytest.mark.parametrize(
    ['request_body_as_query'],
    [
        pytest.param(False, id='request_body_as_json'),
        pytest.param(True, id='request_body_as_query'),
    ],
)
async def test_get_autocomplete(
        web_app_client, mockserver, request_body_as_query,
):
    payload = {
        'country_code': 'NG',
        'input': 'M',
        'lat': 0.1231,
        'lng': 123.12313123,
    }
    headers = helpers.get_auth_headers(1234)
    if request_body_as_query:
        request_params = {'data': payload}
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    else:
        request_params = {'json': payload}
        headers['Content-Type'] = 'application/json'
    request_params['headers'] = headers

    @mockserver.json_handler('/api-proxy-external-geo/google/suggest-geo')
    def _mock_google_maps(request):
        assert request.query == {
            'input': 'M',
            'language': 'en',
            'google_api_key': 'rida',
            'components': 'country:NG',
            'location': '0.1231000,123.1231312',
        }
        return mockserver.make_response(
            status=200,
            json=maps_utils.make_gmaps_suggest_response(
                predictions=GOOGLE_PREDICTIONS_RESPONSE,
            ),
        )

    response = await web_app_client.post(
        path='/v1/maps/getAutocomplete', **request_params,
    )
    data = await response.json()
    assert data == {'status': 'OK', 'data': SERVICE_PREDICTION_RESPONSE}


EMPTY_RESPONSE = {'status': 'OK', 'data': []}
INVALID_RESPONSE = {
    'status': 'INVALID_DATA',
    'errors': {'message': 'Can not get autocomplete!'},
}


@pytest.mark.parametrize(
    [
        'google_status_code',
        'google_response_status',
        'predictions',
        'expected_status',
        'expected_response',
    ],
    [
        pytest.param(
            200,
            consts.EXTERNAL_GEO_OK_STATUS,
            [],
            200,
            EMPTY_RESPONSE,
            id='empty_response',
        ),
        pytest.param(
            200,
            consts.EXTERNAL_GEO_ZERO_STATUS,
            [],
            200,
            EMPTY_RESPONSE,
            id='zero_response',
        ),
        pytest.param(
            200,
            'BILLING',
            [],
            500,
            INVALID_RESPONSE,
            id='unknown_google_status',
        ),
        pytest.param(
            500,
            consts.EXTERNAL_GEO_OK_STATUS,
            [],
            500,
            INVALID_RESPONSE,
            id='google_is_unavailable',
        ),
    ],
)
async def test_external_geo_error_handling(
        web_app_client,
        mockserver,
        google_status_code,
        google_response_status,
        predictions,
        expected_status,
        expected_response,
):
    @mockserver.json_handler('/api-proxy-external-geo/google/suggest-geo')
    def _mock_google_maps(request):
        assert request.query == {
            'input': 'M',
            'language': 'en',
            'google_api_key': 'rida',
            'components': 'country:NG',
        }
        return mockserver.make_response(
            status=google_status_code,
            json=maps_utils.make_gmaps_suggest_response(
                status=google_response_status, predictions=predictions,
            ),
        )

    response = await web_app_client.post(
        path='/v1/maps/getAutocomplete',
        headers=helpers.get_auth_headers(1234),
        json={'country_code': 'NG', 'input': 'M'},
    )
    data = await response.json()
    assert response.status == expected_status
    assert data == expected_response


async def test_unauth_user(web_app_client):
    response = await web_app_client.post(
        path='/v1/maps/getAutocomplete',
        json={'country_code': 'NG', 'input': 'M'},
    )
    assert response.status == 401


@experiments_utils.get_geocoding_exp('persuggest', 'v1/maps/getAutocomplete')
@pytest.mark.parametrize(
    'input_lat, input_lon',
    [
        pytest.param(None, None, id='none latlon'),
        pytest.param(2.0, 3.0, id='usual latlon'),
        pytest.param(0, 0, id='zero latlon'),
    ],
)
@pytest.mark.parametrize(
    ['is_expected_subtitle'],
    [
        pytest.param(False),
        pytest.param(
            True, marks=pytest.mark.config(RIDA_PERSUGGEST_ADD_SUBTITLE=True),
        ),
    ],
)
@pytest.mark.config(
    RIDA_COUNTRY_COORDINATES_FOR_AUTOCOMPLETE={'ng': {'lat': 2.0, 'lon': 3.0}},
)
async def test_get_autocomplete_from_persuggest(
        web_app_client,
        mockserver,
        input_lat: Optional[float],
        input_lon: Optional[float],
        is_expected_subtitle: bool,
):
    lat = 2.0
    lon = 3.0

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    def _mock_persuggest(request):
        json = request.json
        assert json == {
            'action': 'user_input',
            'state': {
                'accuracy': 0,
                'has_special_requirements': False,
                'location': [lon, lat],
            },
            'type': 'b',
            'part': 'Отель',
        }
        return mockserver.make_response(
            status=200,
            json={
                'results': [
                    helpers.create_persuggest_element(
                        lat + 1, lon, title='First result', log='log1',
                    ),
                    helpers.create_persuggest_element(
                        lat, lon + 1, title='Second result', log='log2',
                    ),
                ],
                'suggest_reqid': '',
                'part': 'Отель',
            },
        )

    request: dict = {'country_code': 'ng', 'input': 'Отель'}
    if input_lat is not None and input_lon is not None:
        request.update({'lat': input_lat, 'lng': input_lon})
    response = await web_app_client.post(
        path='/v1/maps/getAutocomplete',
        json=request,
        headers=helpers.get_auth_headers(1234),
    )
    data = await response.json()
    first_name = 'First result'
    second_name = 'Second result'
    if is_expected_subtitle:
        first_name = ', '.join([first_name, 'subtitle'])
        second_name = ', '.join([second_name, 'subtitle'])
    assert data == {
        'status': 'OK',
        'data': [
            {'name': first_name, 'place_id': f'{lat + 1}|{lon}|log1'},
            {'name': second_name, 'place_id': f'{lat}|{lon + 1}|log2'},
        ],
    }


@experiments_utils.get_geocoding_exp('persuggest', 'v1/maps/getAutocomplete')
@pytest.mark.parametrize(
    ['latlng', 'expected_results_count'],
    [
        pytest.param(None, 3, id='no_filtering'),
        pytest.param(
            None,
            2,
            marks=pytest.mark.config(
                RIDA_PERSUGGEST_AUTOCOMPLETE_FILTERS={
                    'is_position_required': True,
                },
            ),
            id='is_position_required',
        ),
        pytest.param(
            (2.0, 3.0),
            2,
            marks=pytest.mark.config(
                RIDA_PERSUGGEST_AUTOCOMPLETE_FILTERS={
                    'is_position_required': False,
                    'max_distance': 1000,
                },
            ),
            id='max_distance',
        ),
        pytest.param(
            None,
            2,
            marks=pytest.mark.config(
                RIDA_PERSUGGEST_AUTOCOMPLETE_FILTERS={
                    'is_position_required': False,
                    'default_max_distance': 1000,
                },
                RIDA_COUNTRY_COORDINATES_FOR_AUTOCOMPLETE={
                    'ng': {'lat': 2.0, 'lon': 3.0},
                },
            ),
            id='default_max_distance',
        ),
    ],
)
async def test_persuggest_results_filtering(
        web_app_client,
        mockserver,
        latlng: Optional[Tuple[float, float]],
        expected_results_count: int,
):
    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    def _mock_persuggest(request):
        return mockserver.make_response(
            status=200,
            json={
                'results': [
                    helpers.create_persuggest_element(2.0, 3.0),
                    helpers.create_persuggest_element(1, 1),
                    helpers.create_persuggest_element(None, None),
                ],
                'suggest_reqid': '',
                'part': 'Отель',
            },
        )

    request: dict = {'country_code': 'ng', 'input': 'Отель'}
    if latlng is not None:
        request.update({'lat': str(latlng[0]), 'lng': str(latlng[1])})
    response = await web_app_client.post(
        path='/v1/maps/getAutocomplete',
        json=request,
        headers=helpers.get_auth_headers(1234),
    )
    assert response.status == 200
    result = await response.json()
    assert len(result['data']) == expected_results_count
