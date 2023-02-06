import pytest
from cron_scripts import sms_sender


class MockExternalConfig:
    HIRING_SCOUTS_SMS_INTENTS = {
            '__default__': 'taxi_infranaim',
            'taxi_infranaim': True
        }
    HIRING_SCOUTS_SMS_ID_TYPES = {
        '__default__': 'zendesk',
        'zendesk': True
    }


@pytest.fixture
def run_sms_sender():
    def run(db):
        sms_sender.do_stuff(db, None)
    return run


def test_sms_sender(
        run_sms_sender, get_mongo, patch, find_field, load_json,
):
    @patch('infranaim.clients.infobip.Infobip._fetch')
    async def _fetch(
            session,
            payload,
    ):
        phone = payload.get('phone')
        phone_id = payload.get('phone_id')
        assert any([phone, phone_id])
        return {'messages': {}}

    @patch('infranaim.clients.tvm.TVMClient.get_auth_headers')
    def _tvm(*args, **kwargs):
        return None

    bad_sms_count = 1

    global external_config
    external_config = MockExternalConfig

    db = get_mongo

    count_to_send = db.sms_pending.count_documents({}) - bad_sms_count
    count_already_sent = db.sms_sent.count_documents({})

    run_sms_sender(db)

    count_sent = db.sms_sent.count_documents({}) - count_already_sent
    assert count_to_send == count_sent

    updates = list(db.zendesk_tickets_to_update.find())
    zendesk_sms = len(
        [
            item
            for item in load_json('db_sms_pending.json')
            if (
                item.get('requester_id') == 'zendesk'
                and item.get('ticket_id') != '__invalid__'
            )
        ]
    )
    assert len(updates) == zendesk_sms
