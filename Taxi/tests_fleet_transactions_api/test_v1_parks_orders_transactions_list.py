# encoding=utf-8
import json

import pytest


ENDPOINT_URL = 'v1/parks/orders/transactions/list'
ANTIFRAUD_ENDPOINT_URL = '/v1/parks/orders/transactions/with-antifraud/list'
MOCK_URL = '/billing-reports/v2/journal/by_tag'
MOCK_NOW = '2019-09-19T14:03:00+00:00'
BILLING_DEFAULT_BEGIN_TIME = '2000-01-01T00:00:00+00:00'

ENDPOINT_URLS_WITH_PREFIX = [
    (ENDPOINT_URL, ''),
    (ANTIFRAUD_ENDPOINT_URL, 'antifraud_'),
]
ENDPOINT_URLS = [endpoint[0] for endpoint in ENDPOINT_URLS_WITH_PREFIX]


def make_billing_request_time(event_at_from, event_at_to):
    # comparison as string is valid because of UTC timezone
    return {
        'begin_time': max(event_at_from or '', BILLING_DEFAULT_BEGIN_TIME),
        'end_time': min(event_at_to or MOCK_NOW, MOCK_NOW),
    }


EVENT_AT_FROM_PARAMS = (
    None,
    '1991-08-21T05:34:00+00:00',
    '2019-07-21T05:34:00+00:00',
)
EVENT_AT_TO_PARAMS = (
    None,
    '2021-08-21T05:34:00+00:00',
    '2019-08-21T05:34:00+00:00',
)


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize('event_at_from', EVENT_AT_FROM_PARAMS)
@pytest.mark.parametrize('event_at_to', EVENT_AT_TO_PARAMS)
@pytest.mark.parametrize('endpoint,static_prefix', ENDPOINT_URLS_WITH_PREFIX)
async def test_ok(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        driver_orders,
        mock_fleet_parks_list,
        event_at_from,
        event_at_to,
        endpoint,
        static_prefix,
):
    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_reports(request):
        request.get_data()
        return load_json(static_prefix + 'ok_billing_response.json')

    ok_request = load_json('ok_request.json')
    ok_request['query']['park']['transaction'] = {
        'event_at': {
            **({'from': event_at_from} if event_at_from is not None else {}),
            **({'to': event_at_to} if event_at_to is not None else {}),
        },
    }

    response = await taxi_fleet_transactions_api.post(
        endpoint, headers={'Accept-Language': 'ru'}, json=ok_request,
    )

    assert response.status_code == 200, response.text
    assert response.json() == load_json(static_prefix + 'ok_response.json')

    assert mock_billing_reports.times_called == 1
    billing_request = mock_billing_reports.next_call()['request']
    assert billing_request.method == 'POST'
    # todo - uncomment when tvm2_client mock is OK
    # assert billing_request.headers.get('X-Ya-Service-Ticket') is not None
    assert json.loads(billing_request.get_data()) == {
        **load_json(static_prefix + 'ok_billing_request.json'),
        **make_billing_request_time(event_at_from, event_at_to),
    }


PAST_OR_FUTURE_EVENT_AT_PARAMS = [
    ('1994-01-01T10:50:00+03:00', '1999-12-31T23:59:59+00:00'),  # past
    ('2019-09-19T14:03:01+03:00', '2021-09-19T14:03:01+03:00'),  # future
]


@pytest.mark.parametrize('endpoint', ENDPOINT_URLS)
async def test_duplicates_in_order_ids(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        mock_fleet_parks_list,
        endpoint,
):
    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_reports(request):
        request.get_data()
        return {}

    bad_request = load_json('ok_request.json')
    bad_request['query']['park']['order']['ids'] = ['abcdef', 'abcdef']

    response = await taxi_fleet_transactions_api.post(
        endpoint, json=bad_request,
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': '400',
        'message': 'field `query.park.order.ids` must contain unique values',
    }

    assert mock_billing_reports.times_called == 0


@pytest.mark.now('2019-09-19T14:03:00+0300')
@pytest.mark.parametrize(
    'event_at_from,event_at_to', PAST_OR_FUTURE_EVENT_AT_PARAMS,
)
@pytest.mark.parametrize('endpoint,static_prefix', ENDPOINT_URLS_WITH_PREFIX)
async def test_past_or_future_event_at(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        mock_fleet_parks_list,
        driver_orders,
        event_at_from,
        event_at_to,
        endpoint,
        static_prefix,
):
    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_reports(request):
        request.get_data()
        return {}

    ok_request = load_json('ok_request.json')
    ok_request['query']['park']['transaction'] = {
        'event_at': {'from': event_at_from, 'to': event_at_to},
    }

    response = await taxi_fleet_transactions_api.post(
        endpoint, json=ok_request,
    )

    assert response.status_code == 200, response.text
    assert response.json() == load_json(static_prefix + 'empty_response.json')

    assert mock_billing_reports.times_called == 0


@pytest.mark.parametrize('endpoint', ENDPOINT_URLS)
async def test_incorrect_event_at(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        mock_fleet_parks_list,
        endpoint,
):
    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_reports(request):
        request.get_data()
        return {}

    ok_request = load_json('ok_request.json')
    ok_request['query']['park']['transaction'] = {
        'event_at': {
            'from': '2019-08-01T02:00:00+00:00',
            'to': '2019-08-01T01:00:00+00:00',
        },
    }

    response = await taxi_fleet_transactions_api.post(
        endpoint, json=ok_request,
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': '400',
        'message': (
            'field `query.park.transaction.event_at`'
            ' must contain a non-empty time interval'
        ),
    }

    assert mock_billing_reports.times_called == 0


@pytest.mark.config(FLEET_TRANSACTIONS_API_GROUPS=[])
async def test_incorrect_config(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        mock_fleet_parks_list,
):
    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_reports(request):
        request.get_data()
        return {}

    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL, json=load_json('ok_request.json'),
    )

    assert response.status_code == 500, response.text
    assert mock_billing_reports.times_called == 0


@pytest.mark.parametrize('endpoint', ENDPOINT_URLS)
async def test_status_code_429(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        driver_orders,
        mock_fleet_parks_list,
        endpoint,
):
    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_reports(request):
        return mockserver.make_response(status=429)

    response = await taxi_fleet_transactions_api.post(
        endpoint,
        headers={'Accept-Language': 'ru'},
        json=load_json('ok_request.json'),
    )

    assert response.status_code == 429, response.text
    assert mock_billing_reports.has_calls


@pytest.mark.parametrize('endpoint', ENDPOINT_URLS)
async def test_chunks(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        driver_orders,
        mock_fleet_parks_list,
        endpoint,
):
    order_ids = [f'id{id}' for id in range(1, 26)]

    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_reports(request):
        tags = request.json['tags']
        assert len(tags) <= 10
        for tag in tags:
            tag_prefix = 'taxi/alias_id/'
            assert tag.startswith(tag_prefix), tag
            order_id = tag[len(tag_prefix) :]
            assert order_id in order_ids
            order_ids.remove(order_id)

        return {'entries': {}}

    request_json = load_json('ok_request.json')
    request_json['query']['park']['order']['ids'] = order_ids

    await taxi_fleet_transactions_api.post(
        endpoint, headers={'Accept-Language': 'ru'}, json=request_json,
    )

    assert mock_billing_reports.has_calls
    assert not order_ids
