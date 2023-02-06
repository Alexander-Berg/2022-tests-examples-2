import pytest


@pytest.mark.parametrize(
    'event_ids ,expected_ids',
    [
        (['event_id_1', 'event_id_3'], ['event_id_1', 'event_id_3']),
        (['event_id_1', 'uknown_event'], ['event_id_1']),
        ([], []),
    ],
)
@pytest.mark.pgsql('cashback', files=['basic_cashback.sql'])
async def test_events_by_id(taxi_cashback_web, event_ids, expected_ids):
    body = {'event_ids': event_ids}
    response = await taxi_cashback_web.post(
        '/internal/events/by-id', json=body,
    )
    assert response.status == 200
    content = await response.json()

    event_ids = [ev['event_id'] for ev in content['events']]
    assert event_ids == expected_ids
