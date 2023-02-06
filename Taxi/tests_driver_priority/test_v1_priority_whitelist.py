import datetime

import pytest
import pytz

from tests_driver_priority import constants
from tests_driver_priority.plugins import mock_priority_data as pd


_NOW = datetime.datetime.now(tz=pytz.timezone('UTC'))
_SINGLE = pd.PriorityRuleType.Single
_TAG_RULE = pd.RuleType.TagRule


async def _ensure_responses(
        taxi_driver_priority, lon, lat, should_have_any_response,
):
    params = {
        'park_id': 'dbid',
        'session': 'session_0',
        'lon': lon,
        'lat': lat,
    }

    response = await taxi_driver_priority.get(
        constants.POLLING_URL,
        params=params,
        headers=constants.DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    values = response.json()['priority']
    assert any(values.values()) == should_have_any_response


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.driver_tags_match(
    dbid='dbid',
    uuid='uuid',
    tags_info={
        'developer': {
            'ttl': '2019-07-17T13:56:07.000+0000',
            'topics': ['priority'],
        },
        'yandex': {
            'ttl': '2019-07-16T13:56:07.000+0000',
            'topics': ['priority'],
        },
    },
)
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
            'tariff_zones': ['tula', 'moscow'],
        },
    ],
)
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
                        _SINGLE, [(_TAG_RULE, 'developer', 2, None)],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                ),
            ],
        ),
        pd.PriorityData(
            'company',
            [
                pd.PrioritySettings(
                    ['moscow'],
                    20,
                    pd.PriorityRule(_SINGLE, [(_TAG_RULE, 'yandex', 2, None)]),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                ),
            ],
        ),
    ],
)
@pytest.mark.tvm2_ticket(
    {200: constants.TICKET_200_300, 300: constants.TICKET_300_200},
)
@pytest.mark.parametrize(
    'cities_enabled', [[], ['moscow'], ['tula'], ['moscow', 'tula']],
)
async def test_whitelist(
        taxi_driver_priority, driver_authorizer, cities_enabled, taxi_config,
):
    park_id = 'dbid'
    uuid = 'uuid'
    whitelist = {'__default__': False}
    for city in cities_enabled:
        whitelist[city] = True
    taxi_config.set(PRIORITY_ZONES_WHITELIST=whitelist)

    driver_authorizer.set_session(park_id, 'session_0', uuid)

    await _ensure_responses(
        taxi_driver_priority, 37.6, 55.75, 'moscow' in whitelist,
    )
    await _ensure_responses(
        taxi_driver_priority, 37.6, 54.2, 'tula' in whitelist,
    )
