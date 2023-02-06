# encoding=utf-8
import base64
import json

import pytest


PARKS_ENDPOINT_URL = 'v1/parks/transactions/list'
DRIVER_PROFILES_ENDPOINT_URL = 'v1/parks/driver-profiles/transactions/list'
ENDPOINT_URLS = [
    (PARKS_ENDPOINT_URL, 'parks_'),
    (DRIVER_PROFILES_ENDPOINT_URL, 'driver_profiles_'),
]
MOCK_URL = '/billing-reports/v2/journal/select'


@pytest.mark.parametrize('endpoint,static_prefix', ENDPOINT_URLS)
async def test_ok(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        driver_orders,
        mock_fleet_parks_list,
        endpoint,
        static_prefix,
):
    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_reports(request):
        request.get_data()
        return load_json(static_prefix + 'ok_billing_response.json')

    response = await taxi_fleet_transactions_api.post(
        endpoint, json=load_json(static_prefix + 'ok_request.json'),
    )

    assert response.status_code == 200, response.text
    assert response.json() == load_json(static_prefix + 'ok_response.json')

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert mock_billing_reports.times_called == 1
    billing_request = mock_billing_reports.next_call()['request']
    assert billing_request.method == 'POST'
    assert json.loads(billing_request.get_data()) == load_json(
        static_prefix + 'ok_billing_request.json',
    )


@pytest.mark.parametrize('endpoint,static_prefix', ENDPOINT_URLS)
@pytest.mark.parametrize('is_affecting', [False, True])
async def test_is_affecting_driver_balance(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        driver_orders,
        mock_fleet_parks_list,
        endpoint,
        static_prefix,
        is_affecting,
):
    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_reports(request):
        request.get_data()
        return load_json('billing_response.json')

    request_json = load_json('service_request.json')
    query = request_json['query']['park']['transaction']
    query['is_affecting_driver_balance'] = is_affecting
    response = await taxi_fleet_transactions_api.post(
        endpoint, json=request_json,
    )

    assert response.status_code == 200, response.text
    assert response.json() == load_json('service_response.json')

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert mock_billing_reports.times_called == 1
    billing_request = mock_billing_reports.next_call()['request']
    assert billing_request.method == 'POST'
    assert json.loads(billing_request.get_data()) == load_json(
        f'{static_prefix}{str(is_affecting).lower()}_billing_request.json',
    )


@pytest.mark.parametrize('endpoint,static_prefix', ENDPOINT_URLS)
@pytest.mark.parametrize(
    'cursor_encoded,cursor,mock_url',
    [
        ('Y3Vyc29y', 'cursor', MOCK_URL),
        (
            'ewogICAgInBnL3RheGltZXRlcl9kcml2ZXJfaWQvN2FkMzVi'
            'LzljNWUzNS90YXhpL3BhcmtfcmlkZS9SVUIiOiAiIgp9',
            {'pg/taximeter_driver_id/7ad35b/9c5e35/taxi/park_ride/RUB': ''},
            '/billing-reports/v1/journal/select',
        ),
    ],
)
async def test_parse_cursor(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        driver_orders,
        mock_fleet_parks_list,
        endpoint,
        static_prefix,
        cursor_encoded,
        cursor,
        mock_url,
):
    @mockserver.json_handler(mock_url)
    async def mock_billing_reports(request):
        request.get_data()
        response = load_json(static_prefix + 'ok_billing_response.json')
        if 'v1' in mock_url:
            response['cursor'] = {}
        return response

    response = await taxi_fleet_transactions_api.post(
        endpoint,
        json={
            **load_json(static_prefix + 'ok_request.json'),
            'cursor': cursor_encoded,
        },
    )

    assert response.status_code == 200, response.text

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert mock_billing_reports.times_called == 1
    billing_request = mock_billing_reports.next_call()['request']
    assert billing_request.method == 'POST'
    assert json.loads(billing_request.get_data()) == {
        **load_json(static_prefix + 'ok_billing_request.json'),
        'cursor': cursor,
    }


@pytest.mark.parametrize('endpoint,static_prefix', ENDPOINT_URLS)
@pytest.mark.parametrize('cursor', ['', '$%@?'])
async def test_invalid_cursor(
        taxi_fleet_transactions_api,
        load_json,
        endpoint,
        static_prefix,
        cursor,
):
    response = await taxi_fleet_transactions_api.post(
        endpoint,
        json={
            **load_json(static_prefix + 'ok_request.json'),
            **{'cursor': cursor},
        },
    )

    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': 'invalid cursor'}


@pytest.mark.parametrize('endpoint,static_prefix', ENDPOINT_URLS)
async def test_park_not_found(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        mock_fleet_parks_list,
        endpoint,
        static_prefix,
):
    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_reports(request):
        request.get_data()
        return {}

    ok_request = load_json(static_prefix + 'ok_request.json')
    ok_request['query']['park']['id'] = 'nonexistent'
    response = await taxi_fleet_transactions_api.post(
        endpoint, json=ok_request,
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': '400',
        'message': 'park with id `nonexistent` not found',
    }

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert mock_billing_reports.times_called == 0


BAD_EVENT_AT_MESSAGE = (
    'field `query.park.transaction.event_at`'
    ' must contain a non-empty time interval'
)
BAD_FILTER_MESSAGE = (
    'at most one field of `query.park.transaction.category_ids`, '
    '`query.park.transaction.group_ids` and '
    '`query.park.transaction.is_affecting_driver_balance` allowed'
)
GOOD_EVENT_AT = {
    'from': '2020-04-01T00:00:00+00:00',
    'to': '2020-04-02T00:00:00+00:00',
}
BAD_PARAMS = [
    (
        {
            'event_at': {
                'from': '2020-04-02T14:33:00+03:00',
                'to': '2020-04-02T14:33:00+03:00',
            },
        },
        BAD_EVENT_AT_MESSAGE,
    ),
    (
        {
            'event_at': {
                'from': '2020-04-02T14:34:00+03:00',
                'to': '2020-04-01T14:33:00+03:00',
            },
        },
        BAD_EVENT_AT_MESSAGE,
    ),
    (
        {
            'event_at': GOOD_EVENT_AT,
            'category_ids': ['cash_collected'],
            'group_ids': ['cash_collected'],
        },
        BAD_FILTER_MESSAGE,
    ),
    (
        {
            'event_at': GOOD_EVENT_AT,
            'category_ids': ['cash_collected'],
            'is_affecting_driver_balance': False,
        },
        BAD_FILTER_MESSAGE,
    ),
    (
        {
            'event_at': GOOD_EVENT_AT,
            'category_ids': ['cash_collected'],
            'group_ids': ['cash_collected'],
            'is_affecting_driver_balance': False,
        },
        BAD_FILTER_MESSAGE,
    ),
    (
        {
            'event_at': GOOD_EVENT_AT,
            'group_ids': ['cash_collected'],
            'is_affecting_driver_balance': False,
        },
        BAD_FILTER_MESSAGE,
    ),
]


@pytest.mark.parametrize('endpoint,static_prefix', ENDPOINT_URLS)
@pytest.mark.parametrize('query_park_transaction, message', BAD_PARAMS)
async def test_bad_request(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        mock_fleet_parks_list,
        endpoint,
        static_prefix,
        query_park_transaction,
        message,
):
    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_reports(request):
        request.get_data()
        return {}

    request_json = load_json(static_prefix + 'ok_request.json')
    request_json['query']['park']['transaction'] = query_park_transaction

    response = await taxi_fleet_transactions_api.post(
        endpoint, json=request_json,
    )

    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': message}
    assert mock_fleet_parks_list.mock_parks_list.times_called == 0
    assert mock_billing_reports.times_called == 0


@pytest.mark.parametrize('endpoint,static_prefix', ENDPOINT_URLS)
@pytest.mark.parametrize(
    'park_id',
    ['godfather', 'avengers'],  # empty currency code  # country not found
)
async def test_no_currency_code(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        mock_fleet_parks_list,
        endpoint,
        static_prefix,
        park_id,
):
    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_reports(request):
        request.get_data()
        return {}

    ok_request = load_json(static_prefix + 'ok_request.json')
    ok_request['query']['park']['id'] = park_id
    response = await taxi_fleet_transactions_api.post(
        endpoint, json=ok_request,
    )

    assert response.status_code == 500, response.text

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert mock_billing_reports.times_called == 0


@pytest.mark.parametrize('endpoint,static_prefix', ENDPOINT_URLS)
@pytest.mark.config(FLEET_TRANSACTIONS_API_GROUPS=[])
async def test_incorrect_config(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        mock_fleet_parks_list,
        endpoint,
        static_prefix,
):
    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_reports(request):
        request.get_data()
        return {}

    response = await taxi_fleet_transactions_api.post(
        endpoint, json=load_json(static_prefix + 'ok_request.json'),
    )

    assert response.status_code == 500, response.text
    assert mock_billing_reports.times_called == 0


def make_list_request(limit):
    return {
        'query': {
            'park': {
                'id': '7ad35b',
                'transaction': {
                    'event_at': {
                        'from': '2018-05-08T12:00:00+03:00',
                        'to': '2020-07-30T12:00:00+03:00',
                    },
                },
            },
        },
        'limit': limit,
    }


def make_journal_select_entry(entry_id, sub_account):
    return (
        {
            'entry_id': entry_id,
            'account': {
                'account_id': 111,
                'entity_external_id': 'taximeter_park_id/7ad36b',
                'agreement_id': 'taxi/park_services',
                'currency': 'RUB',
                'sub_account': sub_account,
            },
            'amount': '1.0000',
            'doc_ref': '11111',
            'event_at': '2020-07-30T12:05:08.000000+00:00',
            'created': '2020-07-30T23:05:12.888869+00:00',
            'reason': '',
        },
        f'2020-07-30T12:05:08.000000+00:00/{entry_id}',
    )


def make_encoded_cursor(offset):
    return (
        base64.b64encode(str(offset).encode('ascii'))
        .decode('ascii')
        .rstrip('=')
    )


def _make_billing_cursor(transaction):
    i = transaction['event_at'].find('+')
    time = transaction['event_at'] = (
        transaction['event_at'][:i] + '.000000' + transaction['event_at'][i:]
    )
    return (
        base64.b64encode(
            '{}/{}'.format(time, transaction['id']).encode('ascii'),
        )
        .decode('ascii')
        .rstrip('=')
    )


@pytest.mark.parametrize(
    'entries_count, external_entries_indices,'
    ' limit, result_offset, billing_requests_count',
    [
        (13, [0, 4, 10], 3, 11, 3),
        (13, [0, 4, 10], 1, 1, 1),
        (5, [0, 2, 3], 2, 3, 1),
    ],
)
@pytest.mark.config(
    FLEET_TRANSACTIONS_API_GROUPS=[
        {
            'group_id': 'partner_other',
            'group_name_tanker_key': 'Ключ',
            'categories': [
                {
                    'category_id': f'target-{x}',
                    'category_name_tanker_key': 'Ключ',
                    'is_affecting_driver_balance': True,
                    'accounts': [
                        {
                            'agreement_id': 'taxi/park_services',
                            'sub_account': f'complex/{x}',
                        },
                    ],
                }
                for x in range(0, 33)
            ],
        },
    ],
)
async def test_complex_billing_request(
        taxi_fleet_transactions_api,
        mockserver,
        driver_orders,
        mock_fleet_parks_list,
        entries_count,
        external_entries_indices,
        limit,
        result_offset,
        billing_requests_count,
):
    entries = [
        make_journal_select_entry(
            4910440061 + 1000 * i,
            f'complex/{i}' if i in external_entries_indices else f'simple/{i}',
        )
        for i in range(0, entries_count)
    ]

    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_reports(request):
        request_json = json.loads(request.get_data())
        response_entries = [
            (e, c) for (e, c) in entries if c > request_json['cursor']
        ][: request_json['limit']]
        return {
            'entries': [e for (e, _) in response_entries],
            'cursor': response_entries[-1][1],
        }

    response = await taxi_fleet_transactions_api.post(
        PARKS_ENDPOINT_URL, json=make_list_request(limit),
    )

    assert response.status_code == 200, response.text
    response_json = response.json()
    print(response_json['transactions'])
    assert response_json['limit'] == limit
    assert response_json['cursor'] == _make_billing_cursor(
        response_json['transactions'][-1],
    )
    assert list(
        map(lambda x: x['category_id'], response_json['transactions']),
    ) == list(map(lambda x: f'target-{x}', external_entries_indices[0:limit]))

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert mock_billing_reports.times_called == billing_requests_count


@pytest.mark.config(FLEET_TRANSACTIONS_API_MAX_LIMIT_FOR_JOURNAL_SELECT=10)
async def test_max_limit_for_journal_select(
        taxi_fleet_transactions_api,
        mockserver,
        driver_orders,
        mock_fleet_parks_list,
):
    limit = 53

    def make_entry_id(index):
        return 1000 + 13 * index

    entries = [
        make_journal_select_entry(make_entry_id(i), 'arbitrary/other')
        for i in range(0, limit)
    ]

    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_reports(request):
        request_json = json.loads(request.get_data())
        response_entries = [
            (e, c) for (e, c) in entries if c > request_json['cursor']
        ][: request_json['limit']]
        return {
            'entries': [e for (e, _) in response_entries],
            'cursor': response_entries[-1][1],
        }

    response = await taxi_fleet_transactions_api.post(
        PARKS_ENDPOINT_URL, json=make_list_request(53),
    )

    assert response.status_code == 200, response.text
    response_json = response.json()

    assert response_json['limit'] == limit
    assert response_json['cursor'] == _make_billing_cursor(
        response_json['transactions'][-1],
    )
    assert list(map(lambda x: x['id'], response_json['transactions'])) == [
        str(make_entry_id(i)) for i in range(0, limit)
    ]

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert mock_billing_reports.times_called == 6


@pytest.mark.parametrize(
    'folder_name', ['localization', 'categories', 'groups', 'uber'],
)
@pytest.mark.config(
    LOCALES_APPLICATION_TYPE_OVERRIDES={
        'uberdriver': {
            'issue_managers': [],
            'stop_words': [],
            'supported_languages': [],
            'override_keysets': {
                'taximeter_backend_api_controllers': 'override_uberdriver',
            },
        },
    },
)
async def test_extensions(
        taxi_fleet_transactions_api,
        mockserver,
        driver_orders,
        mock_fleet_parks_list,
        load_json,
        taxi_config,
        folder_name,
):
    taxi_config.set_values(load_json(f'{folder_name}/config.json'))

    if folder_name == 'uber':
        parks_json = load_json('parks.json')
        parks_json[0]['fleet_type'] = 'uberdriver'
        mock_fleet_parks_list.set_parks(parks_json)

    @mockserver.json_handler(MOCK_URL)
    async def _mock_billing_reports(request):
        return load_json(f'{folder_name}/billing_response.json')

    response = await taxi_fleet_transactions_api.post(
        DRIVER_PROFILES_ENDPOINT_URL,
        headers={'Accept-Language': 'ru'},
        json=load_json(f'{folder_name}/service_request.json'),
    )

    response_json = response.json()
    assert response_json == load_json(f'{folder_name}/service_response.json')


async def test_change_config(
        taxi_fleet_transactions_api,
        mockserver,
        driver_orders,
        mock_fleet_parks_list,
        load_json,
        taxi_config,
):
    taxi_config.set_values(load_json('change_config/config_0.json'))

    @mockserver.json_handler(MOCK_URL)
    async def _mock_billing_reports_1(request):
        request.get_data()
        return load_json('change_config/billing_response.json')

    response = await taxi_fleet_transactions_api.post(
        DRIVER_PROFILES_ENDPOINT_URL,
        headers={'Accept-Language': 'ru'},
        json=load_json('change_config/service_request.json'),
    )

    assert response.json() == load_json('change_config/service_response.json')
    mock_request_1 = _mock_billing_reports_1.next_call()['request']
    assert len(json.loads(mock_request_1.get_data()).get('accounts', [])) == 1

    # add another (agreement_id, sub_account) pair
    taxi_config.set_values(load_json('change_config/config_1.json'))
    await taxi_fleet_transactions_api.invalidate_caches()

    @mockserver.json_handler(MOCK_URL)
    async def _mock_billing_reports_2(request):
        request.get_data()
        return load_json('change_config/billing_response.json')

    response = await taxi_fleet_transactions_api.post(
        DRIVER_PROFILES_ENDPOINT_URL,
        headers={'Accept-Language': 'ru'},
        json=load_json('change_config/service_request.json'),
    )

    assert response.json() == load_json('change_config/service_response.json')
    mock_request_2 = _mock_billing_reports_2.next_call()['request']
    assert len(json.loads(mock_request_2.get_data()).get('accounts', [])) == 2


async def test_driver_orders_timeout(
        taxi_fleet_transactions_api,
        mockserver,
        mock_fleet_parks_list,
        load_json,
):
    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    async def _mock_driver_orders(request):
        request.get_data()
        raise mockserver.TimeoutError()

    @mockserver.json_handler(MOCK_URL)
    async def _mock_billing_reports(request):
        request.get_data()
        return load_json('driver_orders_timeout/billing_response.json')

    response = await taxi_fleet_transactions_api.post(
        DRIVER_PROFILES_ENDPOINT_URL,
        json=load_json('driver_orders_timeout/ok_request.json'),
    )

    response_json = response.json()
    assert response_json == load_json('driver_orders_timeout/ok_response.json')


async def test_complex_with_filter(
        taxi_fleet_transactions_api,
        mockserver,
        driver_orders,
        mock_fleet_parks_list,
        load_json,
        taxi_config,
):
    taxi_config.set_values(load_json('complex_with_filter/config.json'))

    @mockserver.json_handler(MOCK_URL)
    async def _mock_billing_reports(request):
        return load_json(f'complex_with_filter/billing_response.json')

    response = await taxi_fleet_transactions_api.post(
        DRIVER_PROFILES_ENDPOINT_URL,
        headers={'Accept-Language': 'ru'},
        json=load_json('complex_with_filter/service_request.json'),
    )

    assert response.status_code == 200, response.text
    assert response.json() == load_json(
        f'complex_with_filter/service_response.json',
    )


@pytest.mark.parametrize('category_desc', [None, 'A'])
@pytest.mark.parametrize('category_desc_neg', [None, 'B'])
@pytest.mark.parametrize('account_desc', [None, 'C'])
@pytest.mark.parametrize('account_desc_neg', [None, 'D'])
async def test_transaction_description_if_negative(
        taxi_fleet_transactions_api,
        mockserver,
        mock_fleet_parks_list,
        load_json,
        taxi_config,
        category_desc,
        category_desc_neg,
        account_desc,
        account_desc_neg,
):
    def _make_update_obj(desc, desc_neg):
        def _make_obj(name, value):
            return {name: f'just_{value}'} if value else {}

        return {
            **_make_obj('transaction_description_tanker_key', desc),
            **_make_obj(
                'transaction_description_tanker_key_if_negative', desc_neg,
            ),
        }

    folder_name = 'transaction_description_if_negative'
    config = load_json(f'{folder_name}/config.json')
    category = config['FLEET_TRANSACTIONS_API_GROUPS'][0]['categories'][0]
    account = category['accounts'][0]

    category.update(_make_update_obj(category_desc, category_desc_neg))
    account.update(_make_update_obj(account_desc, account_desc_neg))

    taxi_config.set_values(config)

    @mockserver.json_handler(MOCK_URL)
    async def _mock_billing_reports(request):
        return load_json(f'{folder_name}/billing_response.json')

    response = await taxi_fleet_transactions_api.post(
        DRIVER_PROFILES_ENDPOINT_URL,
        headers={'Accept-Language': 'ru'},
        json=load_json(f'{folder_name}/service_request.json'),
    )

    expected_response_json = load_json(f'{folder_name}/service_response.json')
    for transaction in expected_response_json['transactions']:
        desc = account_desc or category_desc

        if float(transaction['amount']) < 0:
            desc = account_desc_neg or category_desc_neg or desc

        if desc:
            transaction['description'] = desc

    assert response.status_code == 200, response.text
    assert response.json() == expected_response_json


@pytest.mark.parametrize('endpoint, static_prefix', ENDPOINT_URLS)
async def test_status_code_429(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        driver_orders,
        mock_fleet_parks_list,
        endpoint,
        static_prefix,
):
    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_reports(request):
        return mockserver.make_response(status=429)

    response = await taxi_fleet_transactions_api.post(
        endpoint, json=load_json(static_prefix + 'ok_request.json'),
    )

    assert response.status_code == 429, response.text
    assert mock_billing_reports.has_calls


@pytest.mark.pgsql('fleet_transactions_api', files=[])
async def test_optimal_query(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        mock_fleet_parks_list,
):
    @mockserver.json_handler(MOCK_URL)
    async def _mock_billing_reports(request):
        assert request.json == load_json('billing_request.json')
        return load_json('billing_response.json')

    response = await taxi_fleet_transactions_api.post(
        PARKS_ENDPOINT_URL, json=load_json('request.json'),
    )

    assert response.status_code == 200, response.text
    assert _mock_billing_reports.has_calls


@pytest.mark.pgsql('fleet_transactions_api', files=[])
async def test_optimal_query_with_empty_excludes(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        mock_fleet_parks_list,
):
    @mockserver.json_handler(MOCK_URL)
    async def _mock_billing_reports(request):
        assert request.json == load_json('billing_request.json')
        return load_json('billing_response.json')

    response = await taxi_fleet_transactions_api.post(
        DRIVER_PROFILES_ENDPOINT_URL, json=load_json('request.json'),
    )

    assert response.status_code == 200, response.text
    assert _mock_billing_reports.has_calls
