import pytest


HANDLER = 'driver/v1/profile-view/v1/drivers/delivery'

PARK_ID = 'park_id1'

AUTHORIZED_HEADERS = {
    'Accept-Language': 'ru',
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.10 (1234)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'User-Agent': 'Taximeter 9.10 (1234)',
}


@pytest.fixture(name='config_with_pro_courier')
async def _config_with_pro_courier(
        load_json, taxi_config, taxi_driver_profile_view,
):
    config = load_json('config.json')
    config['DRIVER_OPTIONS_BUILDER_SETTINGS'].append(
        {
            'options': [
                {
                    'blocking_tags': [],
                    'description_key': 'profi_courier.requirements',
                    'exams': ['profi_exam'],
                    'name': 'profi_courier',
                    'prefix': 'delivery',
                    'title_key': 'profi_courier',
                },
            ],
            'title_key': 'delivery.title',
        },
    )
    taxi_config.set_values(config)
    await taxi_driver_profile_view.invalidate_caches()


@pytest.mark.parametrize(
    'driver_profile_id,old_driver,old_options,new_options',
    [
        # driver with options
        (
            'uuid1',
            [(10, '123', '123')],
            [('thermopack', False), ('thermobag', True)],
            [
                ('medical_card', True),
                ('thermopack', False),
                ('thermobag', False),
                ('profi_courier', True),
            ],
        ),
        #  new  driver
        (
            'uuid2',
            [],
            [],
            [
                ('medical_card', True),
                ('thermobag', False),
                ('profi_courier', True),
            ],
        ),
    ],
)
@pytest.mark.experiments3(filename='experiments3_defaults.json')
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.pgsql('driver_options_pg', files=['driver_options.sql'])
async def test_driver_options_update(
        taxi_driver_profile_view,
        driver_authorizer,
        unique_drivers_mocks,
        driver_tags_mocks,
        fleet_parks,
        pgsql,
        stq,
        mockserver,
        driver_profile_id,
        old_driver,
        old_options,
        new_options,
        config_with_pro_courier,
):
    driver_authorizer.set_session(PARK_ID, 'session1', driver_profile_id)
    driver_tags_mocks.set_tags_info(PARK_ID, driver_profile_id, [])
    unique_drivers_mocks.set_exams(
        PARK_ID,
        driver_profile_id,
        [
            {'course': 'cargo', 'result': 5, 'updated_by': 'support'},
            {'course': 'profi_exam', 'result': 5, 'updated_by': 'support'},
        ],
    )

    def select_driver(park_id, driver_profile_id):
        cursor = pgsql['driver_options_pg'].cursor()
        cursor.execute(
            'SELECT id, etag, finished_etag '
            'FROM driver_options.drivers '
            'WHERE park_driver_profile_id = \'{}\''.format(
                park_id + '_' + driver_profile_id,
            ),
        )
        result = list(row for row in cursor)
        cursor.close()
        return result

    def select_options(driver_options_id):
        cursor = pgsql['driver_options_pg'].cursor()
        cursor.execute(
            'SELECT name, is_active '
            'FROM driver_options.options '
            'WHERE driver_options_id = \'{}\''.format(driver_options_id),
        )
        result = list(row for row in cursor)
        cursor.close()
        return result

    AUTHORIZED_HEADERS['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id

    driver = select_driver(PARK_ID, driver_profile_id)
    assert driver == old_driver
    finished_etag = None if not driver else driver[0][1]

    if driver:
        options = select_options(driver[0][0])
        assert sorted(options) == sorted(old_options)

    response = await taxi_driver_profile_view.post(
        HANDLER,
        headers=AUTHORIZED_HEADERS,
        json={
            'location': {'lat': 55.744094, 'lon': 37.627920},
            'options': {
                'medical_card': True,
                'thermobag': False,
                'profi_courier': True,
            },
        },
    )

    driver = select_driver(PARK_ID, driver_profile_id)
    driver_options_id = driver[0][0]
    new_etag = driver[0][1]

    options = select_options(driver[0][0])
    assert sorted(options) == sorted(new_options)

    assert stq.driver_options_sync.times_called == 1
    stq_task = stq.driver_options_sync.next_call()
    stq_task['kwargs'].pop('log_extra')

    kwargs = {
        'park_id': PARK_ID,
        'driver_profile_id': driver_profile_id,
        'driver_options_id': driver_options_id,
        'delivery': {
            'thermobag': False,
            'medical_card': True,
            'profi_courier': True,
        },
        'etag': new_etag,
    }
    if finished_etag:
        kwargs['finished_etag'] = finished_etag

    assert stq_task['queue'] == 'driver_options_sync'
    assert stq_task['args'] == []
    assert stq_task['kwargs'] == kwargs

    assert response.status_code == 200
