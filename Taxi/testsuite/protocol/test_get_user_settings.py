import pytest

from user_api_switch_parametrize import PROTOCOL_SWITCH_TO_USER_API


URL = '3.0/get-user-settings'


@pytest.mark.parametrize(
    ['request_file', 'expected_status_code', 'expected_response'],
    [
        ('happy_path_request.json', 200, 'happy_path_response.json'),
        ('default_values_request.json', 200, 'default_values_response.json'),
        ('unauthorized_request.json', 401, 'unauthorized_response.json'),
        ('not_found_request.json', 404, 'not_found_response.json'),
    ],
)
@PROTOCOL_SWITCH_TO_USER_API
@pytest.mark.config(USER_SETTINGS_DEFAULT_TIPS=0)
def test_get_user_settings(
        taxi_protocol,
        load_json,
        request_file,
        expected_status_code,
        expected_response,
        mock_user_api,
        user_api_switch_on,
):
    request = load_json(request_file)
    response = taxi_protocol.post(URL, request)
    assert response.status_code == expected_status_code
    assert response.json() == load_json(expected_response)
    assert mock_user_api.users_get_times_called == int(user_api_switch_on)
