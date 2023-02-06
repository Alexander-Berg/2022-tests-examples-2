import pytest

YANDEX_UID = 'yandex_uid'

DADATA_SUGGEST_ITEM = {
    'value': 'ООО рогаИкопыта',
    'unrestricted_value': 'ООО рогаИкопыта',
    'data': {
        'hid': 'abc',
        'inn': '123',
        'kpp': '123',
        'ogrn': '123',
        'ogrn_date': 1469998800000,
        'type': 'LEGAL',
        'finance': {'tax_system': 'SRP'},
        'name': {
            'full': 'рогаИкопыта',
            'short': 'рогаИкопыта',
            'full_with_opf': (
                'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ ' 'рогаИкопыта'
            ),
            'short_with_opf': 'ООО рогаИкопыта',
        },
        'okved': '123',
        'okved_type': '2014',
        'address': None,
        'state': {
            'actuality_date': 1469998800000,
            'registration_date': 1469998800000,
            'status': 'ACTIVE',
            'liquidation_date': None,
        },
    },
}

DADATA_RESPONSE = {'suggestions': [DADATA_SUGGEST_ITEM]}


@pytest.mark.parametrize(
    'country, expected_dadata_calls, expected_json',
    [('rus', 1, DADATA_RESPONSE), ('blr', 0, {})],
)
async def test_dadata_suggest(
        taxi_cargo_crm,
        mockserver,
        country,
        expected_dadata_calls,
        expected_json,
):
    @mockserver.json_handler(
        '/dadata-suggestions/suggestions/api/4_1/rs/suggest/party',
    )
    def _handler(request):
        return mockserver.make_response(status=200, json=DADATA_RESPONSE)

    response = await taxi_cargo_crm.post(
        '/b2b/cargo-crm/flow/phoenix/helpers/company/suggest',
        json={'query': 'рогаИкопыта', 'country': country},
        headers={'X-Yandex-UID': YANDEX_UID},
    )

    assert response.status_code == 200
    # TODO (dipterix): will be ok after removing nullable options
    # assert response.json() == expected_json

    assert _handler.times_called == expected_dadata_calls
    if expected_dadata_calls:
        request_to_mock = _handler.next_call()['request']
        assert (
            request_to_mock.headers['Authorization'] == 'Token dadata-secret'
        )
        assert request_to_mock.json == {
            'count': 10,
            'query': 'рогаИкопыта',
            'status': ['ACTIVE'],
        }
