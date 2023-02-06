import pytest


@pytest.mark.experiments3(
    is_config=True,
    name='driver_change_transport_type',
    consumers=['driver_profile_view/change_transport_type'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'transport_type': 'car'},
)
@pytest.mark.parametrize(
    'driver_options_id, expected_etag, thermo, medical_card, tags',
    [(10, 'new_etag', 1, 1, 2), (None, '123', 0, 0, 0)],
)
@pytest.mark.pgsql('driver_options_pg', files=['driver_options.sql'])
async def test_stq(
        taxi_driver_profile_view,
        stq_runner,
        mockserver,
        pgsql,
        driver_options_id,
        expected_etag,
        thermo,
        medical_card,
        tags,
):
    await taxi_driver_profile_view.invalidate_caches()

    @mockserver.json_handler('/driver-profiles/v1/driver/delivery')
    def _mock_update_thermo(request):
        assert request.json['delivery'] == {
            'profi_courier': True,
            'thermobag': False,
        }
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler('/driver-profiles/v1/driver/medical-card')
    def _mock_update_medical_card(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler('/tags/v1/upload')
    def _mock_tags_v1_upload(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler(
        '/contractor-transport/internal/v1/transport-active',
    )
    def _mock_contractor_transport(request):
        assert request.args['contractor_id'] == 'park_id1_uuid1'
        assert request.json['type'] == 'car'
        return mockserver.make_response(status=200, json={})

    def select_driver(park_id, driver_profile_id):
        cursor = pgsql['driver_options_pg'].cursor()
        cursor.execute(
            'SELECT finished_etag '
            'FROM driver_options.drivers '
            'WHERE park_driver_profile_id = \'{}\''.format(
                park_id + '_' + driver_profile_id,
            ),
        )
        result = list(row for row in cursor)
        cursor.close()
        return result

    def insert_task(driver_options_id, etag):
        cursor = pgsql['driver_options_pg'].cursor()
        cursor.execute(
            'INSERT INTO driver_options.tasks (driver_options_id, etag) '
            'VALUES ({}, \'{}\')'.format(driver_options_id, etag),
        )

    def select_tasks():
        cursor = pgsql['driver_options_pg'].cursor()
        cursor.execute('SELECT * FROM driver_options.tasks')
        result = list(row for row in cursor)
        cursor.close()
        return result

    if driver_options_id:
        insert_task(10, '123')

    await stq_runner.driver_options_sync.call(
        task_id='new_etag',
        kwargs={
            'park_id': 'park_id1',
            'driver_profile_id': 'uuid1',
            'driver_options_id': 10,
            'delivery': {
                'thermobag': False,
                'medical_card': True,
                'profi_courier': True,
            },
            'other': {'cargo_act': True, 'delivery_pack': False},
            'etag': 'new_etag',
            'finished_etag': '123',
        },
    )

    assert _mock_update_thermo.times_called == thermo
    assert _mock_update_medical_card.times_called == medical_card
    assert _mock_tags_v1_upload.times_called == tags

    driver = select_driver('park_id1', 'uuid1')
    assert driver == [(expected_etag,)]

    tasks = select_tasks()
    assert not tasks
