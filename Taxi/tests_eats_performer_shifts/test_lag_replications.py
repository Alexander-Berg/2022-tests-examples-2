import pytest


MOCK_NOW = '2020-12-01T16:40:50+00:00'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eda_couriers_schedule', files=['test_data_replication.sql'],
)
@pytest.mark.config(EATS_PERFORMER_SHIFTS_REPLICATION_TTL_DELAY=10)
async def test_lag_replications(taxi_eats_performer_shifts, load_json):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'updates?cursor=0_0',
    )
    expected_response = load_json('response_lag.json')
    assert response.status_code == 200
    assert response.json() == expected_response

    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1/courier-shift-states/'
        'updates?cursor=' + response.json()['data']['cursor'],
    )
    expected_response = load_json('response_empty.json')
    assert response.status_code == 200
    assert (
        response.json()['data']['shifts']
        == expected_response['data']['shifts']
    )
