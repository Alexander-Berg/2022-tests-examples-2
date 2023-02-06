import pytest


def _case(
        form_code,
        field_code,
        values,
        response_status=200,
        response_json=None,
        send_failed=False,
        mock_called=True,
        skip_state_check=False,
):
    return (
        form_code,
        field_code,
        values,
        response_status,
        response_json or {},
        send_failed,
        mock_called,
        skip_state_check,
    )


_PARAMS = (
    'form_code, '
    'field_code, '
    'values, '
    'response_status, '
    'response_json, '
    'send_failed, '
    'mock_called, '
    'skip_state_check'
)


@pytest.mark.config(TVM_RULES=[{'src': 'form-builder', 'dst': 'personal'}])
@pytest.mark.usefixtures('cached_personal_mock', 'territories_mock')
@pytest.mark.parametrize(
    _PARAMS,
    [
        _case(
            'form-1',
            'field-1',
            {'field-1': {'type': 'string', 'stringValue': '+79215554433'}},
        ),
        _case(
            'form-1',
            'field-1',
            {'field-1': {'type': 'string', 'stringValue': '+7(921)5554433'}},
        ),
        _case(
            'form-1',
            'field-1',
            {'field-1': {'type': 'string', 'stringValue': '+7921-555-4433'}},
        ),
        _case(
            'form-1',
            'field-1',
            {'field-1': {'type': 'string', 'stringValue': '89215554433'}},
        ),
        _case(
            'form-2',
            'field-1',
            {},
            response_status=404,
            response_json={
                'code': 'NOT_FOUND_ERROR',
                'message': 'form "form-2" is not found',
            },
            mock_called=False,
            skip_state_check=True,
        ),
        _case(
            'form-1',
            'field-3',
            {},
            response_status=404,
            response_json={
                'code': 'NOT_FOUND_ERROR',
                'message': 'field "field-3" not found',
            },
            mock_called=False,
            skip_state_check=True,
        ),
        _case(
            'form-1',
            'field-1',
            {'field-1': {'type': 'string', 'stringValue': '+79215554433'}},
            response_status=400,
            response_json={
                'code': 'VALIDATION_FAILED',
                'message': (
                    '{\'code\': \'invalid_phone\', '
                    '\'message\': \'invalid phone\'}'
                ),
            },
            send_failed=True,
        ),
    ],
)
async def test_send_data(
        mockserver,
        mock_hiring_selfreg_forms,
        web_context,
        web_app_client,
        check_validation_state,
        form_code,
        field_code,
        values,
        response_status,
        response_json,
        send_failed,
        mock_called,
        skip_state_check,
):
    @mock_hiring_selfreg_forms('/v1/auth/phone/submit')
    async def _submit_handler(_):
        if send_failed:
            return mockserver.make_response(
                status=400,
                json={'code': 'invalid_phone', 'message': 'invalid phone'},
            )
        return {'code': 'ok', 'message': 'Phone submitted'}

    response = await web_app_client.post(
        '/v1/async-validators/form/send/',
        json={
            'form_code': form_code,
            'field_code': field_code,
            'values': values,
        },
        params={'submit_id': 'submit_id'},
    )
    assert response.status == response_status, await response.text()
    assert response_json == await response.json()
    assert _submit_handler.has_calls == mock_called

    if not skip_state_check:
        await check_validation_state(
            form_code, field_code, values, empty=response_status != 200,
        )
