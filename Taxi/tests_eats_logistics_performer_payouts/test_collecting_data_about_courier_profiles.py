import psycopg2
import pytest


PERFORMER_PAYOUTS_PROFILE_1_JSON = {
    'id': {'id': '1', 'type': 'performer'},
    'relations': [
        {'id': '34', 'type': 'courier_service'},
        {'id': 'park_id_uuid', 'type': 'driver_profile'},
    ],
    'factors': [
        {'name': 'eats_region_id', 'type': 'string', 'value': '1'},
        {'name': 'country_id', 'type': 'string', 'value': '35'},
        {'name': 'country_code', 'type': 'string', 'value': 'RU'},
        {'name': 'pool', 'type': 'string', 'value': 'some_provider'},
        {'name': 'transport_type', 'type': 'string', 'value': 'pedestrian'},
        {
            'name': 'started_work_at',
            'type': 'datetime',
            'value': '2001-04-01T07:00:00+00:00',
        },
        {'name': 'username', 'type': 'string', 'value': 'surname first_name'},
        {'name': 'timezone', 'type': 'string', 'value': 'Europe/Moscow'},
        {'name': 'billing_type', 'type': 'string', 'value': 'courier_service'},
        {'name': 'meta_is_picker', 'type': 'int', 'value': 0},
        {'name': 'meta_is_dedicated_picker', 'type': 'int', 'value': 0},
        {'name': 'meta_is_rover', 'type': 'int', 'value': 0},
        {'name': 'meta_is_storekeeper', 'type': 'int', 'value': 0},
        {'name': 'meta_is_courier_plus', 'type': 'int', 'value': 0},
        {'name': 'meta_is_ultima', 'type': 'int', 'value': 0},
    ],
    'remove_relations_on': [''],
}


@pytest.fixture(autouse=True)
def _mock_regions(mockserver, load_json):
    @mockserver.json_handler('/eats-core/v1/export/regions')
    def _mock_core(request):
        return load_json('eats_regions_response.json')


@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_all_factors.sql'],
)
async def test_distlock_task(
        taxi_eats_logistics_performer_payouts,
        pgsql,
        testpoint,
        _core_integration_profiles_update,
        _driver_profiles_retrieve_by_eats_id,
):
    @testpoint('test_subject_request')
    def test_subject(data):
        def sorted_data(one_of):
            one_of['relations'] = sorted(
                one_of['relations'], key=lambda x: x['id'],
            )
            one_of['factors'] = sorted(
                one_of['factors'], key=lambda x: x['name'],
            )
            return dict(one_of)

        assert sorted_data(data) == sorted_data(
            PERFORMER_PAYOUTS_PROFILE_1_JSON,
        )

    await taxi_eats_logistics_performer_payouts.run_periodic_task(
        'collecting-data-about-courier-profiles-periodic',
    )

    cursor = pgsql['eats_logistics_performer_payouts'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    cursor.execute('SELECT * FROM eats_logistics_performer_payouts.cursors')
    profiles_cursor = cursor.fetchone()

    assert profiles_cursor is not None
    assert profiles_cursor['id'] == 'courier_profiles'
    assert profiles_cursor['cursor'] == 'abc_1'

    assert _core_integration_profiles_update.times_called == 1
    assert _driver_profiles_retrieve_by_eats_id.times_called == 1
    assert test_subject.times_called == 1
