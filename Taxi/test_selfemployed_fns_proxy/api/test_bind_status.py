# pylint: disable=invalid-name,unused-variable
import pytest

# pylint: disable=invalid-name
pytestmark = pytest.mark.parametrize(
    'business_unit', ('taxi', 'test_business_unit'),
)


async def test_bind_status(
        mock_simple_fns_communication,
        mock_personal_service,
        taxi_selfemployed_fns_proxy,
        fns_messages,
        business_unit,
):
    test_inn = '000000000000'
    test_inn_pd_id = 'INN_PD_ID'
    test_request_id = 'request_id'
    test_msg_id = 'msg_id'
    test_bind_result = 'COMPLETED'

    mock_personal_service(pd_type='tins', raw=test_inn, pd_id=test_inn_pd_id)

    mock_simple_fns_communication(
        send_message_request=fns_messages.send_message_request(
            message_name='GetBindPartnerStatusRequest',
            message_content={'id': test_request_id},
        ),
        send_message_response=fns_messages.send_message_response(
            message_id=test_msg_id,
        ),
        get_message_request=fns_messages.get_message_request(
            message_id=test_msg_id,
        ),
        get_message_response=fns_messages.get_message_response(
            message_name='GetBindPartnerStatusResponse',
            message_content={'result': test_bind_result, 'inn': test_inn},
        ),
    )

    response = await taxi_selfemployed_fns_proxy.get(
        '/v1/bind/status',
        params={'business_unit': business_unit, 'request_id': test_request_id},
    )
    assert response.status == 200

    content = await response.json()

    assert content == {'result': test_bind_result, 'inn_pd_id': test_inn_pd_id}


@pytest.mark.parametrize(
    'code, message, status',
    (
        ('REQUEST_VALIDATION_ERROR', 'Test message', 400),
        ('TAXPAYER_UNREGISTERED', 'Test message', 409),
        ('TAXPAYER_UNBOUND', 'Test message', 409),
        ('PERMISSION_NOT_GRANTED', 'Test message', 409),
        ('INTERNAL_ERROR', 'Test message', 500),
    ),
)
async def test_bind_status_error(
        mock_simple_fns_communication,
        taxi_selfemployed_fns_proxy,
        fns_messages,
        business_unit,
        code,
        message,
        status,
):
    test_request_id = 'request_id'
    test_msg_id = 'msg_id'

    mock_simple_fns_communication(
        send_message_request=fns_messages.send_message_request(
            message_name='GetBindPartnerStatusRequest',
            message_content={'id': test_request_id},
        ),
        send_message_response=fns_messages.send_message_response(
            message_id=test_msg_id,
        ),
        get_message_request=fns_messages.get_message_request(
            message_id=test_msg_id,
        ),
        get_message_response=fns_messages.get_message_error_response(
            error_code=code, error_message=message,
        ),
    )

    response = await taxi_selfemployed_fns_proxy.get(
        '/v1/bind/status',
        params={'business_unit': business_unit, 'request_id': test_request_id},
    )
    assert response.status == status

    content = await response.json()

    assert content == {'code': code, 'message': message}


async def test_bind_status_fns_unavailable(
        mock_fns_unavailable,
        taxi_selfemployed_fns_proxy,
        fns_messages,
        business_unit,
):
    test_request_id = 'request_id'

    response = await taxi_selfemployed_fns_proxy.get(
        '/v1/bind/status',
        params={'business_unit': business_unit, 'request_id': test_request_id},
    )
    assert response.status == 503

    content = await response.json()

    assert content == {
        'code': 'FNS_UNAVAILABLE',
        'message': 'FNS is currently unavailable',
    }
