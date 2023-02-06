from typing import Optional

import pytest


TRANSLATIONS = {
    'client_messages': {
        'orderhistory.ride_report.order_not_found': {'en': 'Order not found'},
        'orderhistory.ride_report.email_not_found': {
            'en': 'No verified user email found',
        },
        'orderhistory.ride_report.sent': {
            'en': 'Ride report sent to verified email',
        },
    },
}


async def _request_send_report(
        taxi_orderhistory_web,
        order_id: str,
        service: Optional[str] = None,
        send_personal_email_id: bool = True,
):
    headers = {
        'X-Yandex-UID': 'uid0',
        # 'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
        'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
        'X-Request-Language': 'ru',
    }
    request = {'order_id': order_id}
    if service is not None:
        request['service'] = service
    if send_personal_email_id:
        headers['X-YaTaxi-User'] = 'personal_email_id=foobar'
    else:
        headers['X-YaTaxi-User'] = ''
    return await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/send-report', headers=headers, json=request,
    )


@pytest.mark.translations(**TRANSLATIONS)
async def test_happy_path(taxi_orderhistory_web, mockserver, load_json, stq):
    @mockserver.json_handler('/ridehistory/v2/item')
    def _mock_ridehistory(request):
        return mockserver.make_response(
            status=200, json=load_json('ridehistory_resp_simple.json'),
        )

    response = await _request_send_report(taxi_orderhistory_web, order_id='1')
    assert response.status == 200
    assert await response.json() == {
        'message': 'Ride report sent to verified email',
    }
    assert stq.send_ride_report_mail.times_called == 1
    stq_call_kwargs = stq.send_ride_report_mail.next_call()['kwargs']
    assert stq_call_kwargs == {
        'order_id': '1',
        'personal_email_id': 'foobar',
        'force_send': True,
    }


@pytest.mark.translations(**TRANSLATIONS)
async def test_email_not_found(taxi_orderhistory_web, stq):
    response = await _request_send_report(
        taxi_orderhistory_web, order_id='1', send_personal_email_id=False,
    )
    assert response.status == 404
    assert await response.json() == {
        'code': 'EMAIL_NOT_FOUND',
        'message': 'No verified user email found',
    }
    assert stq.send_ride_report_mail.times_called == 0


@pytest.mark.translations(**TRANSLATIONS)
async def test_order_not_found(
        taxi_orderhistory_web, mockserver, load_json, stq,
):
    @mockserver.json_handler('/ridehistory/v2/item')
    def _mock_ridehistory(request):
        return mockserver.make_response(
            status=404, json=load_json('ridehistory_resp_not_found.json'),
        )

    response = await _request_send_report(taxi_orderhistory_web, order_id='1')
    assert response.status == 404
    assert await response.json() == {
        'code': 'ORDER_NOT_FOUND',
        'message': 'Order not found',
    }
    assert stq.send_ride_report_mail.times_called == 0


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.parametrize(
    ['service', 'expected_status_code'],
    [
        pytest.param(None, 200, id='taxi_as_default_service'),
        pytest.param('taxi', 200, id='allowed_service'),
        pytest.param('drive', 500, id='restricted_service'),
        pytest.param('unknown', 400, id='nonexistent_service'),
    ],
)
async def test_services(
        taxi_orderhistory_web,
        mockserver,
        load_json,
        service: Optional[str],
        expected_status_code: int,
):
    @mockserver.json_handler('/ridehistory/v2/item')
    def _mock_ridehistory(request):
        return mockserver.make_response(
            status=200, json=load_json('ridehistory_resp_simple.json'),
        )

    response = await _request_send_report(
        taxi_orderhistory_web, order_id='1', service=service,
    )
    assert response.status == expected_status_code
