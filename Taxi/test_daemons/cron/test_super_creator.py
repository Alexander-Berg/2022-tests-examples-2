import uuid

import pytest

from infranaim.configs import personal as config_personal
from infranaim.models.configs import external_config


@pytest.mark.parametrize('store_personal', [1, 0])
@pytest.mark.parametrize(
    'doc_name, personal_response',
    [
        ('personal_and_values', 'valid'),
        ('personal_and_values', 'invalid'),
        ('only_values', 'valid'),
        ('only_values', 'invalid'),
        ('only_personal', 'valid'),
        ('only_personal', 'invalid'),
    ]
)
def test_create_ticket(
        run_creator, patch, get_mongo,
        load_json, personal, find_field, personal_imitation,
        check_jobs, store_personal, doc_name, personal_response,
):
    @patch('infranaim.helper.get_zendesk_auth')
    def _zen_auth(*args, **kwargs):
        return 'USER', 'TOKEN'

    @patch('infranaim.helper.get_zendesk_url')
    def _zen_url(*args, **kwargs):
        return 'url'

    @patch('infranaim.helper.get_zendesk_available_jobs')
    def _jobs(*args, **kwargs):
        return 28

    @patch('infranaim.helper.send_request_json')
    def _request(method, url, **kwargs):
        data = kwargs['json']
        tickets = data['tickets']
        assert len(tickets) == 1
        custom_fields = {
            item['id']: item
            for item in tickets[0]['custom_fields']
        }
        assert len(custom_fields) > 0

        fields_forbidden = config_personal.PERSONAL['ZENDESK']['RETRIEVE']
        fields_allowed = config_personal.PERSONAL['ZENDESK']['STORE']
        for field in fields_forbidden:
            ticket_field = custom_fields.get(field)
            assert not ticket_field
        for field in fields_allowed:
            if field == 360006099620:
                continue
            ticket_field = custom_fields.get(field)
            assert ticket_field
        return {
            'job_status': {
                'id': uuid.uuid4().hex
            }
        }

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
    doc = load_json('tickets_to_create_docs.json')[doc_name]
    mongo.zendesk_tickets_to_create.insert_one(doc)
    run_creator(mongo)
    check_jobs(
        mongo, store_personal, personal_response,
        doc_name, ticket_type='create'
    )


@pytest.mark.parametrize('store_personal', [1, 0])
@pytest.mark.parametrize(
    'size',
    [
        2,
        10
    ]
)
def test_create_batch_size(
        run_creator,
        patch,
        get_mongo,
        load_json,
        personal,
        find_field,
        personal_imitation,
        check_jobs,
        store_personal,
        size,
):
    @patch('infranaim.helper.get_zendesk_auth')
    def _zen_auth(*args, **kwargs):
        return 'USER', 'TOKEN'

    @patch('infranaim.helper.get_zendesk_url')
    def _zen_url(*args, **kwargs):
        return 'url'

    @patch('infranaim.helper.get_zendesk_available_jobs')
    def _jobs(*args, **kwargs):
        return 28

    @patch('infranaim.helper.send_request_json')
    def _request(method, url, **kwargs):
        data = kwargs['json']
        tickets = data['tickets']
        assert len(tickets) == size
        custom_fields = {
            item['id']: item
            for item in tickets[0]['custom_fields']
        }
        assert len(custom_fields) > 0

        fields_forbidden = config_personal.PERSONAL['ZENDESK']['RETRIEVE']
        fields_allowed = config_personal.PERSONAL['ZENDESK']['STORE']
        for field in fields_forbidden:
            ticket_field = custom_fields.get(field)
            assert not ticket_field
        for field in fields_allowed:
            if field == 360006099620:
                continue
            ticket_field = custom_fields.get(field)
            assert ticket_field
        return {
            'job_status': {
                'id': uuid.uuid4().hex
            }
        }

    @patch('infranaim.clients.personal.PreparedRequestMain._generate_headers')
    def _tvm(*args, **kwargs):
        return {'headers': 1}

    @patch('infranaim.clients.personal.PreparedRequestSync._request')
    def _personal(*args, **kwargs):
        result = personal('valid', *args, **kwargs)
        return result

    @patch('infranaim.clients.telegram.Telegram.send_message')
    def _telegram(*args, **kwargs):
        return None

    external_config.INFRANAIM_PERSONAL.update({'store_mongo': store_personal})
    external_config.HIRING_INFRANAIM_ZENDESK_BATCH_SIZES.update(
        {'create': size}
    )

    mongo = get_mongo
    doc = load_json('tickets_to_create_docs.json')['only_personal']
    for i in range(size + 1):
        doc['_id'] = i
        mongo.zendesk_tickets_to_create.insert_one(doc)
    run_creator(mongo)
    assert mongo.zendesk_tickets_to_create.count_documents({}) == 1
