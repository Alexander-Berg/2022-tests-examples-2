import pytest


@pytest.mark.pgsql('cashback', files=['basic_cashback.sql'])
@pytest.mark.parametrize('status', [None, 'failed', 'done'])
async def test_events_mark_processed(taxi_cashback_web, pg_cashback, status):
    params = {'external_ref': 'order_id_1'}

    response = await taxi_cashback_web.get('/internal/events', params=params)
    assert response.status == 200
    content = await response.json()
    assert len(content['events']) == 2

    event_ids = ['event_id_1', 'event_id_2', 'event_id_3']
    body = {'event_ids': event_ids, 'status': status}
    response = await taxi_cashback_web.post(
        '/internal/events/mark-processed', params=params, json=body,
    )
    assert response.status == 200

    events = await pg_cashback.events.by_ids(event_ids)
    expected_status = status or 'done'
    assert all(ev['status'] == expected_status for ev in events)


@pytest.mark.pgsql('cashback', files=['basic_cashback.sql'])
async def test_events_mark_processed_idempotency(
        taxi_cashback_web, pg_cashback,
):
    params = {'external_ref': 'order_id_1'}
    event_ids = ['event_id_1', 'event_id_2', 'event_id_3']
    body = {'event_ids': event_ids}

    response = await taxi_cashback_web.post(
        '/internal/events/mark-processed', params=params, json=body,
    )
    assert response.status == 200

    response = await taxi_cashback_web.post(
        '/internal/events/mark-processed', params=params, json=body,
    )
    assert response.status == 200

    events = await pg_cashback.events.by_ids(event_ids)
    new_events = [ev for ev in events if ev['status'] == 'new']
    assert not new_events
