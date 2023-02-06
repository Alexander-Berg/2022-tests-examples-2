import pytest

CORP_CLIENT_ID = 'corporate_client_identifier_test'
EMPLOYEE_YANDEX_UID = 'owner_yandex_uid'
MOCK_NOW = '2021-10-08T07:04:55+00:00'


@pytest.mark.parametrize(
    'passport_code, expected_code', ((200, 200), (500, 500)),
)
@pytest.mark.now(MOCK_NOW)
async def test_func_enable_2fa_light(
        taxi_cargo_crm, mockserver, passport_code, expected_code,
):
    @mockserver.json_handler('/passport-card-verification/update_list')
    def _handler(request):
        assert request.json['items'] == [EMPLOYEE_YANDEX_UID]
        return mockserver.make_response(status=passport_code, json={})

    request = {
        'corp_client_id': CORP_CLIENT_ID,
        'yandex_uid': EMPLOYEE_YANDEX_UID,
    }

    response = await taxi_cargo_crm.post(
        '/functions/enable-2fa-light', json=request,
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {}

    request_to_mock = _handler.next_call()['request'].json
    assert request_to_mock == {
        'author': 'dipterix',
        'channel': 'auth',
        'sub_channel': 'login',
        'list_name': 'sms2fa_delivery_uids_list',
        'reason': f'sms2fa_delivery_uid, cci:{CORP_CLIENT_ID}',
        'items': [EMPLOYEE_YANDEX_UID],
        'from': 1633676695000,
        'to': 1949036695000,
    }
