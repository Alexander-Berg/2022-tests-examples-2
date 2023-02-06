import datetime

import psycopg2
import pytest


HANDLE_PATH = '/internal/eats-order-stats/v1/places-event-counters'
NOW = datetime.datetime.fromisoformat('2022-07-11T10:00:00+03:00')
TIME_PLACEHOLDER = '2011-11-11T11:11:11+01:00'


def to_str(datetm):
    return datetm.strftime('%Y-%m-%dT%H:%M:%S.%f%z')


def seconds(count):
    return datetime.timedelta(seconds=count)


def _make_checkout_response(order_nr, asap):
    response = {
        'items': [
            {
                'order_nr': order_nr,
                'revision': {
                    'number': 1,
                    'costs': {'type': 'unfetched_object'},
                    'items': {'type': 'unfetched_object'},
                    'created_at': TIME_PLACEHOLDER,
                },
                'changes': {'type': 'unfetched_object'},
                'currency_code': 'RUB',
                'payment_method': 'prepayment_cashless',
            },
        ],
    }
    if not asap:
        response['items'][0]['revision']['delivery_date'] = TIME_PLACEHOLDER
    return response


def _make_stq_event(
        order_nr,
        place_id,
        order_event,
        ready_to_delivery_at=None,
        taken_at=None,
        created_at=NOW,
):
    event = {
        'order_nr': order_nr,
        'place_id': place_id,
        'order_event': order_event,
        'created_at': to_str(created_at),
    }
    if ready_to_delivery_at:
        event['ready_to_delivery_at'] = to_str(ready_to_delivery_at)
    if taken_at:
        event['taken_at'] = to_str(taken_at)
    return event


def _db_select_counters(pgsql):
    cursor = pgsql['eats_order_stats'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute(
        'SELECT place_id, event_type, statistics '
        'FROM eats_order_stats.place_event_counters;',
    )
    return sorted(
        cursor.fetchall(),
        key=lambda item: (item['place_id'], item['event_type']),
    )


@pytest.mark.parametrize(
    'events,request_body,asap,expected_db_response_json,'
    'expected_handle_response_json',
    [
        pytest.param(
            [
                _make_stq_event(
                    'order-1',
                    'place-1',
                    'ready_to_delivery',
                    ready_to_delivery_at=NOW + seconds(1),
                ),
                _make_stq_event(
                    'order-2', 'place-2', 'taken', taken_at=NOW + seconds(2),
                ),
            ],
            {
                'place_ids': ['place-1', 'place-2'],
                'timestamp': TIME_PLACEHOLDER,
            },
            False,
            'db_empty.json',
            'handle_empty.json',
            id='ignore_non_asap',
        ),
        pytest.param(
            [
                _make_stq_event(
                    'order-1',
                    'place-1',
                    'ready_to_delivery',
                    ready_to_delivery_at=NOW + seconds(1),
                ),
                _make_stq_event(
                    'order-2',
                    'place-2',
                    'ready_to_delivery',
                    ready_to_delivery_at=NOW + seconds(2),
                ),
            ],
            {
                'place_ids': ['place-1', 'place-2'],
                'timestamp': to_str(NOW + seconds(4)),
            },
            True,
            'db_ready_to_delivery.json',
            'handle_ready_to_delivery.json',
            id='store_ready_to_delivery_to_db',
        ),
        pytest.param(
            [
                _make_stq_event(
                    'order-1', 'place-1', 'taken', taken_at=NOW + seconds(1),
                ),
                _make_stq_event(
                    'order-2',
                    'place-2',
                    'taken',
                    taken_at=NOW + seconds(2),
                    ready_to_delivery_at=NOW + seconds(1),
                ),
            ],
            {
                'place_ids': ['place-1', 'place-2'],
                'timestamp': to_str(NOW + seconds(4)),
            },
            True,
            'db_taken.json',
            'handle_taken.json',
            id='store_taken_to_db',
        ),
        pytest.param(
            [
                _make_stq_event(
                    'order-1',
                    'place-3',
                    'ready_to_delivery',
                    ready_to_delivery_at=NOW + seconds(1),
                ),
                _make_stq_event(
                    'order-2',
                    'place-3',
                    'taken',
                    ready_to_delivery_at=NOW + seconds(1),
                    taken_at=NOW + seconds(2),
                ),
                _make_stq_event(
                    'order-2', 'place-3', 'taken', taken_at=NOW + seconds(3),
                ),
            ],
            {'place_ids': ['place-3'], 'timestamp': to_str(NOW + seconds(4))},
            True,
            'db_recalculated.json',
            'handle_recalculated.json',
            id='recalculate_db_statistics',
        ),
    ],
)
@pytest.mark.experiments3(
    filename='eats_order_stats_place_event_counters.json',
)
@pytest.mark.now(to_str(NOW + seconds(10)))
async def test_place_event_counters(
        taxi_eats_order_stats,
        pgsql,
        stq_runner,
        load_json,
        mockserver,
        events,
        request_body,
        asap,
        expected_db_response_json,
        expected_handle_response_json,
):
    @mockserver.json_handler('/eats-checkout/orders/fetch-revisions')
    def _mock_checkout(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            status=200,
            json=_make_checkout_response(request.json['order_nrs'][0], asap),
        )

    for event in events:
        await stq_runner.eats_order_stats_cooking_order.call(
            task_id=event['order_nr'], kwargs=event,
        )
    assert _mock_checkout.times_called == len(events)

    assert _db_select_counters(pgsql) == load_json(expected_db_response_json)

    response = await taxi_eats_order_stats.post(HANDLE_PATH, json=request_body)
    assert response.status_code == 200
    assert sorted(
        response.json()['data'], key=lambda item: item['place_id'],
    ) == load_json(expected_handle_response_json)
