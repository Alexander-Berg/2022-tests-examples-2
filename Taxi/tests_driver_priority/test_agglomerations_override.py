import datetime
import json
import pathlib

import pytest

from tests_driver_priority import constants
from tests_driver_priority import utils
from tests_driver_priority.plugins import mock_priority_data as pd


_NOW = datetime.datetime(2019, 7, 15, 13, 57, 8, tzinfo=datetime.timezone.utc)
_SINGLE = pd.PriorityRuleType.Single
_RANKED = pd.PriorityRuleType.Ranked
_EXCLUDED = pd.PriorityRuleType.Excluded
_TAG_RULE = pd.RuleType.TagRule


_PRIORITY_BY_GEO_NODES = {
    'br_moscow_near_region': 1,
    'br_moscow': 2,
    'br_tula': 4,
    'br_russia': 8,
    '__default__': 16,
}

_CACHE_PATH = 'testsuite/cache/agglomerations/agglomerations_cache_dump.json'
_SERVICE_PATH = 'services/driver-priority'


async def _check_response(
        taxi_driver_priority, params, expected, driver_tags_mocks,
):
    response = await taxi_driver_priority.get(
        constants.POLLING_URL,
        params=params,
        headers=constants.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == expected
    assert driver_tags_mocks.has_calls()


@pytest.fixture
def create_cache_dump(mockserver, build_dir: pathlib.Path):
    cache_path = build_dir.joinpath(_SERVICE_PATH, _CACHE_PATH)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open('w') as file:
        file.write(json.dumps({'moscow': ['br_root']}))

    yield create_cache_dump

    if cache_path.is_file():
        cache_path.unlink()


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.usefixtures('create_cache_dump')
@pytest.mark.driver_tags_match(
    dbid='dbid_dev',
    uuid='uuid_dev',
    tags_info={'developer': {'topics': ['priority']}},
)
@pytest.mark.config(PRIORITY_ZONES_WHITELIST={'__default__': True})
@pytest.mark.priority_data(
    now=_NOW,
    data=[
        pd.PriorityData(
            'job',
            [
                pd.PrioritySettings(
                    ['__default__'],
                    10,
                    pd.PriorityRule(
                        _SINGLE, [(_TAG_RULE, 'developer', 16, None)],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                    is_achievable=True,
                    is_temporary=False,
                ),
                pd.PrioritySettings(
                    ['br_root'],
                    10,
                    pd.PriorityRule(
                        _SINGLE, [(_TAG_RULE, 'developer', 8, None)],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                    is_achievable=True,
                    is_temporary=False,
                ),
            ],
        ),
    ],
)
@pytest.mark.tvm2_ticket(
    {200: constants.TICKET_200_300, 300: constants.TICKET_300_200},
)
async def test_start_from_cache_dump(
        taxi_driver_priority, driver_authorizer, driver_tags_mocks,
):
    driver_authorizer.set_session('dbid_dev', 'session_0', 'uuid_dev')
    params = {
        'park_id': 'dbid_dev',
        'session': 'session_0',
        'lon': 37.6,
        'lat': 55.75,
    }

    # make request with initialized cache
    await _check_response(
        taxi_driver_priority,
        params,
        utils.polling_response(8, 0, 8),
        driver_tags_mocks,
    )


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.driver_tags_match(
    dbid='dbid_dev',
    uuid='uuid_dev',
    tags_info={'developer': {'topics': ['priority']}},
)
@pytest.mark.config(PRIORITY_ZONES_WHITELIST={'__default__': True})
@pytest.mark.priority_data(
    now=_NOW,
    data=[
        pd.PriorityData(
            'job',
            [
                pd.PrioritySettings(
                    ['__default__'],
                    10,
                    pd.PriorityRule(
                        _SINGLE, [(_TAG_RULE, 'developer', 16, None)],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                    is_achievable=True,
                    is_temporary=False,
                ),
                pd.PrioritySettings(
                    ['br_root'],
                    10,
                    pd.PriorityRule(
                        _SINGLE, [(_TAG_RULE, 'developer', 8, None)],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                    is_achievable=True,
                    is_temporary=False,
                ),
            ],
        ),
    ],
)
@pytest.mark.tvm2_ticket(
    {200: constants.TICKET_200_300, 300: constants.TICKET_300_200},
)
async def test_service_error(
        taxi_driver_priority, driver_authorizer, driver_tags_mocks, mockserver,
):
    driver_authorizer.set_session('dbid_dev', 'session_0', 'uuid_dev')
    params = {
        'park_id': 'dbid_dev',
        'session': 'session_0',
        'lon': 37.6,
        'lat': 55.75,
    }
    expected = utils.polling_response(8, 0, 8)

    # make request with initialized cache
    await _check_response(
        taxi_driver_priority, params, expected, driver_tags_mocks,
    )

    @mockserver.json_handler('/taxi-agglomerations/v1/br-geo-nodes/')
    def _agglomeration_mock(request):
        return mockserver.make_response('{}', status=500)

    # check cache restore on request error
    with pytest.raises(Exception):
        await taxi_driver_priority.invalidate_caches()

    await _check_response(
        taxi_driver_priority, params, expected, driver_tags_mocks,
    )

    @mockserver.json_handler('/taxi-agglomerations/v1/br-geo-nodes/')
    def _agglomeration_mock2(request):
        return []

    # check cache update failure on invalid data
    with pytest.raises(Exception):
        await taxi_driver_priority.invalidate_caches()

    await _check_response(
        taxi_driver_priority, params, expected, driver_tags_mocks,
    )


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.driver_tags_match(
    dbid='dbid_dev',
    uuid='uuid_dev',
    tags_info={
        'developer': {'topics': ['priority']},
        'yandex': {'topics': ['priority']},
        'gold': {'topics': ['commissions', 'priority']},
    },
)
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'name': 'br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'node',
            'parent_name': 'br_root',
        },
        {
            'name': 'br_russia',
            'name_en': 'Russia',
            'name_ru': 'Россия',
            'node_type': 'node',
            'parent_name': 'br_root',
            'region_id': '225',
        },
        {
            'name': 'br_moscow_adm',
            'name_en': 'Moscow (adm)',
            'name_ru': 'Москва (адм)',
            'node_type': 'node',
            'parent_name': 'br_moscow',
            'tariff_zones': ['moscow'],
            'region_id': '213',
        },
        {
            'name': 'br_moscow_near_region',
            'name_en': 'Moscow (Middle Region)',
            'name_ru': 'Москва (среднее)',
            'node_type': 'node',
            'parent_name': 'br_moscow',
        },
        {
            'name': 'br_mytishchi',
            'name_en': 'Mytishchi',
            'name_ru': 'Мытищи',
            'node_type': 'node',
            'parent_name': 'br_moscow_near_region',
            'tariff_zones': ['mytishchi'],
            'region_id': '10740',
        },
        {
            'name': 'br_tula',
            'name_en': 'Tula',
            'name_ru': 'Тула',
            'node_type': 'node',
            'parent_name': 'br_russia',
            'tariff_zones': ['tula'],
            'region_id': '15',
        },
    ],
)
@pytest.mark.config(PRIORITY_ZONES_WHITELIST={'__default__': True})
@pytest.mark.priority_data(
    now=_NOW,
    data=[
        pd.PriorityData(
            'job',
            [
                pd.PrioritySettings(
                    [zone],
                    10,
                    pd.PriorityRule(
                        _SINGLE, [(_TAG_RULE, 'developer', priority, None)],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                    is_achievable=True,
                    is_temporary=False,
                )
                for zone, priority in _PRIORITY_BY_GEO_NODES.items()
            ],
            extra_geo_nodes=['moscow', 'mytishchi', 'tula'],
        ),
    ],
)
@pytest.mark.parametrize(
    'lon, lat, stable_priority',
    [
        (37.6, 55.75, 2),  # moscow
        (37.738, 56.05, 1),  # mytishchi
        (37.6, 54.2, 4),  # tula
    ],
)
@pytest.mark.tvm2_ticket(
    {200: constants.TICKET_200_300, 300: constants.TICKET_300_200},
)
async def test_priorities(
        taxi_driver_priority,
        driver_authorizer,
        driver_tags_mocks,
        taxi_config,
        lon,
        lat,
        stable_priority,
):
    driver_authorizer.set_session('dbid_dev', 'session_0', 'uuid_dev')
    params = {
        'park_id': 'dbid_dev',
        'session': 'session_0',
        'lon': lon,
        'lat': lat,
    }

    expected = utils.polling_response(stable_priority, 0, stable_priority)

    await _check_response(
        taxi_driver_priority, params, expected, driver_tags_mocks,
    )
