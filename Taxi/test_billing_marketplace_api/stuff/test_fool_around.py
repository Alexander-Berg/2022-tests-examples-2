# pylint: disable=redefined-outer-name,duplicate-code,unused-variable
import json

import pytest

from billing_marketplace_api.generated.cron import run_cron


@pytest.mark.skip(reason='incompatible with pytest-xdist TAXITOOLS-472')
@pytest.mark.parametrize(
    'data',
    [
        (
            {
                'items': [
                    {
                        'created_at': '2018-10-21T00:00:00+00:00',
                        'currency': 'RUB',
                        'charge_value': '22.00',
                        'charge_source': 'advert_call',
                        'park_id': 'dbp1',
                        'charge_id': '0',
                    },
                    {
                        'created_at': '2018-10-21T00:00:00+00:00',
                        'currency': 'RUB',
                        'charge_value': '22.00',
                        'charge_source': 'advert_call',
                        'park_id': 'dbp2',
                        'charge_id': '1',
                    },
                    {
                        'created_at': '2018-10-21T00:00:00+00:00',
                        'currency': 'RUB',
                        'charge_value': '22.00',
                        'charge_source': 'advert_call',
                        'park_id': 'dbp1',
                        'charge_id': '2',
                    },
                    {
                        'created_at': '2018-10-21T17:05:34+00:00',
                        'currency': 'RUB',
                        'charge_value': '23.00',
                        'charge_source': 'advert_call',
                        'park_id': 'dbp2',
                        'charge_id': '3',
                    },
                ],
            }
        ),
    ],
)
async def test_fool_around(
        db,
        simple_secdist,
        patch,
        data,
        response_mock,
        patch_aiohttp_session,
        monkeypatch,
):
    monkeypatch.setattr(
        'billing_marketplace_api.stuff.fool_around.DOCUMENTS_LIMIT', 3,
    )

    @patch('yt.wrapper.YtClient.exists')
    def yt_exists(path):
        assert path == 'services/marketplace/export'
        return True

    @patch('yt.wrapper.YtClient.list')
    def yt_list(path):
        assert path == 'services/marketplace/export'
        return ['2018-10-20', '2018-10-21']

    @patch('yt.wrapper.YtClient.row_count')
    def yt_row_count(path):
        return 1

    @patch('yt.wrapper.YtClient.read_table')
    def read_table(path):
        for doc in [
                {
                    'dt': '2018-10-21T00:00:00+00:00',
                    'client_id': '321',
                    'comission_currency': 'RUB',
                    'comission_value': '23.00',
                    'type': 'marketplace_advert_call',
                    'id': 0,
                },
        ]:
            yield doc

    @patch('yt.wrapper.YtClient.write_table')
    def write_table(path, chunk):
        assert path == (
            '//home/taxi/development/services/marketplace/export/2018-10-21'
        )
        assert len(chunk) == 3
        assert chunk[0]['client_id'] == '3'

    @patch_aiohttp_session(
        'https://marketplace-backend.taxi.tst.yandex.net/'
        'api/v1/billing/get_charges',
        'POST',
    )
    def mock_request(method, url, **kwargs):
        assert method == 'post'
        assert 'v1/billing/get_charges' in url
        loaded_params = json.loads(kwargs['data'])
        limit = loaded_params['limit']
        more_than_id = loaded_params['more_than_id'] + 1
        assert limit == 3
        new_data = data.copy()
        new_data['items'] = new_data['items'][
            more_than_id : more_than_id + limit
        ]
        return response_mock(json=new_data)

    await run_cron.main(
        ['billing_marketplace_api.stuff.fool_around', '-t', '0'],
    )
