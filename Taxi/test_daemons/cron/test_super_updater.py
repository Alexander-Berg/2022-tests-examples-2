import json
import uuid

import pytest
import requests

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
def test_update_ticket(
        run_updater, patch, get_mongo,
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

    @patch('infranaim.utils.make_request.request')
    def _request(*args, **kwargs):
        data = kwargs['payload']
        tickets = data['tickets']
        assert len(tickets) == 1
        custom_fields = tickets[0]['custom_fields']
        assert len(custom_fields) > 0

        fields_forbidden = config_personal.PERSONAL['ZENDESK']['RETRIEVE']
        fields_allowed = config_personal.PERSONAL['ZENDESK']['STORE']
        for field in fields_forbidden:
            ticket_field = next(
                (
                    _doc
                    for _doc in custom_fields
                    if _doc['id'] == field
                ),
                None
            )
            assert not ticket_field
        for field in fields_allowed:
            if field == 360006099620:
                continue
            ticket_field = next(
                (
                    _doc
                    for _doc in custom_fields
                    if _doc['id'] == field
                ),
                None
            )
            assert ticket_field
        data = {
            'job_status': {
                'id': uuid.uuid4().hex
            }
        }
        result = requests.Response()
        result._content = bytes(json.dumps(data), encoding='utf8')
        result.status_code = 200
        return result

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
    doc = load_json('tickets_to_update_docs.json')[doc_name]
    mongo.zendesk_tickets_to_update.insert_one(doc)
    run_updater(mongo)
    check_jobs(
        mongo, store_personal, personal_response,
        doc_name, ticket_type='update'
    )
