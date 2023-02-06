import json

import pytest

ENDPOINT = '/fleet/cashbox/v1/parks/cashboxes/list'


@pytest.fixture(name='personal_tins_retrieve')
def _personal_tins_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/tins/retrieve')
    async def mock_callback(request):
        tin_id = request.json['id']
        return {'id': tin_id, 'value': tin_id[:-3]}

    return mock_callback


@pytest.mark.pgsql(
    'cashbox_integration',
    queries=[
        'INSERT INTO cashbox_integration.cashboxes '
        'VALUES(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\','
        '       \'{}\',\'{}\',\'{}\',\'{}\',\'{}\')'.format(
            'park_123',
            'id_abc123',
            'idemp_100500',
            '2016-06-22 19:10:25-07',
            '2016-06-22 19:10:25-07',
            'valid',
            False,
            'atol_online',
            json.dumps(
                {
                    'tin_pd_id': '0123456789_id',
                    'tax_scheme_type': 'simple',
                    'group_code': 'super_park_group',
                },
            ),
            json.dumps(
                {
                    'login': 'M5a7svvcrnA7E5axBDY2sw==',
                    'password': 'dCKumeJhRuUkLWmKppFyPQ==',
                },
            ),
        ),
        'INSERT INTO cashbox_integration.cashboxes '
        'VALUES(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\','
        '       \'{}\',\'{}\',\'{}\',\'{}\',\'{}\')'.format(
            'park_123',
            'id_abc456',
            'idemp_100000',
            '2016-06-22 19:10:25-07',
            '2016-06-22 19:10:25-07',
            'deleted',
            False,
            'atol_online',
            json.dumps(
                {
                    'tin_pd_id': '0123456789_id',
                    'tax_scheme_type': 'simple',
                    'group_code': 'super_park_group',
                },
            ),
            json.dumps(
                {
                    'login': 'M5a7svvcrnA7E5axBDY2sw==',
                    'password': 'dCKumeJhRuUkLWmKppFyPQ==',
                },
            ),
        ),
        'INSERT INTO cashbox_integration.cashboxes '
        'VALUES(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\','
        '       \'{}\',\'{}\',\'{}\',\'{}\',\'{}\')'.format(
            'park_124',
            'id_abc123',
            'idemp_100500',
            '2016-06-22 19:10:25-07',
            '2016-06-22 19:10:25-07',
            'valid',
            True,
            'atol_online',
            json.dumps(
                {
                    'tin_pd_id': '0123456789_id',
                    'tax_scheme_type': 'simple',
                    'group_code': 'super_park_group',
                },
            ),
            json.dumps(
                {
                    'login': 'M5a7svvcrnA7E5axBDY2sw==',
                    'password': 'dCKumeJhRuUkLWmKppFyPQ==',
                },
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'park_id, expected_response, tin_retrieve_times_called',
    [
        (
            'park_123',
            {
                'cashboxes': [
                    {
                        'cashbox': {
                            'cashbox_type': 'atol_online',
                            'tax_identification_number': '0123456789',
                            'tax_scheme_type': 'simple',
                            'group_code': 'super_park_group',
                        },
                        'id': 'id_abc123',
                        'cashbox_state': 'valid',
                        'current': False,
                    },
                ],
            },
            1,
        ),
        (
            'park_124',
            {
                'cashboxes': [
                    {
                        'cashbox': {
                            'cashbox_type': 'atol_online',
                            'tax_identification_number': '0123456789',
                            'tax_scheme_type': 'simple',
                            'group_code': 'super_park_group',
                        },
                        'id': 'id_abc123',
                        'cashbox_state': 'valid',
                        'current': True,
                    },
                ],
            },
            1,
        ),
        ('park_456', {'cashboxes': []}, 0),
    ],
)
async def test_ok(
        taxi_cashbox_integration,
        pgsql,
        personal_tins_retrieve,
        park_id,
        expected_response,
        tin_retrieve_times_called,
):
    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        json={'query': {'park_id': park_id}},
        headers={'X-Ya-User-Ticket-Provider': 'yandex', 'X-Yandex-UID': '123'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == expected_response
    assert personal_tins_retrieve.times_called == tin_retrieve_times_called
