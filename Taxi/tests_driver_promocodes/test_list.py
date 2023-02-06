import pytest

DRIVER_HEADERS = {
    'X-Yandex-Login': 'vdovkin',
    'X-YaTaxi-Park-Id': 'park_0',
    'X-YaTaxi-Driver-Profile-Id': 'driver_0',
    'X-Request-Application-Version': '9.37 (1234)',
    'X-Request-Platform': 'android',
    'Accept-Language': 'ru',
}
ZONE_TO_COORDS = {
    'moscow': {'lon': 37.627920, 'lat': 55.744094, 'timestamp': 123},
    'spb': {'lon': -10, 'lat': -10, 'timestamp': 123},
}


def make_headers(is_uberdriver: bool) -> dict:
    return {
        **DRIVER_HEADERS,
        **(
            {
                'X-Request-Application': 'uberdriver',
                'X-Request-Version-Type': 'uber',
            }
            if is_uberdriver
            else {
                'X-Request-Application': 'taximeter',
                'X-Request-Version-Type': '',
            }
        ),
    }


@pytest.mark.pgsql('driver_promocodes', files=['series.sql'])
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.now('2020-06-01T12:00:00+0300')
@pytest.mark.parametrize(
    'expected_response,classes,zone,tags,is_uberdriver',
    [
        pytest.param(
            'response.json',
            ['econom'],
            'moscow',
            [],
            False,
            marks=pytest.mark.pgsql(
                'driver_promocodes', files=['promocodes_to_activate.sql'],
            ),
        ),
        pytest.param(
            'response_uberdriver.json',
            ['econom'],
            'moscow',
            [],
            True,
            marks=pytest.mark.pgsql(
                'driver_promocodes', files=['promocodes_to_activate.sql'],
            ),
        ),
        pytest.param(
            'response_wrong_conditions.json',
            ['comfort_plus'],
            'moscow',
            ['tag_no_group', 'tag_2_group_1', 'commission_promocode'],
            False,
            marks=pytest.mark.pgsql(
                'driver_promocodes', files=['promocodes_to_activate.sql'],
            ),
        ),
        pytest.param(
            'response_only_active.json',
            ['econom'],
            'moscow',
            ['commission_promocode'],
            False,
            marks=pytest.mark.pgsql(
                'driver_promocodes', files=['promocodes.sql'],
            ),
        ),
        pytest.param(
            'response_no_promocodes.json',
            ['econom'],
            'moscow',
            [],
            False,
            marks=pytest.mark.pgsql('driver_promocodes', files=[]),
        ),
    ],
)
async def test_driver_promocodes_list(
        taxi_driver_promocodes,
        parks,
        load_json,
        mockserver,
        driver_tags_mocks,
        expected_response,
        classes,
        zone,
        tags,
        is_uberdriver,
):
    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        return {
            'drivers': [
                {
                    'uuid': 'driver_0',
                    'dbid': 'park_0',
                    'position': [33.0, 55.0],
                    'classes': classes,
                },
            ],
        }

    driver_tags_mocks.set_tags_info('park_0', 'driver_0', tags)
    response = await taxi_driver_promocodes.get(
        'driver/v1/promocodes/v1/list',
        headers=make_headers(is_uberdriver),
        params={
            'tz': 'Europe/Moscow',
            'lat': ZONE_TO_COORDS[zone]['lat'],
            'lon': ZONE_TO_COORDS[zone]['lon'],
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)
