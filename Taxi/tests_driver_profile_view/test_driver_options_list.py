import pytest


HANDLER = 'driver/v1/profile-view/v1/options/list'

PARK_ID = 'park_id1'

AUTHORIZED_HEADERS = {
    'Accept-Language': 'ru',
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.10 (1234)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}

LOCATION_DEFAULT = {'location': {'lat': 55.744094, 'lon': 31.627920}}
LOCATION_MOSCOW = {'location': {'lat': 55.744094, 'lon': 37.627920}}

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


@pytest.mark.parametrize(
    'driver_profile_id,location,exams,driver_tags,version,'
    'expected_response',
    [
        # moscow, has options, no exams, has bad tags
        (
            'uuid1',
            LOCATION_MOSCOW,
            [],
            ['bad_rating'],
            '9.10 (1234)',
            'expected_response1.json',
        ),
        # nowhere, has options, no exams, has bad tags
        (
            'uuid1',
            LOCATION_DEFAULT,
            [],
            ['bad_rating'],
            '9.10 (1234)',
            'expected_response2.json',
        ),
        # moscow, has options, has cargo exam 5, has bad tags
        (
            'uuid1',
            LOCATION_MOSCOW,
            [{'course': 'cargo', 'result': 5}],
            ['bad_rating'],
            '9.10 (1234)',
            'expected_response3.json',
        ),
        # moscow, has options, has cargo exams 5, no bad tags
        (
            'uuid1',
            LOCATION_MOSCOW,
            [{'course': 'cargo', 'result': 5}],
            [],
            '9.10 (1234)',
            'expected_response4.json',
        ),
        # moscow, has options, has cargo exams 1, no bad tags
        (
            'uuid1',
            LOCATION_MOSCOW,
            [{'course': 'cargo', 'result': 1}],
            [],
            '9.10 (1234)',
            'expected_response4_1.json',
        ),
        # moscow, has options, has cargo exams 2, no bad tags
        (
            'uuid1',
            LOCATION_MOSCOW,
            [{'course': 'cargo', 'result': 2}],
            [],
            '9.10 (1234)',
            'expected_response4_2.json',
        ),
        # moscow, has options, has cargo exams 5 support, no bad tags
        (
            'uuid1',
            LOCATION_MOSCOW,
            [{'course': 'cargo', 'result': 5, 'updated_by': 'support'}],
            [],
            '9.10 (1234)',
            'expected_response4_3.json',
        ),
        # moscow, no options, no exams, no bad tags
        (
            'uuid3',
            LOCATION_MOSCOW,
            [],
            [],
            '9.10 (1234)',
            'expected_response5.json',
        ),
        # moscow, has options, no exams, no bad tags, bad version
        (
            'uuid1',
            LOCATION_MOSCOW,
            [],
            [],
            '9.05 (1234)',
            'expected_response6.json',
        ),
        (
            'uuid7',
            LOCATION_MOSCOW,
            [],
            [],
            '9.05 (1234)',
            'expected_response10.json',
        ),
        # moscow, empty DRIVER_OPTIONS_BUILDER_SETTINGS config
        pytest.param(
            'uuid3',
            LOCATION_MOSCOW,
            [],
            [],
            '9.10 (1234)',
            'expected_response9.json',
            marks=pytest.mark.config(DRIVER_OPTIONS_BUILDER_SETTINGS=[]),
        ),
    ],
)
@pytest.mark.experiments3(filename='experiments3_defaults.json')
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.pgsql('driver_options_pg', files=['driver_options.sql'])
async def test_driver_options_list(
        taxi_driver_profile_view,
        driver_authorizer,
        unique_drivers_mocks,
        driver_tags_mocks,
        fleet_parks,
        mockserver,
        load_json,
        driver_profile_id,
        location,
        exams,
        driver_tags,
        version,
        expected_response,
):
    driver_authorizer.set_session(PARK_ID, 'session1', driver_profile_id)
    driver_tags_mocks.set_tags_info(PARK_ID, driver_profile_id, driver_tags)
    unique_drivers_mocks.set_exams(PARK_ID, driver_profile_id, exams)

    AUTHORIZED_HEADERS['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id
    AUTHORIZED_HEADERS['X-Request-Application-Version'] = version

    response = await taxi_driver_profile_view.post(
        HANDLER, headers=AUTHORIZED_HEADERS, json=location,
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.parametrize(
    'location,mock_error,expected_response',
    [
        # empty location
        ({}, False, 'expected_response7.json'),
        # failed to get exams
        (LOCATION_MOSCOW, True, 'expected_response8.json'),
    ],
)
@pytest.mark.experiments3(filename='experiments3_defaults.json')
async def test_driver_options_list_error(
        taxi_driver_profile_view,
        driver_authorizer,
        unique_drivers_mocks,
        fleet_parks,
        mockserver,
        load_json,
        location,
        mock_error,
        expected_response,
):
    driver_authorizer.set_session(PARK_ID, 'session1', 'uuid1')

    AUTHORIZED_HEADERS['X-YaTaxi-Driver-Profile-Id'] = 'uuid1'

    response = await taxi_driver_profile_view.post(
        HANDLER, headers=AUTHORIZED_HEADERS, json=location,
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.experiments3(filename='experiments3_defaults.json')
@pytest.mark.config(DRIVER_OPTIONS_BUILDER_SETTINGS=POSTPAYMENT_SETTINGS)
async def test_driver_deactivation_locked_options_list(
        taxi_driver_profile_view,
        driver_authorizer,
        unique_drivers_mocks,
        driver_tags_mocks,
        fleet_parks,
        mockserver,
        load_json,
):
    driver_profile_id = 'uuid543'
    location = {
        'location': {'lat': 55.478983901730004, 'lon': 37.1946401739712},
    }

    driver_authorizer.set_session(PARK_ID, 'session1', driver_profile_id)
    driver_tags_mocks.set_tags_info(PARK_ID, driver_profile_id, [])
    unique_drivers_mocks.set_exams(PARK_ID, driver_profile_id, [])

    AUTHORIZED_HEADERS['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id

    async def update_driver_other_options(headers, other_options):
        return await taxi_driver_profile_view.post(
            'driver/v1/profile-view/v1/options/update',
            headers=headers,
            json={
                'location': location['location'],
                'options': {
                    'other': [
                        {'name': key, 'value': val}
                        for key, val in other_options
                    ],
                },
            },
        )

    response = await taxi_driver_profile_view.post(
        HANDLER, headers=AUTHORIZED_HEADERS, json=location,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response11_1.json')

    response = await update_driver_other_options(
        AUTHORIZED_HEADERS,
        [('post_payment', True), ('post_payment_eda', True)],
    )
    assert response.status_code == 200

    response = await taxi_driver_profile_view.post(
        HANDLER, headers=AUTHORIZED_HEADERS, json=location,
    )
    assert response.status_code == 200
    response_json_data = response.json()
    del response_json_data['meta']['etag']
    assert response_json_data == load_json('expected_response11_2.json')
