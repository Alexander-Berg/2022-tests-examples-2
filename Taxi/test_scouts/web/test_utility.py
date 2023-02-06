import pytest

from infranaim.configs import emailer as config
from infranaim.models.configs import external_config


@pytest.mark.parametrize(
    'store_personal, personal_response, request_name',
    [
        (1, 'valid', 'w/o_from'),
        (0, 'valid', 'w/o_from'),
        (0, 'valid', 'with_from'),
        (1, 'valid', 'with_from'),
        (1, 'invalid', 'w/o_from'),
        (0, 'invalid', 'w/o_from'),
    ]
)
def test_email(
        flask_client_factory, get_mongo, patch, load_json,
        personal, personal_imitation,
        store_personal, personal_response, request_name
):
    @patch('infranaim.helper._find_valid_token')
    def _getenv(*args, **kwargs):
        return 'TOKEN'

    @patch('infranaim.helper._is_equal_b64')
    def _token(*args, **kwargs):
        return True

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

    config.FROM = 'test@example.com'


    mongo = get_mongo
    external_config.INFRANAIM_PERSONAL.update({'store_mongo': store_personal})
    client = flask_client_factory(mongo)

    data = load_json('requests_email.json')['valid'][request_name]
    res = client.post('/utility/email', json=data)
    assert res.status_code == 200

    email_docs = list(mongo.email_pending.find())
    assert len(email_docs) == 1
    doc = email_docs[0]

    assert doc['from']
    if personal_response == 'valid':
        assert len(doc['personal_email_ids']) == len(data['email'])
        for email in data['email']:
            assert personal_imitation(email) in doc['personal_email_ids']

    if store_personal:
        assert doc['email']
        if personal_response != 'valid':
            assert 'personal_email_ids' not in doc
    else:
        if personal_response == 'valid':
            assert not doc['email']
        else:
            assert doc['email']


@pytest.mark.usefixtures('log_in')
@pytest.mark.parametrize(
    'request_data, field, personal_response, expected',
    [
        (
            'valid', 'personal_phone_id', 'valid', {
                'phone': '+79264927795',
                'personal_phone_id': '1cd53a0af061466ebcafa3527ee8f892'
            }
        ),
        (
            'valid', 'personal_license_id', 'valid', {
                'driver_license': '12TK123456',
                "personal_license_id": "65e7bf4ad95e4c339927680e843ecf66"
            }
        ),
        (
            'valid', 'personal_email_ids', 'valid', {
                'email': ['email1@email.com'],
                "personal_email_ids": [
                    "2b9fbd6491444c6dac6945eaaf2f705c"
                ]
            }
        ),
        (
            'valid', 'personal_phone_id', 'invalid', {
                'code': 'NO_DATA_GENERATED',
                'message': 'No Data Generated',
                'details': 'No personal data found'
            }
        )
    ]
)
def test_show_personal(
        flask_client, csrf_token_session, patch, load_json,
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
    res = flask_client.post('/utility/personal/show', json=data)
    response = res.json
    assert response == expected
    if personal_response != 'valid':
        assert res.status_code == 400
    else:
        assert res.status_code == 200
