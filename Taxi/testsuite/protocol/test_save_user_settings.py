import pytest

from user_api_switch_parametrize import PROTOCOL_SWITCH_TO_USER_API


URL = '3.0/save-user-settings'


@pytest.mark.parametrize(
    ['request_file', 'expected_status_code', 'expected_response'],
    [
        ('str_tips_request.json', 200, 'str_tips_response.json'),
        ('int_tips_request.json', 200, 'int_tips_response.json'),
        (
            'invalid_str_tips_request.json',
            400,
            'invalid_str_tips_response.json',
        ),
        ('not_found_request.json', 404, 'not_found_response.json'),
        ('unauthorized_request.json', 401, 'unauthorized_response.json'),
        ('outdated_request.json', 409, 'outdated_response.json'),
    ],
)
@PROTOCOL_SWITCH_TO_USER_API
def test_save_user_settings(
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
    assert mock_user_api.users_get_times_called == int(
        user_api_switch_on and (expected_status_code != 400),
    )
