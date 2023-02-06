import json

import pytest

from . import auth
from . import utils


MOCK_URL = '/parks/texts'
ENDPOINT_URL = '/v1/parks/texts'
PARK_ID = 'texts_park'
OK_PARAMS = {'park_id': PARK_ID, 'text_type': 'terms'}


@pytest.fixture
def parks_texts(mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {'text': 'длинный текст'}

    return mock_callback


@pytest.mark.parametrize(
    'absent_header',
    [auth.USER_TICKET_HEADER, auth.USER_TICKET_PROVIDER_HEADER],
)
def test_absent_header(
        taxi_fleet_management_api, dispatcher_access_control, absent_header,
):
    headers = auth.HEADERS.copy()
    headers.pop(absent_header)
    response = taxi_fleet_management_api.get(
        ENDPOINT_URL, params=OK_PARAMS, headers=headers,
    )

    assert dispatcher_access_control.times_called == 0
    assert response.status_code == 401
    assert response.json() == utils.format_error(
        f'header {absent_header} must not be empty',
    )


@pytest.mark.parametrize(
    'bad_header', [auth.USER_TICKET_HEADER, auth.USER_TICKET_PROVIDER_HEADER],
)
def test_invalid_header(
        taxi_fleet_management_api, dispatcher_access_control, bad_header,
):
    headers = auth.HEADERS.copy()
    headers[bad_header] = 'trash'
    response = taxi_fleet_management_api.get(
        ENDPOINT_URL, params=OK_PARAMS, headers=headers,
    )

    assert dispatcher_access_control.times_called == 0
    assert response.status_code == 403
    assert response.json() == utils.format_error(
        f'failed to parse header {bad_header}',
    )


def test_yandex(
        taxi_fleet_management_api, dispatcher_access_control, parks_texts,
):
    response = taxi_fleet_management_api.get(
        ENDPOINT_URL, params=OK_PARAMS, headers=auth.HEADERS,
    )

    assert response.status_code == 200
    assert parks_texts.times_called == 1
    assert dispatcher_access_control.times_called == 1
    dac_request = dispatcher_access_control.next_call()['request'].get_data()
    assert json.loads(dac_request) == {'query': {'park': {'id': PARK_ID}}}


def test_yandex_team(
        taxi_fleet_management_api, dispatcher_access_control, parks_texts,
):
    response = taxi_fleet_management_api.get(
        ENDPOINT_URL,
        params=OK_PARAMS,
        headers={
            auth.USER_TICKET_PROVIDER_HEADER: 'yandex_team',
            auth.USER_TICKET_HEADER: '_!fake!_ya-team-1120000000083978',
        },
    )

    assert response.status_code == 200
    assert parks_texts.times_called == 1
    assert dispatcher_access_control.times_called == 0


def test_dac_forbidden(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(auth.DAC_MOCK_URL)
    def dac_mock_callback(request):
        response_json = {'code': str(403), 'message': 'forbidden'}
        return mockserver.make_response(json.dumps(response_json), 403)

    response = taxi_fleet_management_api.get(
        ENDPOINT_URL, params=OK_PARAMS, headers=auth.HEADERS,
    )

    assert response.status_code == 403
    assert response.json() == utils.format_error('access denied')
    assert dac_mock_callback.times_called == 1


def test_empty_grants(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(auth.DAC_MOCK_URL)
    def dac_mock_callback(request):
        return {'grants': []}

    response = taxi_fleet_management_api.get(
        ENDPOINT_URL, params=OK_PARAMS, headers=auth.HEADERS,
    )

    assert response.status_code == 403
    assert response.json() == utils.format_error('access denied')
    assert dac_mock_callback.times_called == 1


@pytest.mark.parametrize('dac_status', [400, 401, 404, 500, 503])
def test_internal_error(taxi_fleet_management_api, mockserver, dac_status):
    @mockserver.json_handler(auth.DAC_MOCK_URL)
    def dac_mock_callback(request):
        response_json = {'code': str(dac_status), 'message': 'msg'}
        return mockserver.make_response(json.dumps(response_json), dac_status)

    response = taxi_fleet_management_api.get(
        ENDPOINT_URL, params=OK_PARAMS, headers=auth.HEADERS,
    )

    assert response.status_code == 500
    assert response.json() == utils.INTERNAL_ERROR
    assert dac_mock_callback.times_called == 1


@pytest.mark.config(FLEET_API_INTERNAL_DISABLE_CHECK_GRANTS=True)
def test_disable_check(taxi_fleet_management_api, mockserver, parks_texts):
    @mockserver.json_handler(auth.DAC_MOCK_URL)
    def dac_mock_callback(request):
        return {'grants': []}

    response = taxi_fleet_management_api.get(
        ENDPOINT_URL, params=OK_PARAMS, headers=auth.HEADERS,
    )

    assert response.status_code == 200
    assert parks_texts.times_called == 1
    assert dac_mock_callback.times_called == 0
