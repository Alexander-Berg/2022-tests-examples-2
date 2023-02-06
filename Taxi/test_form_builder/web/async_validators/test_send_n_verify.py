from typing import Optional

import pytest


_PARAMS = (
    'form_code,'
    'field_code,'
    'values,'
    'value,'
    'send_failed,'
    'send_response_json,'
    'verify_failed,'
    'verify_response_json,'
)


def _case(
        form_code: str,
        field_code: str,
        values: dict,
        value: dict,
        send_failed: bool,
        verify_failed: bool,
        send_response_json: Optional[dict] = None,
        verify_response_json: Optional[dict] = None,
        id_: Optional[str] = None,
):
    return pytest.param(
        form_code,
        field_code,
        values,
        value,
        send_failed,
        send_response_json,
        verify_failed,
        verify_response_json,
        id=id_,
    )


@pytest.mark.config(TVM_RULES=[{'src': 'form-builder', 'dst': 'personal'}])
@pytest.mark.usefixtures('territories_mock')
@pytest.mark.parametrize(
    _PARAMS,
    [
        _case(
            'form-1',
            'field-1',
            {'field-1': {'type': 'string', 'stringValue': '+79999999999'}},
            {'type': 'string', 'stringValue': '1234'},
            False,
            False,
        ),
        _case(
            'form-1',
            'field-1',
            {'field-1': {'type': 'string', 'stringValue': '+79999999999'}},
            {'type': 'string', 'stringValue': '1234'},
            True,
            False,
            send_response_json={
                'code': 'VALIDATION_FAILED',
                'message': (
                    '{\'code\': \'invalid_phone\', '
                    '\'message\': \'invalid phone\'}'
                ),
            },
        ),
        _case(
            'form-1',
            'field-1',
            {'field-1': {'type': 'string', 'stringValue': '+79999999999'}},
            {'type': 'string', 'stringValue': '1234'},
            False,
            True,
            verify_response_json={
                'code': 'VERIFICATION_FAILED',
                'message': 'user data verification failed',
            },
        ),
    ],
)
async def test_send_n_verify(
        mockserver,
        mock_hiring_selfreg_forms,
        taxi_form_builder_web,
        cached_personal_mock,
        form_code,
        field_code,
        values,
        value,
        send_failed,
        send_response_json,
        verify_failed,
        verify_response_json,
        check_validation_state,
):
    cached_personal_mock['phones'].store('+79999999999')

    @mock_hiring_selfreg_forms('/v1/auth/phone/submit')
    async def _submit_handler(_):
        if send_failed:
            return mockserver.make_response(
                status=400,
                json={'code': 'invalid_phone', 'message': 'invalid phone'},
            )
        return {'code': 'ok', 'message': 'Phone submitted'}

    @mock_hiring_selfreg_forms('/v1/auth/phone/check')
    async def _check_handler(request):
        if verify_failed:
            return mockserver.make_response(
                status=401, json={'success': False, 'message': 'oops'},
            )
        return {'success': True, 'message': 'verification ok'}

    response = await taxi_form_builder_web.post(
        '/v1/async-validators/form/send/',
        json={
            'form_code': form_code,
            'field_code': field_code,
            'values': values,
        },
        params={'submit_id': 'submit_id'},
    )
    if send_failed:
        assert response.status == 400, await response.text()
        assert send_response_json == await response.json()
        return
    assert response.status == 200, await response.text()
    await check_validation_state(form_code, field_code, values)

    response = await taxi_form_builder_web.post(
        '/v1/async-validators/form/verify/',
        json={
            'form_code': form_code,
            'field_code': field_code,
            'values': values,
            'value': value,
        },
        params={'submit_id': 'submit_id'},
    )
    if verify_failed:
        assert response.status == 400, await response.text()
        assert verify_response_json == await response.json()
    else:
        assert response.status == 200, await response.text()

    await check_validation_state(form_code, field_code, values)
