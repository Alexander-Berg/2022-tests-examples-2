# encoding=utf-8
import pytest

from . import auth

"""
We dont perform any checks in fleet api. We just pass through TAXIMETER_HEADERS
and pass X-Client-ID as service_id. So we test only this functionality here.
"""

MOCK_URL = '/taximeter-xservice.taxi.yandex.net/fm-api/auth/parks'
ENDPOINT_URL = '/v1/parks'

# just to check that PARKS are proxied as is
PARKS = [{'id': 'string', 'name': 'string'}]


@pytest.mark.parametrize('park_id', [None, 'test-park'])
def test_post_ok(
        taxi_fleet_management_api,
        mockserver,
        dispatcher_access_control,
        park_id,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return PARKS

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL,
        headers=auth.HEADERS,
        params={'park_id': park_id} if park_id is not None else {},
    )

    assert response.status_code == 200, response.text
    assert response.json() == PARKS

    assert dispatcher_access_control.times_called == 0
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    assert mock_request.args.get('park_id') == park_id
    assert mock_request.args.get('service_id') == auth.OPTEUM_SERVICE_ID
    auth.check_user_ticket_headers(mock_request.headers)
