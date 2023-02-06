import json

import pytest

TVM_TICKET = (
    '3:serv:CBAQ__________9_IgQIGRAT:UXM0pikXNjP5F-20d6WV_QyOeJMlAjJbaKNg'
    'fEmh98yar4tKXEqCLQF6maRzaAYFF8_SmGOHJ2S_7qtlFNrlY3rY9TnoQE5w-Ektcu43'
    'PS1lOFzp8Q3FXgHCPa53dVbyJjT6NglQDeCaP252Y4bhlF8iV_gHX_fpMWGhrnC8kU4'
)

DAP_HEADERS = {
    'X-Ya-Service-Ticket': TVM_TICKET,
    'X-YaTaxi-Park-Id': '1488',
    'X-YaTaxi-Driver-Profile-Id': 'driver',
    'X-Request-Application-Version': '8.99 (999)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'X-Request-Application': 'taximeter',
    'Accept-Language': 'ru',
    'User-Agent': 'Taximeter 8.99 (999)',
}


def test_check_session(
        taxi_driver_protocol, driver_authorizer_service, mockserver,
):
    @mockserver.json_handler('/driver-status/v1/internal/status')
    def mock_v1_status(request):
        return {}

    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post('driver/status/set')
    assert response.status_code == 401

    response = taxi_driver_protocol.post('driver/status/set?db=1488')
    assert response.status_code == 401

    response = taxi_driver_protocol.post(
        'driver/status/set?db=abc&session=qwerty',
    )
    assert response.status_code == 401

    response = taxi_driver_protocol.post(
        'driver/status/set?db=1488&session=qwerty',
    )
    assert response.status_code != 401


def test_bad_status(
        taxi_driver_protocol, driver_authorizer_service, mockserver,
):
    @mockserver.json_handler('/driver-status/v1/internal/status')
    def mock_v1_status(request):
        return {}

    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post(
        'driver/status/set?db=1488&session=qwerty', 'status=blabla',
    )
    assert response.status_code == 400


@pytest.mark.now('2018-04-01T00:00:00Z')
def test_full(
        taxi_driver_protocol,
        redis_store,
        driver_authorizer_service,
        tvm2_client,
        mockserver,
):
    @mockserver.json_handler('/driver-status/v1/internal/status')
    def mock_v1_status(request):
        return {}

    # Now we make offline driver free
    tvm2_client.set_ticket(json.dumps({'19': {'ticket': 'ticket'}}))
    response = taxi_driver_protocol.post(
        'driver/status/set?',
        'status=2&order=111&comment=Free',
        headers=DAP_HEADERS,
    )
    assert response.status_code == 200

    # Now we give yandex order to driver but he still can take orders
    redis_store.hset('Order:SetCar:Items:Providers:1488', '111', '2')

    response = taxi_driver_protocol.post(
        'driver/status/set',
        'status=2&order=111&comment=OnOrderFree',
        headers=DAP_HEADERS,
    )
    assert response.status_code == 200

    # Now we make driver busy and on order
    response = taxi_driver_protocol.post(
        'driver/status/set', 'status=1&order=111', headers=DAP_HEADERS,
    )
    assert response.status_code == 200

    # Now we close order and make driver busy
    redis_store.hdel('Order:SetCar:Items:Providers:1488', '111')

    response = taxi_driver_protocol.post(
        'driver/status/set', 'status=1&order=111', headers=DAP_HEADERS,
    )
    assert response.status_code == 200


@pytest.mark.now('2018-04-01T00:00:00Z')
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'communications', 'dst': 'driver_protocol'}],
)
def test_send_to_driver_status(
        taxi_driver_protocol,
        redis_store,
        driver_authorizer_service,
        mockserver,
):
    @mockserver.json_handler('/driver-status/v1/internal/status')
    def mock_v1_status(request):
        request_json = json.loads(request.get_data())
        assert request_json == {
            'park_id': '1488',
            'driver_id': 'driver',
            'status': 'busy',
            'order_id': '111',
            'order_provider': 0,
            'comment': 'Busy',
        }
        return {}

    response = taxi_driver_protocol.post(
        'driver/status/set',
        'status=1&order=111&comment=Busy',
        headers=DAP_HEADERS,
    )
    assert response.status_code == 200
    assert mock_v1_status.times_called == 1
