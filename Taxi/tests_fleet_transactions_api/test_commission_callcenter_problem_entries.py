import json

import pytest


ORDERS_ENDPOINT_URL = 'v1/parks/orders/transactions/list'
PARKS_ENDPOINT_URL = 'v1/parks/transactions/list'

JOURNAL_MOCK_URL = '/billing-reports/v2/journal/select'
BY_TAG_MOCK_URL = '/billing-reports/v2/journal/by_tag'

EVENT_AT_FROM = '2019-01-01T00:00:00+00:00'
EVENT_AT_TO = '2021-05-05T17:00:00+00:00'
PARK_ID = '7ad35b'
ORDER_ID = 'A001AA77'

ENTRIES_PARAMS = [
    # before min_event_at_of_correct_entry
    (11, '2019-03-22T22:00:00+00:00', 'cc', False),
    (11, '2019-03-22T22:00:00+00:00', 'other', True),
    (22, '2019-06-22T22:00:00+00:00', 'cc', False),
    (22, '2019-06-22T22:00:00+00:00', 'other', True),
    (33, '2019-09-22T22:00:00+00:00', 'cc', False),
    (33, '2019-09-22T22:00:00+00:00', 'other', True),
    (44, '2019-12-22T21:59:59+00:00', 'cc', False),
    (44, '2019-12-22T21:59:59+00:00', 'other', True),
    # between min_event_at_of_correct_entry and max_event_at_of_problem_entry
    (11, '2019-12-22T22:00:00+00:00', 'cc', False),
    (11, '2019-12-22T22:00:00+00:00', 'other', True),
    (55, '2019-12-22T22:00:00+00:00', 'cc', True),
    (22, '2019-12-31T17:00:00+00:00', 'cc', False),
    (22, '2019-12-31T17:00:00+00:00', 'other', True),
    (55, '2019-12-31T17:00:00+00:00', 'cc', True),
    (33, '2020-01-03T00:00:00+00:00', 'cc', True),
    (33, '2020-01-03T00:00:00+00:00', 'other', True),
    (55, '2020-01-03T00:00:00+00:00', 'cc', True),
    (44, '2020-01-11T11:00:00+00:00', 'cc', False),
    (44, '2020-01-11T11:00:00+00:00', 'other', True),
    (55, '2020-01-11T11:00:00+00:00', 'cc', True),
    # after max_event_at_of_problem_entry
    (11, '2020-01-11T11:00:01+00:00', 'cc', True),
    (11, '2020-01-11T11:00:01+00:00', 'other', True),
    (22, '2020-02-11T11:00:00+00:00', 'cc', True),
    (22, '2020-02-11T11:00:00+00:00', 'other', True),
    (33, '2020-03-11T11:00:00+00:00', 'cc', True),
    (33, '2020-03-11T11:00:00+00:00', 'other', True),
    (44, '2020-04-11T11:00:00+00:00', 'cc', True),
    (44, '2020-04-11T11:00:00+00:00', 'other', True),
]


def _make_entry(amount, entry_id, event_at, category):
    (agreement_id, sub_account) = (
        ('taxi/yandex_ride', 'commission/callcenter')
        if category == 'cc'
        else ('taxi/park_services', 'arbitrary/other')
    )
    return {
        'account': {
            'currency': 'RUB',
            'account_id': 123,
            'agreement_id': agreement_id,
            'sub_account': sub_account,
            'entity_external_id': f'taximeter_park_id/{PARK_ID}',
        },
        'amount': amount,
        'created': event_at,
        'details': {'alias_id': ORDER_ID},
        'doc': None,
        'doc_ref': f'doc-{entry_id}',
        'entry_id': entry_id,
        'event_at': event_at,
        'reason': '',
    }


def _filter_entries_params(category_ids=None):
    return [
        entry_params
        for entry_params in ENTRIES_PARAMS
        if category_ids is None or entry_params[2] in category_ids
    ]


def _make_transaction(amount, entry_id, event_at, category_id):
    return {
        'amount': amount,
        'category_id': category_id,
        'category_name': category_id,
        'created_by': {'identity': 'platform'},
        'currency_code': 'RUB',
        'description': '',
        'event_at': event_at,
        'id': f'{entry_id}',
        'order_id': ORDER_ID,
    }


def _make_transactions(category_ids=None):
    return [
        _make_transaction(f'-{index+1}', *entry[:3])
        for index, entry in enumerate(_filter_entries_params(category_ids))
        if entry[3]
    ]


async def test_orders(
        taxi_fleet_transactions_api,
        mockserver,
        driver_orders,
        mock_fleet_parks_list,
):
    def _make_orders_request():
        return {
            'query': {'park': {'id': PARK_ID, 'order': {'ids': [ORDER_ID]}}},
        }

    @mockserver.json_handler(BY_TAG_MOCK_URL)
    async def _by_tag_mock(request):
        return {
            'entries': {
                f'taxi/alias_id/{ORDER_ID}': [
                    _make_entry(f'-{index+1}', *entry[:3])
                    for index, entry in enumerate(ENTRIES_PARAMS)
                ],
            },
        }

    response = await taxi_fleet_transactions_api.post(
        ORDERS_ENDPOINT_URL, json=_make_orders_request(),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'transactions': _make_transactions()}


def _make_parks_request(event_at_from, category_ids):
    return {
        'limit': 1000,
        'query': {
            'park': {
                'id': PARK_ID,
                'transaction': {
                    **({'category_ids': category_ids} if category_ids else {}),
                    'event_at': {'from': event_at_from, 'to': EVENT_AT_TO},
                },
            },
        },
    }


def _make_parks_response(category_ids):
    return {
        'cursor': '',
        'limit': 1000,
        'transactions': _make_transactions(category_ids),
    }


CC_ACCOUNT = ('taxi/yandex_ride', 'commission/callcenter')
OTHER_ACCOUNT = ('taxi/park_services', 'arbitrary/other')
PARKS_PARAMS = [
    # before min_event_at_of_correct_entry
    ('2019-12-22T21:59:59+00:00', None, [CC_ACCOUNT, OTHER_ACCOUNT]),
    ('2019-12-22T21:59:59+00:00', ['other'], [OTHER_ACCOUNT]),
    # between min_event_at_of_correct_entry and max_event_at_of_problem_entry
    ('2019-12-22T22:00:00+00:00', None, [CC_ACCOUNT, OTHER_ACCOUNT]),
    ('2019-12-22T22:00:00+00:00', ['other'], [OTHER_ACCOUNT]),
    ('2020-01-01T00:00:00+00:00', None, [CC_ACCOUNT, OTHER_ACCOUNT]),
    ('2020-01-01T00:00:00+00:00', ['other'], [OTHER_ACCOUNT]),
    ('2020-01-11T11:00:00+00:00', None, [CC_ACCOUNT, OTHER_ACCOUNT]),
    ('2020-01-11T11:00:00+00:00', ['other'], [OTHER_ACCOUNT]),
    # after max_event_at_of_problem_entry
    ('2020-01-11T11:00:01+00:00', None, [CC_ACCOUNT, OTHER_ACCOUNT]),
    ('2020-01-11T11:00:01+00:00', ['other'], [OTHER_ACCOUNT]),
]


@pytest.mark.pgsql('fleet_transactions_api', files=[])
@pytest.mark.parametrize('event_at_from, category_ids, accounts', PARKS_PARAMS)
async def test_parks(
        taxi_fleet_transactions_api,
        mockserver,
        driver_orders,
        mock_fleet_parks_list,
        event_at_from,
        category_ids,
        accounts,
):
    def _make_journal_request():
        return {
            'begin_time': event_at_from,
            'end_time': EVENT_AT_TO,
            'limit': 1000,
            'cursor': '',
            'exclude': {'zero_entries': True},
            'accounts': [
                {
                    'currency': 'RUB',
                    'agreement_id': agreement_id,
                    **({'sub_account': sub_account} if sub_account else {}),
                    'entity_external_id': f'taximeter_park_id/{PARK_ID}',
                }
                for (agreement_id, sub_account) in accounts
            ],
        }

    def _make_entries(category_ids):
        return [
            _make_entry(f'-{index+1}', *entry[:3])
            for index, entry in enumerate(_filter_entries_params(category_ids))
        ]

    @mockserver.json_handler(JOURNAL_MOCK_URL)
    async def _journal_mock(request):
        request.get_data()
        return {'entries': _make_entries(category_ids)}

    response = await taxi_fleet_transactions_api.post(
        PARKS_ENDPOINT_URL,
        json=_make_parks_request(event_at_from, category_ids),
    )

    assert response.status_code == 200, response.text
    assert response.json() == _make_parks_response(category_ids)

    assert _journal_mock.times_called == 1
    journal_request = _journal_mock.next_call()['request']
    assert json.loads(journal_request.get_data()) == _make_journal_request()
