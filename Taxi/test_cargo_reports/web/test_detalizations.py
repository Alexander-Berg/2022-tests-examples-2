import pytest

CORP_CLIENT_ID = '00144b4a9ec44ca383ae3ed8ec4a230d'
CONTRACT_EIDS = ['12345/12', '123456/12']
YT_TABLE_PATH = (
    '//home/unittests/unittests/services/cargo-tasks/detalizations/2021-12'
)

FIELD_NAMES = [
    'contract_eid',
    'order_id',
    'claim_id',
    'city',
    'status',
    'created_date',
    'source_point_address',
    'dest_point_address',
    'tariff',
    'external_order_id',
    'vat_price',
    'no_vat_price',
]

CONTRACTS_RESPONSE = {
    'contracts': [
        {
            'contract_id': 0,
            'external_id': CONTRACT_EIDS[0],
            'billing_client_id': '12345',
            'billing_person_id': '54321',
            'payment_type': 'postpaid',
            'is_offer': False,
            'currency': 'RUB',
            'services': ['cargo'],
        },
        {
            'contract_id': 1,
            'external_id': CONTRACT_EIDS[1],
            'billing_client_id': '12345',
            'billing_person_id': '54321',
            'payment_type': 'postpaid',
            'is_offer': False,
            'currency': 'RUB',
            'services': ['cargo'],
        },
    ],
}


@pytest.mark.config(
    CARGO_REPORTS_ACTS_DETALIZATIONS_SETTINGS={
        'field_names': FIELD_NAMES,
        'chunk_size': 10000,
    },
)
async def test_detalizations_ok(
        taxi_cargo_reports_web, yt_apply, yt_client, load_json, mockserver,
):
    @mockserver.json_handler('/corp-clients/v1/contracts')
    def _get_contracts_handler(request):
        assert request.query['client_id'] == CORP_CLIENT_ID
        return mockserver.make_response(status=200, json=CONTRACTS_RESPONSE)

    # tables prepare
    table_schema = load_json('schema.json')
    table_data = load_json('table_data.json')
    yt_client.create_table(
        YT_TABLE_PATH,
        recursive=True,
        attributes={
            'dynamic': False,
            'optimize_for': 'scan',
            'schema': table_schema,
        },
    )
    yt_client.write_table(YT_TABLE_PATH, table_data)

    # request with contract_eids
    response = await taxi_cargo_reports_web.post(
        'v1/act-detalizations',
        headers={
            'X-B2B-Client-Id': CORP_CLIENT_ID,
            'X-Yandex-Login': 'me',
            'X-Yandex-Uid': '05780',
            'Accept-Language': 'en',
        },
        params={'month': '2021-12', 'contract_eids': ','.join(CONTRACT_EIDS)},
    )

    assert response.status == 200
    result = await response.text()
    expected = ''.join(
        [
            '\ufeff' + '\t'.join(FIELD_NAMES) + '\r\n',
            *_get_expected_rows(table_data),
        ],
    )
    assert result == expected
    assert _get_contracts_handler.times_called == 0

    # request without contract_eids
    response = await taxi_cargo_reports_web.post(
        'v1/act-detalizations',
        headers={
            'X-B2B-Client-Id': CORP_CLIENT_ID,
            'X-Yandex-Login': 'me',
            'X-Yandex-Uid': '05780',
            'Accept-Language': 'en',
        },
        params={'month': '2021-12'},
    )

    assert response.status == 200
    result = await response.text()
    assert result == expected
    assert _get_contracts_handler.times_called == 1


@pytest.mark.config(
    CARGO_REPORTS_ACTS_DETALIZATIONS_SETTINGS={
        'field_names': FIELD_NAMES,
        'chunk_size': 10000,
    },
)
async def test_detalizations_detail_missing(taxi_cargo_reports_web):

    _eids = ['12347/12', '123458/12']

    response = await taxi_cargo_reports_web.post(
        'v1/act-detalizations',
        headers={
            'X-B2B-Client-Id': CORP_CLIENT_ID,
            'X-Yandex-Login': 'me',
            'X-Yandex-Uid': '05780',
            'Accept-Language': 'en',
        },
        params={'month': '2021-12', 'contract_eids': ','.join(_eids)},
    )

    assert response.status == 404
    result = await response.json()
    assert result == {
        'code': 'detail_missing',
        'message': 'Detail missing. Contact the manager.',
    }


@pytest.mark.config(
    CARGO_REPORTS_ACTS_DETALIZATIONS_SETTINGS={
        'field_names': FIELD_NAMES,
        'chunk_size': 10000,
    },
)
async def test_detalizations_bad(
        taxi_cargo_reports_web, yt_apply, yt_client, load_json, mockserver,
):
    # no table with detalizations
    response = await taxi_cargo_reports_web.post(
        'v1/act-detalizations',
        headers={
            'X-B2B-Client-Id': CORP_CLIENT_ID,
            'X-Yandex-Login': 'me',
            'X-Yandex-Uid': '05780',
            'Accept-Language': 'en',
        },
        params={'month': '2021-11', 'contract_eids': ','.join(CONTRACT_EIDS)},
    )

    assert response.status == 404
    response_json = await response.json()
    assert response_json == {
        'code': 'not_found',
        'message': 'Act detalizations not found',
    }


def _get_expected_rows(table_data):
    return [
        '\t'.join(
            [str(row.get(field_name) or '') for field_name in FIELD_NAMES],
        )
        + '\r\n'
        for row in table_data
        if row['contract_eid'] in CONTRACT_EIDS
    ]
