import pytest

NOW = '2021-09-03T12:00:00.000000+03:00'

HEADERS = {
    'Accept-Language': 'ru_RU',
    'X-Remote-IP': '12.34.56.78',
    'X-YaEda-CourierId': '1',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.65 (5397)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'User-Agent': 'Taximeter 9.25 (2222)',
}

ERROR_HEADERS = {
    'Accept-Language': 'ru_RU',
    'X-Remote-IP': '12.34.56.78',
    'X-YaEda-CourierId': '2',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.65 (5397)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'User-Agent': 'Taximeter 9.25 (2222)',
}

EXPECTED_X_POLLING_POWER_POLICY = (
    'full=601s, background=1202s, idle=1803s, powersaving=1204s'
)


@pytest.mark.now(NOW)
@pytest.mark.pgsql(
    'eats_performer_statistics', files=['fill_invalid_data.sql'],
)
async def test_time_border(taxi_eats_performer_statistics):

    response = await taxi_eats_performer_statistics.get(
        '/driver/v1/eats-performer-statistics/v1/start-screen',
        headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {'items': []}


@pytest.mark.now(NOW)
@pytest.mark.translations()
@pytest.mark.pgsql('eats_performer_statistics', files=['fill_data.sql'])
async def test_empty_config(taxi_eats_performer_statistics):
    response = await taxi_eats_performer_statistics.get(
        '/driver/v1/eats-performer-statistics/v1/start-screen',
        headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {'items': []}


@pytest.mark.translations()
@pytest.mark.pgsql('eats_performer_statistics', files=['fill_data.sql'])
async def test_empty_db_request(taxi_eats_performer_statistics):
    response = await taxi_eats_performer_statistics.get(
        '/driver/v1/eats-performer-statistics/v1/start-screen',
        headers=ERROR_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {'items': []}


@pytest.mark.now(NOW)
@pytest.mark.translations()
@pytest.mark.config(
    TAXIMETER_POLLING_POWER_POLICY_DELAYS={
        '__default__': {
            'background': 1202,
            'idle': 1803,
            'full': 601,
            'powersaving': 1204,
        },
    },
)
@pytest.mark.experiments3(
    filename='config3_eats_performer_statistics_statistics_params.json',
)
@pytest.mark.experiments3(
    name='eats_performer_statistics_fulltimer_widget',
    consumers=['eats-performer-statistics/courier-id'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'metric_days': '14', 'metric_hours': '12'},
    is_config=True,
)
@pytest.mark.pgsql('eats_performer_statistics', files=['fill_data.sql'])
async def test_ui(taxi_eats_performer_statistics, load_json):
    response = await taxi_eats_performer_statistics.get(
        '/driver/v1/eats-performer-statistics/v1/start-screen',
        headers=HEADERS,
    )

    assert 'X-Polling-Power-Policy' in response.headers

    expected_response = load_json('expected_response.json')

    delays = EXPECTED_X_POLLING_POWER_POLICY.split(', ').sort()
    assert (
        delays == response.headers['X-Polling-Power-Policy'].split(', ').sort()
    )
    assert response.status_code == 200
    assert response.json() == expected_response


async def test_start_screen_400(taxi_eats_performer_statistics, load_json):

    response = await taxi_eats_performer_statistics.get(
        '/driver/v1/eats-performer-statistics/v1/start-screen', headers=None,
    )

    assert response.status_code == 400
