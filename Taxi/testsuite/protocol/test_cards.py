from user_api_switch_parametrize import PROTOCOL_SWITCH_TO_USER_API


@PROTOCOL_SWITCH_TO_USER_API
def test_cards_user_from_user_api(
        taxi_protocol, mockserver, user_api_switch_on,
):
    @mockserver.json_handler('/user-api/users/get')
    def mock_user_api_user_get(request):
        return {
            'id': 'ab1d0000000000000000000000000000',
            'phone_id': '558af6684794b3f8d9cb8c30',
            'yandex_uid': '4003514353',
        }

    response = taxi_protocol.post(
        '3.0/cards', json={'id': 'ab1d0000000000000000000000000000'},
    )
    assert response.status_code == 200
    if user_api_switch_on:
        assert mock_user_api_user_get.times_called == 1
    else:
        assert mock_user_api_user_get.times_called == 0
