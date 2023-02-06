import pytest

from infranaim.models.configs import external_config


PERSONAL_FIELDS = [
    'phone',
    'driver_license',
    'yandex_login',
]
PERSONAL_ID_FIELDS = [
    'personal_phone_id',
    'personal_license_id',
    'personal_yandex_login_id',
]


@pytest.mark.parametrize('store_personal', [1, 0])
@pytest.mark.parametrize('use_bulk', [1, 0])
@pytest.mark.parametrize('personal_response', ['valid', 'invalid'])
def test_zendesk2mongo(
        run_zendesk2mongo, patch, personal,
        load_json, get_mongo, store_personal, personal_response, use_bulk
):
    @patch('infranaim.helper.get_zendesk_auth')
    def _zen_auth(*args, **kwargs):
        return 'USER', 'TOKEN'

    @patch('infranaim.helper.get_zendesk_url')
    def _zen_url(route_name):
        if route_name == 'TICKET':
            template = 'http://zendesk_url.com/ticket?id={ticket_id}'
        elif route_name == 'TICKETS_BULK':
            template = 'http://zendesk_url.com/tickets?ids={ticket_ids}'
        else:
            raise ValueError('Invalid route name')
        return template

    @patch('infranaim.helper.get_zendesk_available_jobs')
    def _jobs(*args, **kwargs):
        return 28

    @patch('daemons.zendesk2mongo.fetch')
    async def _request(*args, **kwargs):
        url = args[0]
        return load_json('zendesk_response.json')[url]

    @patch('daemons.zendesk2mongo.is_bulk_enabled')
    def _bulk(*args, **kwargs):
        return use_bulk

    @patch('infranaim.clients.personal.PreparedRequestMain.'
           '_generate_headers')
    def _tvm(*args, **kwargs):
        return {'headers': 1}

    @patch('infranaim.clients.personal.PreparedRequestAsync._fetch')
    async def _personal(*args, **kwargs):
        result = personal(personal_response, *args, **kwargs)
        return result

    @patch('infranaim.clients.telegram.Telegram.send_message')
    def _telegram(*args, **kwargs):
        return None

    external_config.INFRANAIM_PERSONAL.update({'store_mongo': store_personal})
    mongo = get_mongo

    times_called = 0
    assert list(mongo.queue.find())
    while list(mongo.queue.find()):
        run_zendesk2mongo(mongo)
        times_called += 1
    assert not list(mongo.queue.find())
    assert times_called == 1

    tickets = list(mongo.tickets.find())
    assert len(tickets) == 2
    for ticket in tickets:
        assert ticket['_id'] in (123, 124)
        assert ticket['id'] in ('123', '124')
        if personal_response == 'valid':
            for field in PERSONAL_ID_FIELDS:
                assert ticket[field]
            if store_personal:
                for field in PERSONAL_FIELDS:
                    assert ticket[field]
        else:
            if not store_personal:
                for field in PERSONAL_FIELDS:
                    assert ticket[field]
