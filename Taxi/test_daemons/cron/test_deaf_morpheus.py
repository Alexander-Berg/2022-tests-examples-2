import pytest

from infranaim.models.configs import external_config
from infranaim.configs import personal as config_personal


PERSONAL_ID_FIELDS = config_personal.PERSONAL['MAP_FIELDS']['RETRIEVE']
PERSONAL_DATA_FIELDS = config_personal.PERSONAL['MAP_FIELDS']['STORE']


def _check_personal(iterable, field_data, field_personal):
    for item in iterable:
        assert item.get(field_data) or item.get(field_personal)


@pytest.mark.parametrize('store_personal', [0, 1])
@pytest.mark.parametrize('personal_response', ['valid', 'invalid'])
def test_deaf_morpheus(
        get_mongo, run_deaf_morpheus, patch,
        personal, store_personal, personal_response,
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

    external_config.INFRANAIM_PERSONAL.update({'store_mongo': store_personal})

    mongo = get_mongo
    iterations = 0
    while run_deaf_morpheus(mongo):
        iterations += 1
    assert iterations == 4
    assert mongo.deaf_drivers_to_add.count_documents({}) == 0

    sms = list(mongo.sms_pending.find())
    emails = list(mongo.email_pending.find())
    updates = list(mongo.zendesk_tickets_to_update.find())
    assert len(sms) == 3
    assert len(emails) == 3
    assert len(updates) == 4

    _check_personal(
        sms,
        'phone',
        'personal_phone_id',
    )

    _check_personal(
        emails,
        'email',
        'personal_email_ids',
    )
