import pytest


@pytest.mark.usefixtures('log_in')
@pytest.mark.parametrize(
    'request_data, field, personal_response, expected',
    [
        (
            'valid', 'personal_contact_phone_id', 'valid', {
                'contact_phone': '+79260909099',
                'personal_contact_phone_id': [
                    'fdf688c7da41483698fabea16cefa592'
                ]
            }
        ),
        (
            'valid', 'personal_dispatch_phone_id', 'valid', {
                'dispatch_phone': '+78887766554',
                "personal_dispatch_phone_id": [
                    '9c92c1aeb5f6488390b45dae2c58264c'
                ]
            }
        ),
        (
            'valid', 'personal_whatsapp_contact_id', 'valid', {
                'whatsapp_contact': '+79689540572',
                "personal_whatsapp_contact_id": "bb0302d879474e93"
                                                "905d44d1c289ccb5"
            }
        ),
        (
            'valid', 'personal_email_ids', 'valid', {
                'email': ['email1@email.com', 'email2@email.com'],
                "personal_email_ids": [
                    "2b9fbd6491444c6dac6945eaaf2f705c",
                    "46771270474d4d5982d8324ae5d2262c"
                ]
            }
        ),
        (
            'valid', 'personal_contact_phone_id', 'invalid', {
                'code': 'NO_DATA_GENERATED',
                'message': 'No Data Generated',
                'details': 'No personal data found'
            }
        )
    ]
)
def test_show_personal(
        taxiparks_client, csrf_token_session, patch, load_json,
        personal, personal_imitation,
        request_data, field, personal_response, expected,
):
    @patch('infranaim.clients.personal.PreparedRequestMain._generate_headers')
    def _tvm(*args, **kwargs):
        return {'headers': 1}

    @patch('infranaim.clients.personal.PreparedRequestSync._request')
    def _personal(*args, **kwargs):
        result = personal(personal_response, *args, **kwargs)
        return result

    @patch('infranaim.clients.telegram.Telegram.send_message')
    def _telegram(*args, **kwargs):
        return None

    data = load_json('requests_personal.json')[request_data][field]
    data['csrf_token'] = csrf_token_session()
    res = taxiparks_client.post('/utility/personal/show', json=data)
    response = res.json
    assert response == expected
    if personal_response != 'valid':
        assert res.status_code == 400
    else:
        assert res.status_code == 200
