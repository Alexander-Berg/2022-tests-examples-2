import datetime

import pytest

from tests_workforce_metrics_storage import util


@pytest.mark.now('2020-01-01T00:01:00+0000')
async def test_v1_event_new(
        taxi_workforce_metrics_storage, mocked_time, pgsql,
):
    event = {
        'idempotency_token': 'token-1',
        'type': 'type-X',
        'employee_id': '000000000000000000000001',
        'extra_data': {
            'order_id': 'order-id-1',
            'important_feature': 'feat-1',
        },
        'descriptor': {'name': 'proc'},
        'created': '2020-01-01T00:01:00+0000',
    }
    event_expected = {
        'activation': datetime.datetime(2020, 1, 1, 0, 1, 0, 200000),
        'created': datetime.datetime(2020, 1, 1, 0, 1),
        'deadline': datetime.datetime(2020, 1, 1, 0, 21),
        'descriptor': '{"name":"proc"}',
        'employee_id': 1,
        'event_id': 1,
        'event_type_id': 1,
        'extra_data': '{"order_id":"order-id-1","important_feature":"feat-1"}',
    }
    token_expected = {
        'token': 'token-1',
        'deadline': datetime.datetime(2020, 1, 2, 0, 1),
    }

    response = await taxi_workforce_metrics_storage.post(
        '/v1/event/new', json=event,
    )
    assert response.status_code == 200

    stored_events = util.select_named('select * from events.queue_64', pgsql)
    stored_tokens = util.select_named(
        'select token, deadline from events.tokens', pgsql,
    )
    assert stored_events == [event_expected]
    assert stored_tokens == [token_expected]

    # deduplication check
    response = await taxi_workforce_metrics_storage.post(
        '/v1/event/new', json=event,
    )
    assert response.status_code == 200

    stored_events = util.select_named('select * from events.queue_64', pgsql)
    stored_tokens = util.select_named(
        'select token, deadline from events.tokens', pgsql,
    )
    assert stored_events == [event_expected]
    assert stored_tokens == [token_expected]
