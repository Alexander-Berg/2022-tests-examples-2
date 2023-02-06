import pytest


HANDLER = 'driver/v1/profile-view/v1/options/update'

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

POSTPAYMENT_SETTINGS = [
    {
        'options': [
            {
                'blocking_tags': [],
                'exams': [],
                'name': 'post_payment',
                'prefix': 'other',
                'title_key': 'post_payment_title',
            },
        ],
        'title_key': 'post_payment.title',
    },
    {
        'options': [
            {
                'blocking_tags': [],
                'exams': [],
                'name': 'post_payment_eda',
                'prefix': 'other',
                'title_key': 'post_payment_eda_title',
            },
        ],
        'title_key': 'post_payment_eda.title',
    },
]


def select_driver(pgsql, park_id, driver_profile_id):
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


def select_options(pgsql, driver_options_id):
    cursor = pgsql['driver_options_pg'].cursor()
    cursor.execute(
        'SELECT name, is_active '
        'FROM driver_options.options '
        'WHERE driver_options_id = \'{}\''.format(driver_options_id),
    )
    result = list(row for row in cursor)
    cursor.close()
    return result


def select_tasks(pgsql):
    cursor = pgsql['driver_options_pg'].cursor()
    cursor.execute('SELECT * FROM driver_options.tasks')
    result = list(row for row in cursor)
    cursor.close()
    return result


@pytest.mark.parametrize(
    'driver_profile_id,etag,old_driver,old_options,new_options',
    [
        # driver with options
        (
            'uuid1',
            '123',
            [(10, '123', '123')],
            [('thermopack', False), ('thermobag', True)],
            [
                ('cargo_act', True),
                ('medical_card', True),
                ('thermopack', False),
                ('thermobag', False),
            ],
        ),
        #  new  driver
        (
            'uuid2',
            None,
            [],
            [],
            [
                ('cargo_act', True),
                ('medical_card', True),
                ('thermobag', False),
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
        etag,
        old_driver,
        old_options,
        new_options,
):
    driver_authorizer.set_session(PARK_ID, 'session1', driver_profile_id)
    driver_tags_mocks.set_tags_info(PARK_ID, driver_profile_id, [])
    unique_drivers_mocks.set_exams(
        PARK_ID,
        driver_profile_id,
        [{'course': 'cargo', 'result': 5, 'updated_by': 'support'}],
    )

    AUTHORIZED_HEADERS['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id
    if etag:
        AUTHORIZED_HEADERS['ETag'] = etag

    driver = select_driver(pgsql, PARK_ID, driver_profile_id)
    assert driver == old_driver
    finished_etag = None if not driver else driver[0][1]

    if driver:
        options = select_options(pgsql, driver[0][0])
        assert sorted(options) == sorted(old_options)

    response = await taxi_driver_profile_view.post(
        HANDLER,
        headers=AUTHORIZED_HEADERS,
        json={
            'location': {'lat': 55.744094, 'lon': 37.627920},
            'options': {
                'delivery': [
                    {'name': 'thermobag', 'value': False},
                    {'name': 'medical_card', 'value': True},
                ],
                'other': [{'name': 'cargo_act', 'value': True}],
            },
        },
    )

    driver = select_driver(pgsql, PARK_ID, driver_profile_id)
    driver_options_id = driver[0][0]
    new_etag = driver[0][1]

    options = select_options(pgsql, driver[0][0])
    assert sorted(options) == sorted(new_options)

    assert stq.driver_options_sync.times_called == 1
    stq_task = stq.driver_options_sync.next_call()
    stq_task['kwargs'].pop('log_extra')

    kwargs = {
        'park_id': PARK_ID,
        'driver_profile_id': driver_profile_id,
        'driver_options_id': driver_options_id,
        'delivery': {'thermobag': False, 'medical_card': True},
        'other': {'cargo_act': True},
        'etag': new_etag,
    }
    if finished_etag:
        kwargs['finished_etag'] = finished_etag

    assert stq_task['queue'] == 'driver_options_sync'
    assert stq_task['args'] == []
    assert stq_task['kwargs'] == kwargs

    assert response.status_code == 200
    assert response.json() == {'meta': {'etag': new_etag}}

    tasks = select_tasks(pgsql)
    task_id = etag if etag else driver_profile_id
    assert tasks == [(driver_options_id, task_id)]


@pytest.mark.experiments3(filename='experiments3_defaults.json')
@pytest.mark.config(DRIVER_OPTIONS_BUILDER_SETTINGS=POSTPAYMENT_SETTINGS)
async def test_driver_deactivation_locked_options_update(
        taxi_driver_profile_view,
        driver_authorizer,
        unique_drivers_mocks,
        driver_tags_mocks,
        fleet_parks,
        pgsql,
):
    driver_profile_id = 'uuid543'

    driver_authorizer.set_session(PARK_ID, 'session1', driver_profile_id)
    driver_tags_mocks.set_tags_info(PARK_ID, driver_profile_id, [])
    unique_drivers_mocks.set_exams(PARK_ID, driver_profile_id, [])

    AUTHORIZED_HEADERS['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id

    async def update_driver_other_options(headers, other_options):
        return await taxi_driver_profile_view.post(
            HANDLER,
            headers=headers,
            json={
                'location': {'lat': 55.744094, 'lon': 37.627920},
                'options': {
                    'other': [
                        {'name': key, 'value': val}
                        for key, val in other_options
                    ],
                },
            },
        )

    new_options = [('post_payment', True), ('post_payment_eda', True)]

    response = await update_driver_other_options(
        AUTHORIZED_HEADERS, new_options,
    )

    assert response.status_code == 200

    driver = select_driver(pgsql, PARK_ID, driver_profile_id)
    driver_options_id = driver[0][0]
    new_etag = driver[0][1]

    assert response.json() == {'meta': {'etag': new_etag}}

    options = select_options(pgsql, driver[0][0])
    assert sorted(options) == sorted(new_options)

    tasks = select_tasks(pgsql)
    task_id = driver_profile_id
    assert tasks == [(driver_options_id, task_id)]

    old_options = new_options
    new_options = [('post_payment_eda', False)]

    AUTHORIZED_HEADERS['ETag'] = new_etag
    response = await update_driver_other_options(
        AUTHORIZED_HEADERS, new_options,
    )

    driver = select_driver(pgsql, PARK_ID, driver_profile_id)

    options = select_options(pgsql, driver[0][0])
    assert sorted(options) == sorted(old_options)

    assert response.status_code == 400
    assert response.json() == {
        'code': 'BAD_REQUEST',
        'message': 'Option deactivation is not allowed',
    }

    # not locked options must be available to setting false
    new_options = [('post_payment', False)]

    response = await update_driver_other_options(
        AUTHORIZED_HEADERS, new_options,
    )

    assert response.status_code == 200

    driver = select_driver(pgsql, PARK_ID, driver_profile_id)
    driver_options_id = driver[0][0]
    old_etag = new_etag
    new_etag = driver[0][1]

    assert response.json() == {'meta': {'etag': new_etag}}

    options = select_options(pgsql, driver[0][0])
    assert sorted(options) == sorted(
        new_options + [('post_payment_eda', True)],
    )

    tasks = select_tasks(pgsql)
    task_id = driver_profile_id
    assert tasks == [
        (driver_options_id, task_id),
        (driver_options_id, old_etag),
    ]
