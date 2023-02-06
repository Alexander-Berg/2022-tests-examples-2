import pytest

from infranaim.models.configs import external_config


@pytest.mark.parametrize('store_personal', [1, 0])
@pytest.mark.parametrize('personal_response', ['valid', 'invalid'])
async def test_synch_parks(
        get_mongo, run_synch_parks,
        patch, personal, find_field, load_json,
        find_documents_in_update_queue,
        store_personal, personal_response,
):
    @patch('infranaim.clients.personal.PreparedRequestMain.'
           '_generate_headers')
    def _tvm(*args, **kwargs):
        return {'headers': 1}

    @patch('infranaim.clients.personal.PreparedRequestSync._request')
    def _personal(*args, **kwargs):
        result = personal(personal_response, *args, **kwargs)
        return result

    @patch('infranaim.clients.telegram.Telegram.send_message')
    def _telegram(*args, **kwargs):
        return None

    @patch('daemons.synch_taxiparks_zendesk_taximeter.'
           'request_park_data_from_taximeter')
    def _request_park_data_from_taximeter(park_doc):
        park_id = park_doc['park_id']
        return load_json('taximeter_parks.json')[park_id]

    @patch('daemons.synch_taxiparks_zendesk_taximeter.'
           'update_park_in_taximeter')
    def _update_park_in_taximeter(park_doc):
        contact_phone = park_doc['park_phone']
        email = park_doc['park_email']
        assert isinstance(contact_phone, str)
        assert isinstance(email, str)
        contact_phones = [
            item.strip() for item in contact_phone.split(',')
        ]
        emails = [
            item.strip() for item in email.split(',')
        ]
        for item in contact_phones:
            assert item.startswith('+')
        for item in emails:
            assert item.endswith('@email.com')
        return {}

    @patch('daemons.synch_taxiparks_zendesk_taximeter._get_raw_parks')
    def _get_raw_parks():
        return load_json('zendesk_parks.json')

    @patch('daemons.synch_taxiparks_zendesk_taximeter.ticket_fields_update')
    def _ticket_fields_update(*args, **kwargs):
        for item in args[0]:
            if 'OPTOUT' in item['name']:
                raise BaseException('OPTOUT')
        return {'success': True}

    external_config.INFRANAIM_PERSONAL.update({'store_mongo': store_personal})

    mongo = get_mongo
    run_synch_parks(mongo)
