import pytest


@pytest.mark.parametrize(
    'lead_id',
    [
        pytest.param('1234', id='to_amo'),
        pytest.param(None, id='to_st'),
        pytest.param('9001', id='to_amo_fail'),
    ],
)
async def test_manager_notification(
        taxi_cargo_sf, mock_amo_create_note, mock_startrek, lead_id,
):
    json = {
        'event_code': 'something_happened',
        'ticket_id': 'ticket_id',
        'event_message': 'something terrible happened',
        'manager_request_data': {
            'contract': '80085',
            'manager': 'Ivan-the-Lazy',
        },
    }
    if lead_id:
        json['manager_request_data']['crm'] = {'lead_id': lead_id}
    response = await taxi_cargo_sf.post(
        '/internal/cargo-sf/internal-requests/'
        'accept-manager-request-notification',
        json=json,
    )
    assert response.status_code == 200
    if lead_id == '1234':
        next_call = mock_amo_create_note.next_call()
        assert next_call['request'].json == [
            {
                'entity_id': 1234,
                'note_type': 'common',
                'params': {
                    'text': (
                        'Изменение по заявке на договор '
                        'ticket_id (something_happened)\n'
                        'maybe not so terrible\n'
                        'something terrible happened\n'
                        '{"contract":"80085","manager":"Ivan-the-Lazy",'
                        '"crm":{"lead_id":"1234"}}'
                    ),
                },
            },
        ]
    elif lead_id == '9001':
        assert mock_amo_create_note.times_called == 1
        assert mock_startrek.times_called == 1
    else:
        next_call = mock_startrek.next_call()
        assert (
            next_call['request'].headers['Authorization']
            == 'OAuth startrek_token'
        )
        assert next_call['request'].json == {
            'description': (
                'Изменение по заявке на договор '
                'ticket_id (something_happened)\n'
                'maybe not so terrible\n'
                'something terrible happened\n'
                '{"contract":"80085","manager":"Ivan-the-Lazy"}'
            ),
            'queue': 'CARGOMANREQ',
            'summary': 'Новое событие в процессе регистрации договора',
        }


@pytest.mark.parametrize(
    'code,response_json,form_id',
    [
        pytest.param(200, {}, '1', id='happy_path'),
        pytest.param(
            400,
            {'code': '', 'message': '', 'details': {}},
            '1',
            id='bad_cargo_crm_response',
        ),
        pytest.param(403, {}, '3', id='access_error'),
    ],
)
async def test_manager_request(
        taxi_cargo_sf, mock_cargo_crm, code, response_json, form_id,
):
    json = {
        'contract': '80085',
        'manager': 'Ivan-the-Lazy',
        'status': code,
        'json': response_json,
    }
    headers = {
        'X-Form-Id': form_id,
        'X-Access-Token': 'API_TOKEN_YA_FORM_PROXY_AMOCRM',
    }

    response = await taxi_cargo_sf.post(
        '/internal/cargo-sf/' 'internal-requests/manager-request',
        json=json,
        headers=headers,
    )
    assert response.status_code == code
