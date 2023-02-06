import json

import pytest

from . import auth
from . import utils

ENDPOINT = '/v1/parks/orders/list'
MOCK_URL = '/driver_orders/v1/parks/orders/list'

OK_REQUEST = {
    'query': {
        'park': {
            'id': 'park_id',
            'order': {
                'booked_at': {
                    'from': '2019-05-01T00:00:00+03:00',
                    'to': '2019-06-01T00:00:00+03:00',
                },
            },
        },
    },
    'limit': 1,
}


BAD_REQUEST_PARAMS = [
    ('wrong', 'json root must be an object'),
    ({'query': {}}, 'query.park must be present'),
    ({'query': {'park': {}}}, 'query.park.id must be present'),
    (
        {'query': {'park': {'id': ''}}},
        'query.park.id must be a non-empty utf-8 string without BOM',
    ),
]


@pytest.mark.parametrize('payload, expected_response', BAD_REQUEST_PARAMS)
def test_bad_request(
        taxi_fleet_management_api, mockserver, payload, expected_response,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {}

    response = taxi_fleet_management_api.post(
        ENDPOINT, data=json.dumps(payload), headers=auth.HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json() == utils.format_error(expected_response)
    assert mock_callback.times_called == 0


def test_ok_request(taxi_fleet_management_api, mockserver):
    expected_response = {
        'id': 'order0',
        'short_id': 1,
        'status': 'complete',
        'created_at': '2019-05-01T10:00:00+00:00',
        'ended_at': '2019-05-01T10:20:00+00:00',
        'driver_profile': {'id': 'driver_id_0', 'name': 'driver_name_0'},
        'car': {
            'id': 'car_id_0',
            'brand_model': 'car_model_0',
            'license': {'number': 'car_number_0'},
            'callsign': 'callsign_0',
        },
        'booked_at': '2019-05-01T10:05:00+00:00',
        'provider': 'park',
        'address_from': {
            'address': 'Москва, Рядом с: улица Островитянова, 47',
            'lat': 55.6348324304,
            'lon': 37.541191945,
        },
        'route_points': [
            {
                'address': 'Россия, Химки, Нагорная улица',
                'lat': 55.123,
                'lon': 37.1,
            },
            {'address': 'Москва, Улица 1', 'lat': 55.5111, 'lon': 37.222},
            {
                'address': 'Москва, Гостиница Прибалтийская',
                'lat': 55.5545,
                'lon': 37.8989,
            },
        ],
        'cancelation_description': 'canceled',
        'mileage': '1500.0000',
        'type': {'id': 'request_type_0', 'name': 'request_type_name'},
        'category': 'vip',
        'amenities': ['animal_transport'],
        'payment_method': 'corp',
        'driver_work_rule': {
            'id': 'work_rule_id_1',
            'name': 'work_rule_name_1',
        },
        'price': '159.9991',
        'park_details': {
            'passenger': {
                'name': 'client_id_0',
                'phones': ['phone1', 'phone2', 'phone3'],
            },
            'company': {
                'id': 'company_id_0',
                'name': 'company_name_0',
                'slip': 'company_slip_0',
                'comment': 'company_comment_0',
            },
            'tariff': {'id': 'tariff_id_0', 'name': 'tariff_name_0'},
        },
        'events': [
            {'status': 'driving', 'event_at': '2019-05-01T10:10:00+00:00'},
            {'status': 'waiting', 'event_at': '2019-05-01T10:15:00+00:00'},
            {'status': 'calling', 'event_at': '2019-05-01T10:16:00+00:00'},
            {
                'status': 'transporting',
                'event_at': '2019-05-01T10:17:00+00:00',
            },
            {'status': 'complete', 'event_at': '2019-05-01T10:20:00+00:00'},
        ],
    }

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return expected_response

    response = taxi_fleet_management_api.post(
        ENDPOINT, data=json.dumps(OK_REQUEST), headers=auth.HEADERS,
    )

    assert response.status_code == 200, response.text
    assert response.json() == expected_response
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    assert json.loads(mock_request.get_data()) == OK_REQUEST


MOCK_ERROR_PARAMS = [
    (
        400,
        json.dumps({'code': '400', 'message': 'bad request'}),
        utils.format_error('bad request', '400'),
    ),
    (
        500,
        json.dumps({'code': '500', 'message': 'internal server error'}),
        utils.format_error('internal server error', 'internal_error'),
    ),
]


@pytest.mark.parametrize(
    'code, mock_response, expected_response', MOCK_ERROR_PARAMS,
)
def test_mock_error(
        taxi_fleet_management_api,
        mockserver,
        code,
        mock_response,
        expected_response,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return mockserver.make_response(mock_response, code)

    response = taxi_fleet_management_api.post(
        ENDPOINT, data=json.dumps(OK_REQUEST), headers=auth.HEADERS,
    )

    assert response.status_code == code, response.text
    assert response.json() == expected_response
    assert mock_callback.times_called == 1


def test_too_many_requests(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return mockserver.make_response('Limit exceeded.', 429)

    response = taxi_fleet_management_api.post(
        ENDPOINT, data=json.dumps(OK_REQUEST), headers=auth.HEADERS,
    )

    assert response.status_code == 429, response.text
    assert response.json() == utils.TOO_MANY_REQUESTS_ERROR
    assert mock_callback.times_called == 1
