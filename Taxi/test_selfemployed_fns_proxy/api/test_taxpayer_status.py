# pylint: disable=invalid-name,unused-variable
import datetime as dt

import pytest

# pylint: disable=invalid-name
pytestmark = pytest.mark.parametrize(
    'business_unit', ('taxi', 'test_business_unit'),
)


@pytest.mark.now('2022-01-01T00:00:00+00:00')
async def test_taxpayer_status(
        mock_simple_fns_communication,
        mock_personal_service,
        taxi_selfemployed_fns_proxy,
        fns_messages,
        business_unit,
):
    test_inn = '000000000000'
    test_inn_pd_id = 'INN_PD_ID'
    test_phone = '+70000000000'
    test_phone_pd_id = 'PHONE_PD_ID'
    test_msg_id = 'msg_id'

    mock_personal_service(pd_type='tins', raw=test_inn, pd_id=test_inn_pd_id)
    mock_personal_service(
        pd_type='phones', raw=test_phone, pd_id=test_phone_pd_id,
    )

    test_taxpayer_data_fns = {
        'first_name': 'Test',
        'second_name': 'Test',
        'patronymic': 'Test',
        'registration_time': dt.datetime.now(tz=dt.timezone.utc),
        'unregistration_time': dt.datetime.now(tz=dt.timezone.utc),
        'unregistration_reason': 'Test',
        'activities': ['Test'],
        'region': '000000',
        'phone': test_phone,
        'email': 'test@test',
        'account_number': 'Test',
        'update_time': dt.datetime.now(tz=dt.timezone.utc),
        'registration_certificate_number': 'Test',
        'oksm_code': '000',
    }

    mock_simple_fns_communication(
        send_message_request=fns_messages.send_message_request(
            message_name='GetTaxpayerStatusRequestV2',
            message_content={'inn': test_inn},
        ),
        send_message_response=fns_messages.send_message_response(
            message_id=test_msg_id,
        ),
        get_message_request=fns_messages.get_message_request(
            message_id=test_msg_id,
        ),
        get_message_response=fns_messages.get_message_response(
            message_name='GetTaxpayerStatusResponseV2',
            message_content=test_taxpayer_data_fns,
        ),
    )

    response = await taxi_selfemployed_fns_proxy.get(
        '/v1/taxpayer/status',
        params={'business_unit': business_unit, 'inn_pd_id': test_inn_pd_id},
    )
    assert response.status == 200

    content = await response.json()

    content['registration_time'] = dt.datetime.fromisoformat(
        content['registration_time'],
    )
    content['unregistration_time'] = dt.datetime.fromisoformat(
        content['unregistration_time'],
    )
    content['update_time'] = dt.datetime.fromisoformat(content['update_time'])

    test_taxpayer_data = test_taxpayer_data_fns.copy()
    test_taxpayer_data['middle_name'] = test_taxpayer_data.pop('patronymic')
    test_taxpayer_data['last_name'] = test_taxpayer_data.pop('second_name')
    test_taxpayer_data['region_oktmo_code'] = test_taxpayer_data.pop('region')
    test_taxpayer_data.pop('phone')
    test_taxpayer_data['phone_pd_id'] = test_phone_pd_id
    test_taxpayer_data[
        'registration_certificate_num'
    ] = test_taxpayer_data.pop('registration_certificate_number')

    assert content == test_taxpayer_data


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
async def test_taxpayer_status_error(
        mock_simple_fns_communication,
        mock_personal_service,
        taxi_selfemployed_fns_proxy,
        fns_messages,
        business_unit,
        code,
        message,
        status,
):
    test_inn = '000000000000'
    test_inn_pd_id = 'INN_PD_ID'
    test_msg_id = 'msg_id'

    mock_personal_service(pd_type='tins', raw=test_inn, pd_id=test_inn_pd_id)

    mock_simple_fns_communication(
        send_message_request=fns_messages.send_message_request(
            message_name='GetTaxpayerStatusRequestV2',
            message_content={'inn': test_inn},
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
        '/v1/taxpayer/status',
        params={'business_unit': business_unit, 'inn_pd_id': test_inn_pd_id},
    )
    assert response.status == status

    content = await response.json()

    assert content == {'code': code, 'message': message}


async def test_taxpayer_status_fns_unavailable(
        mock_fns_unavailable,
        mock_personal_service,
        taxi_selfemployed_fns_proxy,
        fns_messages,
        business_unit,
):
    test_inn = '000000000000'
    test_inn_pd_id = 'INN_PD_ID'

    mock_personal_service(pd_type='tins', raw=test_inn, pd_id=test_inn_pd_id)

    response = await taxi_selfemployed_fns_proxy.get(
        '/v1/taxpayer/status',
        params={'business_unit': business_unit, 'inn_pd_id': test_inn_pd_id},
    )
    assert response.status == 503

    content = await response.json()

    assert content == {
        'code': 'FNS_UNAVAILABLE',
        'message': 'FNS is currently unavailable',
    }
