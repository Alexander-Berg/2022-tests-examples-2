import pytest


def _case(
        form_code: str,
        field_code: str,
        values: dict,
        value: dict,
        response_status=200,
        response_json: dict = None,
        verify_failed=False,
        mock_called=True,
        skip_validation_state=False,
        id_=None,
):
    return pytest.param(
        form_code,
        field_code,
        values,
        value,
        response_status,
        response_json or {},
        verify_failed,
        mock_called,
        skip_validation_state,
        id=id_,
    )


_PARAMS = (
    'form_code, '
    'field_code, '
    'values, '
    'value, '
    'response_status, '
    'response_json, '
    'verify_failed, '
    'mock_called, '
    'skip_validation_state'
)


@pytest.mark.usefixtures('territories_mock')
@pytest.mark.config(TVM_RULES=[{'src': 'form-builder', 'dst': 'personal'}])
@pytest.mark.parametrize(
    _PARAMS,
    [
        _case(
            'form-1',
            'field-1',
            {'field-1': {'type': 'string', 'stringValue': '+79215554433'}},
            {'type': 'string', 'stringValue': '1234'},
            id_='all ok',
        ),
        _case(
            'form-2',
            'field-1',
            {'field-1': {'type': 'string', 'stringValue': '+79215554433'}},
            {'type': 'string', 'stringValue': '1234'},
            response_status=404,
            response_json={
                'code': 'NOT_FOUND_ERROR',
                'message': 'form "form-2" is not found',
            },
            mock_called=False,
            skip_validation_state=True,
            id_='form not found',
        ),
        _case(
            'form-1',
            'field-3',
            {'field-1': {'type': 'string', 'stringValue': '+79215554433'}},
            {'type': 'string', 'stringValue': '1234'},
            response_status=404,
            response_json={
                'code': 'NOT_FOUND_ERROR',
                'message': 'field "field-3" not found',
            },
            mock_called=False,
            skip_validation_state=True,
            id_='field not found',
        ),
        _case(
            'form-1',
            'field-1',
            {'field-1': {'type': 'string', 'stringValue': '+79215554433'}},
            {'type': 'string', 'stringValue': '1234'},
            response_status=400,
            response_json={
                'code': 'VERIFICATION_FAILED',
                'message': 'user data verification failed',
            },
            verify_failed=True,
            id_='verification failed',
        ),
        _case(
            'form-1',
            'field-1',
            {'field-1': {'type': 'string', 'stringValue': '+79215554434'}},
            {'type': 'string', 'stringType': 'a'},
            response_status=400,
            response_json={
                'code': 'VALIDATION_FAILED',
                'message': (
                    'fields value has changed in '
                    'before submitting verification data'
                ),
            },
            verify_failed=True,
            mock_called=False,
            skip_validation_state=True,
            id_='fields value changed after verification',
        ),
    ],
)
async def test_verify_data(
        mockserver,
        mock_hiring_selfreg_forms,
        web_context,
        web_app_client,
        cached_personal_mock,
        check_validation_state,
        form_code,
        field_code,
        values,
        value,
        response_status,
        response_json,
        verify_failed,
        mock_called,
        skip_validation_state,
):
    cached_personal_mock['phones'].store('+79215554433')

    @mock_hiring_selfreg_forms('/v1/auth/phone/check')
    async def _check_handler(request):
        if verify_failed:
            return mockserver.make_response(
                status=401, json={'success': False, 'message': 'oops'},
            )
        return {'success': True, 'message': 'verification ok'}

    response = await web_app_client.post(
        '/v1/async-validators/form/verify/',
        json={
            'form_code': form_code,
            'field_code': field_code,
            'values': values,
            'value': value,
        },
        params={'submit_id': 'submit_id'},
    )
    assert response.status == response_status, await response.text()
    assert response_json == await response.json()
    assert _check_handler.has_calls == mock_called

    if not skip_validation_state:
        await check_validation_state(form_code, field_code, values)
