import pytest

from infranaim.configs import emailer as config
from infranaim.models.configs import external_config


@pytest.mark.parametrize('store_personal', [1, 0])
@pytest.mark.parametrize('personal_response', ['valid', 'invalid'])
def test_email_sender(
        run_email_sender, get_mongo, patch,
        find_field, load_json, personal, store_personal, personal_response,
):
    @patch('infranaim.clients.emailer.Emailer._send_email')
    def _send(payload):
        return 'Sent'

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

    external_config.INFRANAIM_PERSONAL.update({'store_mongo': store_personal})

    db = get_mongo
    run_email_sender(db)

    sent_emails = list(db.email_sent.find())
    if personal_response != 'valid':
        assert len(sent_emails) == 2
    else:
        assert len(sent_emails) == 3

    for item in sent_emails:
        assert item.get('email') or item.get('personal_email_ids')
        assert item.get('from')
