import collections
import datetime

import pytest

from . import utils


PERIODIC_NAME = 'cargo-journal-reader'
POLLING_DELAY_MS = 10
POLLING_DELAY_HEADER = 'X-Polling-Delay-Ms'
RESPONSE_HEADERS = {POLLING_DELAY_HEADER: str(POLLING_DELAY_MS)}
OK_CORP_CLIENTS = (
    utils.MAGNIT_CORP_CLIENT,
    utils.RETAIL_CORP_CLIENT,
    utils.BELARUS_CORP_CLIENT,
    utils.KAZAKHSTAN_CORP_CLIENT,
    utils.EDA_CORP_CLIENT,
)

DUPLICATED_CORP_CLIENTS = ('retail_new',)


@utils.eats_eta_settings_config3()
@pytest.mark.parametrize('corp_client', OK_CORP_CLIENTS)
@pytest.mark.parametrize('events_count', [1, 10])
@pytest.mark.parametrize('initial_cursor', [None, '0'])
@pytest.mark.parametrize('response_cursor', ['1', 'a'])
async def test_cargo_journal_reader_ok(
        stq_runner,
        stq,
        mockserver,
        now_utc,
        make_order,
        get_cargo_journal_cursor,
        create_cargo_journal_cursor,
        db_insert_order,
        db_select_orders,
        claim_statuses_list,
        corp_client,
        initial_cursor,
        response_cursor,
        events_count,
        now,
):
    claim_orders_count = 2
    corp_client_claims_count = 2
    claims_info = collections.defaultdict(dict)
    orders = []
    create_cargo_journal_cursor(corp_client, initial_cursor)
    for claim_idx in range(corp_client_claims_count):
        claim_id = f'claim-{corp_client}-{claim_idx}'
        claims_info[claim_id]['claim_status'] = claim_statuses_list[0]
        for order_idx in range(claim_orders_count):
            order = make_order(
                order_nr=f'order_{corp_client}_{claim_idx}_{order_idx}',
                delivery_type='native',
                claim_id=claim_id,
                claim_status=claim_statuses_list[0],
                place_point_id=order_idx,
                customer_point_id=order_idx + claim_orders_count,
                place_visit_order=order_idx,
                customer_visit_order=order_idx + claim_orders_count,
            )
            del order['id']
            order['id'] = db_insert_order(order)
            orders.append(order)
    events = [
        {'claim_id': claim_id, 'new_status': status}
        for claim_id in claims_info
        for status in claim_statuses_list
    ][:events_count]
    for i, event in enumerate(events):
        event['updated_ts'] = utils.to_string(
            now_utc - datetime.timedelta(seconds=len(events) - i),
        )

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/journal',
    )
    def mock_cargo_journal(request):
        auth_header = request.headers['Authorization']
        request_corp_client = utils.CARGO_AUTH_HEADER_TO_CORP_CLIENT[
            auth_header
        ]
        assert request_corp_client == corp_client
        for event in events:
            claim_info = claims_info[event['claim_id']]
            claim_info['claim_status'] = event['new_status']
            if event['new_status'] == 'pickup_arrived':
                claim_info['pickup_arrived_at'] = utils.parse_datetime(
                    event['updated_ts'],
                )
            elif event['new_status'] == 'delivery_arrived':
                claim_info['delivery_arrived_at'] = utils.parse_datetime(
                    event['updated_ts'],
                )
        assert request.json.get('cursor', None) == initial_cursor
        event_stub = {
            'operation_id': 1,
            'change_type': 'status_change',
            'revision': 1,
        }
        response_events = [dict(event_stub, **event) for event in events]
        response = {'cursor': response_cursor, 'events': response_events}
        return mockserver.make_response(
            status=200, json=response, headers=RESPONSE_HEADERS,
        )

    await stq_runner.eats_eta_read_cargo_journal.call(
        task_id=corp_client, kwargs={'corp_client_type': corp_client},
    )
    for order in orders:
        order.update(claims_info[order['claim_id']])
        assert db_select_orders(order_nr=order['order_nr']) == [order]
    assert get_cargo_journal_cursor(corp_client) == response_cursor

    assert mock_cargo_journal.times_called == 1
    assert stq.eats_eta_read_cargo_journal.times_called == 1
    rescheduled_task = stq.eats_eta_read_cargo_journal.next_call()
    assert rescheduled_task['id'] == corp_client
    assert rescheduled_task['eta'] - now == datetime.timedelta(
        milliseconds=POLLING_DELAY_MS,
    )


@utils.eats_eta_settings_config3()
@pytest.mark.parametrize('corp_client', DUPLICATED_CORP_CLIENTS + ('unknown',))
async def test_cargo_journal_reader_duplicated_or_unknown_corp_client(
        stq_runner, stq, corp_client,
):
    await stq_runner.eats_eta_read_cargo_journal.call(
        task_id=corp_client, kwargs={'corp_client_type': corp_client},
    )

    assert stq.eats_eta_read_cargo_journal.times_called == 0


@utils.eats_eta_settings_config3()
@pytest.mark.parametrize('corp_client', OK_CORP_CLIENTS)
async def test_cargo_journal_reader_400(
        stq,
        stq_runner,
        now,
        mockserver,
        get_cargo_journal_cursor,
        create_cargo_journal_cursor,
        corp_client,
):
    initial_cursor = 'initial_cursor'
    create_cargo_journal_cursor(corp_client, initial_cursor)

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/journal',
    )
    def mock_cargo_journal(request):
        return mockserver.make_response(
            status=400, json={'code': 'db_error', 'message': 'message'},
        )

    await stq_runner.eats_eta_read_cargo_journal.call(
        task_id=corp_client, kwargs={'corp_client_type': corp_client},
    )
    assert get_cargo_journal_cursor(corp_client) is None

    assert mock_cargo_journal.times_called == 1
    assert stq.eats_eta_read_cargo_journal.times_called == 1
    rescheduled_task = stq.eats_eta_read_cargo_journal.next_call()
    assert rescheduled_task['id'] == corp_client
    assert rescheduled_task['eta'] - now == datetime.timedelta(milliseconds=0)


@utils.eats_eta_settings_config3()
@pytest.mark.parametrize('corp_client', OK_CORP_CLIENTS)
async def test_cargo_journal_reader_429(
        stq,
        stq_runner,
        now,
        mockserver,
        get_cargo_journal_cursor,
        create_cargo_journal_cursor,
        corp_client,
):
    initial_cursor = 'initial_cursor'
    create_cargo_journal_cursor(corp_client, initial_cursor)

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/journal',
    )
    def mock_cargo_journal(request):
        return mockserver.make_response(
            status=429,
            json={'code': 'db_error', 'message': 'message'},
            headers=RESPONSE_HEADERS,
        )

    await stq_runner.eats_eta_read_cargo_journal.call(
        task_id=corp_client, kwargs={'corp_client_type': corp_client},
    )
    assert get_cargo_journal_cursor(corp_client) == initial_cursor

    assert mock_cargo_journal.times_called == 1
    assert stq.eats_eta_read_cargo_journal.times_called == 1
    rescheduled_task = stq.eats_eta_read_cargo_journal.next_call()
    assert rescheduled_task['id'] == corp_client
    assert rescheduled_task['eta'] - now == datetime.timedelta(
        milliseconds=POLLING_DELAY_MS,
    )
