import pytest

from infranaim.models.configs import external_config


@pytest.mark.parametrize(
    'store_personal, personal_response',
    [
        (1, 'valid'),
        (0, 'valid'),
        (1, 'invalid'),
        (0, 'invalid'),
    ]
)
def test_send_sms(
        flask_client_factory, get_mongo, patch, load_json,
        personal, personal_imitation,
        store_personal, personal_response,
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

    mongo = get_mongo
    external_config.INFRANAIM_PERSONAL.update({'store_mongo': store_personal})
    client = flask_client_factory(mongo)

    data = load_json('requests_send_sms.json')
    count = 0
    for request_data, status_code in data:
        response = client.post(
            '/v2/utility/sms',
            json=request_data,
        )
        if response.status_code == 200:
            count += 1
        assert response.status_code == status_code

    sms_docs = list(mongo.sms_pending.find())
    assert len(sms_docs) == count

    for doc in sms_docs:
        if personal_response == 'valid':
            assert doc['personal_phone_id']

        if store_personal:
            assert doc['phone']
            if personal_response != 'valid':
                assert 'personal_phone_id' not in doc
        else:
            if personal_response == 'valid':
                assert not doc['phone']
            else:
                assert doc['phone']
