import json
import typing

import pytest


@pytest.mark.parametrize(
    'personal_response', ['valid', 'invalid']
)
def test_taxiparks2altay(
        run_taxiparks2altay,
        get_mongo,
        patch,
        load_json,
        personal,
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

    @patch('infranaim.utils.yandex_spravochnik.SpravEntry.get_yt_table')
    def _read_yt_table(cluster, token, table):
        return load_json(table)

    @patch('infranaim.utils.geocoder.GeoObject._request_geo_object')
    def _geo_object(*args, **kwargs):
        return load_json('geo_object.json')

    @patch('cron_scripts.taxiparks2altay.upload_yt_table')
    def _upload_yt_table(
        cluster: str,
        token: str,
        table: str,
        data: typing.Optional[typing.List[str]],
    ):
        for item in data:
            item = json.loads(item)
            assert sorted(item['email']) == [
                'email1@email.com', 'email2@email.com',
            ]

    mongo = get_mongo
    run_taxiparks2altay(mongo, '-d')
