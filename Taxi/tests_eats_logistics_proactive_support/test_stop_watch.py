import pytest

import tests_eats_logistics_proactive_support.common as common


async def test_200(taxi_eats_logistics_proactive_support, pgsql):

    pg_result = common.select_deliveries(pgsql)
    assert pg_result == []

    response = await taxi_eats_logistics_proactive_support.post(
        '/v1/start-watch', json=common.DEFAULT_DELIVERY,
    )
    assert response.status_code == 200
    pg_result = common.select_deliveries(pgsql)
    assert len(pg_result) == 1

    # add events
    event_num = 2
    for _ in range(event_num):
        response = await taxi_eats_logistics_proactive_support.post(
            '/v1/push-event', json=common.DEFAULT_EVENT,
        )
        assert response.status_code == 200
    pg_result = common.select_events(common.TEST_DELIVERY_ID, pgsql)
    assert len(pg_result) == event_num

    response = await taxi_eats_logistics_proactive_support.post(
        '/v1/stop-watch', json={'delivery_id': common.TEST_DELIVERY_ID},
    )

    assert response.status_code == 200
    pg_result = common.select_deliveries(pgsql)
    assert pg_result == []

    pg_result = common.select_events(common.TEST_DELIVERY_ID, pgsql)
    assert pg_result == []


async def test_404(taxi_eats_logistics_proactive_support):

    response = await taxi_eats_logistics_proactive_support.post(
        '/v1/stop-watch', json={'delivery_id': common.TEST_DELIVERY_ID},
    )

    assert response.status_code == 404


@pytest.mark.pgsql(
    'eats_logistics_proactive_support',
    files=['fill_deliveries.sql', 'fill_events.sql'],
)
async def test_non_empty(taxi_eats_logistics_proactive_support, pgsql):
    pg_result = common.select_deliveries(pgsql)
    assert pg_result == common.DELIVERIES_DATA

    delivery_id = common.EVENTS_DATA[0][0]
    pg_result_events = common.select_events(delivery_id, pgsql)
    initial_len = len(pg_result_events)
    initial_events = common.EVENTS_DATA[0:initial_len]
    assert pg_result_events == initial_events

    response = await taxi_eats_logistics_proactive_support.post(
        '/v1/stop-watch', json={'delivery_id': delivery_id},
    )

    assert response.status_code == 200

    pg_result = common.select_deliveries(pgsql)
    assert len(pg_result) == len(common.DELIVERIES_DATA) - 1
    expected_result = common.DELIVERIES_DATA[1:]
    assert sorted(expected_result, key=lambda tup: tup[0]) == sorted(
        pg_result, key=lambda tup: tup[0],
    )

    pg_result_events = common.select_events(delivery_id, pgsql)
    assert pg_result_events == []
