import pytest

import tests_eats_logistics_proactive_support.common as common


async def test_200(taxi_eats_logistics_proactive_support, pgsql):
    pg_result = common.select_deliveries(pgsql)
    assert pg_result == []
    response = await taxi_eats_logistics_proactive_support.post(
        '/v1/start-watch', json=common.DEFAULT_DELIVERY,
    )

    assert response.status_code == 200
    response = await taxi_eats_logistics_proactive_support.post(
        '/v1/push-event', json=common.DEFAULT_EVENT,
    )
    assert response.status_code == 200
    response = await taxi_eats_logistics_proactive_support.post(
        '/v1/push-event', json=common.DEFAULT_EVENT,
    )
    assert response.status_code == 200

    pg_result = common.select_deliveries(pgsql)
    assert len(pg_result) == 1
    pg_result = common.select_events(common.TEST_DELIVERY_ID, pgsql)
    assert len(pg_result) == 2


async def test404(taxi_eats_logistics_proactive_support):
    response = await taxi_eats_logistics_proactive_support.post(
        '/v1/push-event', json=common.DEFAULT_EVENT,
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    'test_event',
    [
        common.modify_event(
            {
                'delivery_id': '000002',
                'meta_info': {
                    'position': [4.5, 5.5],
                    'promise': '2021-03-04T15:00:00+00:00',
                },
            },
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_logistics_proactive_support',
    files=['fill_deliveries.sql', 'fill_events.sql'],
)
async def test_non_empty(
        taxi_eats_logistics_proactive_support, pgsql, test_event,
):
    delivery_id = common.EVENTS_DATA[0][0]
    pg_result = common.select_events(delivery_id, pgsql)
    initial_len = len(pg_result)
    initial_events = common.EVENTS_DATA[0:initial_len]
    assert pg_result == initial_events

    response = await taxi_eats_logistics_proactive_support.post(
        '/v1/push-event', json=test_event,
    )
    expected_result = (
        test_event['delivery_id'],
        test_event['event_type'],
        test_event['meta_info'],
    )

    assert response.status_code == 200

    pg_result = common.select_events(delivery_id, pgsql)
    assert len(pg_result) == initial_len + 1
    expected_result = initial_events + [expected_result]
    for result_field in pg_result:
        assert result_field in expected_result
