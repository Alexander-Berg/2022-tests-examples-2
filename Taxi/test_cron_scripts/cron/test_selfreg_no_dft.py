import pytest

from infranaim.models.configs import external_config


@pytest.mark.parametrize(
    'store_personal', [1, 0]
)
@pytest.mark.parametrize(
    'personal_response', ['valid', 'invalid']
)
def test_selfreg_no_dft(
        run_selfreg_no_dft,
        get_mongo,
        load_json,
        find_field,
        patch,
        personal,
        store_personal,
        personal_response,
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

    @patch('cron_scripts.selfreg_no_dft.get_yt_table')
    def _yt_table(*args, **kwargs):
        return load_json('yt_table.json')

    external_config.INFRANAIM_PERSONAL.update({'store_mongo': store_personal})

    mongo = get_mongo
    run_selfreg_no_dft(mongo, '-d')
    docs = list(mongo.zendesk_tickets_to_create.find())
    assert len(docs) == 3

    for doc in docs:
        ticket = doc['data']
        phone = find_field(ticket['custom_fields'], 30557445)
        pd_phone = find_field(ticket['custom_fields'], 360005536320)
        driver_license = find_field(ticket['custom_fields'], 30148269)
        pd_license = find_field(ticket['custom_fields'], 360005536340)
        name = find_field(ticket['custom_fields'], 111)['value']

        if (
            (
                not store_personal
                and personal_response == 'valid'
            )
            or name == 'Name3'
        ):
            assert not any([phone, driver_license])
        else:
            assert phone['value']
            assert driver_license['value']

        if (
            personal_response != 'valid'
            and name != 'Name3'
        ):
            assert not any([pd_license, pd_phone])
        else:

            assert pd_phone['value']
            assert pd_license['value']
