import pytest

from . import auth
from . import utils

MOCK_URL = '/taximeter-xservice.taxi.yandex.net/fm-api/auth/accept_offer'
ENDPOINT_URL = '/v1/offer-accept'


@pytest.mark.parametrize(
    'park_id,response_code,response_json',
    [
        ('123', 200, {}),
        (None, 400, utils.format_error('parameter park_id must be set')),
    ],
)
def test_post(
        taxi_fleet_management_api,
        mockserver,
        park_id,
        response_code,
        response_json,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return {}

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL,
        headers=auth.HEADERS,
        params={'park_id': park_id} if park_id is not None else {},
    )

    assert response.status_code == response_code, response.text
    assert response.json() == response_json, response.text

    if response_code == 200:
        assert mock_callback.times_called == 1
        mock_request = mock_callback.next_call()['request']
        assert mock_request.method == 'POST'
        assert mock_request.args.get('park_id') == park_id
        assert mock_request.args.get('service_id') == auth.OPTEUM_SERVICE_ID
        auth.check_user_ticket_headers(mock_request.headers)
    else:
        assert mock_callback.times_called == 0
