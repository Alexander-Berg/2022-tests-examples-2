import psycopg2
import pytest

PERFORMER_PAYOUTS_PROFILE_1_JSON = {
    'id': '1',
    'revision': 1,
    'courier_service_id': 1,
    'courier_service_revision': 1,
    'eats_region_id': '1',
    'timezone': 'Europe/Moscow',
    'country_code': 'RU',
    'country_id': '35',
    'transport_type': 'pedestrian',
    'pool': 'some_provider',
    'started_work_at': '2001-04-01T07:00:00+00:00',
    'username': 'surname first_name',
    'billing_type': 'courier_service',
    'is_picker': False,
    'is_dedicated_picker': False,
    'is_rover': False,
    'is_storekeeper': False,
    'is_courier_plus': False,
    'is_ultima': False,
}


@pytest.fixture(autouse=True)
def _mock_regions(mockserver, load_json):
    @mockserver.json_handler('/eats-core/v1/export/regions')
    def _mock_core(request):
        return load_json('eats_regions_response.json')


@pytest.mark.pgsql('eats_payouts_events', files=['insert_courier_service.sql'])
async def test_courier_profiles_collector(
        taxi_eats_payouts_events,
        pgsql,
        testpoint,
        _core_integration_profiles_update,
        _driver_profiles_retrieve_by_eats_id,
):
    @testpoint('test_courier_profile_subject')
    def test_courier_profile_subject(data):
        assert data == PERFORMER_PAYOUTS_PROFILE_1_JSON

    await taxi_eats_payouts_events.run_periodic_task(
        'courier-profiles-collector-periodic',
    )

    cursor = pgsql['eats_payouts_events'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    cursor.execute('SELECT * FROM eats_payouts_events.cursors')
    profiles_cursor = cursor.fetchone()

    assert profiles_cursor is not None
    assert profiles_cursor['key'] == 'courier-profiles-collector'
    assert profiles_cursor['value'] == 'abc_2'

    assert _core_integration_profiles_update.times_called == 3
    assert _driver_profiles_retrieve_by_eats_id.times_called == 1
    assert test_courier_profile_subject.times_called == 1
