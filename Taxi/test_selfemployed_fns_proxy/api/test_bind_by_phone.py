# pylint: disable=invalid-name,unused-variable
import pytest

# pylint: disable=invalid-name
pytestmark = pytest.mark.parametrize(
    'business_unit', ('taxi', 'test_business_unit'),
)


async def test_bind_by_phone(
        mock_simple_fns_communication,
        mock_personal_service,
        taxi_selfemployed_fns_proxy,
        fns_messages,
        business_unit,
):
    test_phone = '70000000000'
    test_phone_personal = f'+{test_phone}'
    test_phone_pd_id = 'PHONE_PD_ID'
    test_permissions = ['test_permission']
    test_request_id = 'request_id'
    test_msg_id = 'msg_id'

    mock_personal_service(
        pd_type='phones', raw=test_phone_personal, pd_id=test_phone_pd_id,
    )

    mock_simple_fns_communication(
        send_message_request=fns_messages.send_message_request(
            message_name='PostBindPartnerWithPhoneRequest',
            message_content={
                'phone': test_phone,
                'permissions': test_permissions,
            },
        ),
        send_message_response=fns_messages.send_message_response(
            message_id=test_msg_id,
        ),
        get_message_request=fns_messages.get_message_request(
            message_id=test_msg_id,
        ),
        get_message_response=fns_messages.get_message_response(
            message_name='PostBindPartnerWithPhoneResponse',
            message_content={'id': test_request_id},
        ),
    )

    response = await taxi_selfemployed_fns_proxy.post(
        '/v1/bind/phone',
        json={
            'phone_pd_id': test_phone_pd_id,
            'permissions': test_permissions,
        },
        params={'business_unit': business_unit},
    )
    assert response.status == 200

    content = await response.json()

    assert content == {'request_id': test_request_id}


@pytest.mark.parametrize(
    'code, message, status, args, details',
    (
        ('REQUEST_VALIDATION_ERROR', 'Test message', 400, None, None),
        ('TAXPAYER_UNREGISTERED', 'Test message', 409, None, None),
        ('TAXPAYER_UNBOUND', 'Test message', 409, None, None),
        ('PERMISSION_NOT_GRANTED', 'Test message', 409, None, None),
        (
            'TAXPAYER_ALREADY_BOUND',
            'Test message',
            409,
            {'inn': '000000000000'},
            {'inn_pd_id': 'INN_PD_ID'},
        ),
        ('INTERNAL_ERROR', 'Test message', 500, None, None),
    ),
)
async def test_bind_by_inn_error(
        mock_simple_fns_communication,
        mock_personal_service,
        taxi_selfemployed_fns_proxy,
        fns_messages,
        business_unit,
        code,
        message,
        status,
        args,
        details,
):
    test_inn = '000000000000'
    test_phone = '70000000000'
    test_phone_personal = f'+{test_phone}'
    test_inn_pd_id = 'INN_PD_ID'
    test_phone_pd_id = 'PHONE_PD_ID'
    test_permissions = ['test_permission']
    test_msg_id = 'msg_id'

    mock_personal_service(
        pd_type='phones', raw=test_phone_personal, pd_id=test_phone_pd_id,
    )
    mock_personal_service(pd_type='tins', raw=test_inn, pd_id=test_inn_pd_id)

    mock_simple_fns_communication(
        send_message_request=fns_messages.send_message_request(
            message_name='PostBindPartnerWithPhoneRequest',
            message_content={
                'phone': test_phone,
                'permissions': test_permissions,
            },
        ),
        send_message_response=fns_messages.send_message_response(
            message_id=test_msg_id,
        ),
        get_message_request=fns_messages.get_message_request(
            message_id=test_msg_id,
        ),
        get_message_response=fns_messages.get_message_error_response(
            error_code=code, error_message=message, args=args,
        ),
    )

    response = await taxi_selfemployed_fns_proxy.post(
        '/v1/bind/phone',
        json={
            'phone_pd_id': test_phone_pd_id,
            'permissions': test_permissions,
        },
        params={'business_unit': business_unit},
    )
    assert response.status == status

    content = await response.json()

    assert content == {
        'code': code,
        'message': message,
        **({'details': details} if details else {}),
    }


async def test_bind_by_phone_fns_unavailable(
        mock_fns_unavailable,
        mock_personal_service,
        taxi_selfemployed_fns_proxy,
        fns_messages,
        business_unit,
):
    test_phone = '70000000000'
    test_phone_personal = f'+{test_phone}'
    test_phone_pd_id = 'PHONE_PD_ID'
    test_permissions = ['test_permission']

    mock_personal_service(
        pd_type='phones', raw=test_phone_personal, pd_id=test_phone_pd_id,
    )

    response = await taxi_selfemployed_fns_proxy.post(
        '/v1/bind/phone',
        json={
            'phone_pd_id': test_phone_pd_id,
            'permissions': test_permissions,
        },
        params={'business_unit': business_unit},
    )
    assert response.status == 503

    content = await response.json()

    assert content == {
        'code': 'FNS_UNAVAILABLE',
        'message': 'FNS is currently unavailable',
    }
