import pytest


@pytest.mark.now('2020-11-10T11:00:00+0300')
@pytest.mark.config(PARKS_ACTIVATION_CHECK_CONTRACT_IS_FINISHED=True)
async def test_activate_parks(
        testpoint, pgsql, mock_territories, taxi_parks_activation,
):
    expected_data_by_park_id = {
        '100': {
            'deactivated': True,
            'deactivated_reason': 'all contracts are finished',
        },
        '300': {'deactivated': False, 'deactivated_reason': ''},
    }
    processed_parks = set()

    @testpoint('parks-activation::activate-and-record')
    def activate_and_record(data):
        park_id = data.pop('park_id')
        processed_parks.add(park_id)
        assert data == expected_data_by_park_id[park_id]

    pg_cursor = pgsql['parks_activation'].cursor()
    pg_cursor.execute('delete from distlocks.parks_activation_locks')
    await taxi_parks_activation.run_periodic_task('activate-parks')
    assert activate_and_record.times_called >= 1
    assert processed_parks == expected_data_by_park_id.keys()
