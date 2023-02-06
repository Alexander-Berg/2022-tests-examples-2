import pytest


@pytest.fixture(autouse=True)
def user_api_service_autouse(config):
    config.set_values(
        dict(
            USER_API_USE_USER_PHONES_CREATION=True,
            USER_API_USE_USER_PHONES_BULK_CREATION=True,
            USER_API_USE_USER_PHONES_SAVE_LAST_PAYMENT_METHOD=True,
            USER_API_CLIENT_USER_PHONES_TIMEOUT_MS=2000,
        ),
    )


def test_order_draft(taxi_protocol, load_json, mockserver, mock_user_api):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def mock_pickup_zones(request):
        return {}

    @mockserver.json_handler('/user-api/user_phones/save_last_payment_method')
    def mock_user_api_save_last_payment(request):
        assert mock_user_api.user_phones_times_called == 1
        json = request.json
        del json['phone_id']
        assert request.json == {'payment_method_type': 'cash'}
        return {}

    request = load_json('basic_request.json')
    draft_response = taxi_protocol.post('3.0/orderdraft', request)
    assert draft_response.status_code == 200
    assert mock_user_api_save_last_payment.times_called == 1
