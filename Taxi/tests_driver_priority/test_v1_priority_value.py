import datetime as dt
from typing import List
from typing import Optional
from typing import Tuple

# pylint: disable=F0401,C5521
from dap_tools.dap import dap_fixture  # noqa: F401 C5521
# pylint: enable=F0401,C5521
import pytest

from tests_driver_priority import constants
from tests_driver_priority import db_tools
from tests_driver_priority import utils

_NOW = dt.datetime.now(dt.timezone.utc)
_HOUR = dt.timedelta(hours=1)

_DEFAULT_CALCULATIONS: List[Tuple[str, str, dt.datetime, dt.datetime]] = [
    ('dbid_hascalculation', 'moscow', _NOW, _NOW - _HOUR),
]
_HEADERS = {
    'Accept-Language': constants.DEFAULT_ACCEPT_LANGUAGE,
    'User-Agent': constants.DEFAULT_USER_AGENT,
}


@pytest.mark.driver_tags_match(
    dbid='dbid', uuid='uuid', tags_info={}, udid='udid',
)
@pytest.mark.driver_tags_match(
    dbid='no', uuid='coordinate', tags_info={}, udid='udid',
)
@pytest.mark.driver_tags_match(
    dbid='dbid', uuid='hascalculation', tags_info={}, udid='udid',
)
@pytest.mark.driver_ratings(
    ratings=[{'unique_driver_id': 'udid', 'rating': 4.94}],
)
@pytest.mark.driver_taximeter(
    profile='dbid_uuid', platform='android', version='10.10', version_type='',
)
@pytest.mark.driver_taximeter(
    profile='no_coordinate',
    platform='android',
    version='10.10',
    version_type='',
)
@pytest.mark.driver_taximeter(
    profile='dbid_hascalculation',
    platform='android',
    version='10.10',
    version_type='',
)
@pytest.mark.driver_trackstory(
    positions={
        'dbid_uuid': {
            'lon': 37.6,
            'lat': 55.75,
            'timestamp': int(_NOW.timestamp()),
        },
        'position_without-zone': {
            'lon': 1.1,
            'lat': 2.2,
            'timestamp': int(_NOW.timestamp()),
        },
    },
)
@pytest.mark.pgsql(
    'driver_priority',
    queries=db_tools.get_pg_default_data(_NOW)
    + [db_tools.insert_priority_calculations(_DEFAULT_CALCULATIONS)],
)
@pytest.mark.config(
    ENABLE_PRIORITY_BY_EXPERIMENTS={'__default__': False},
    PRIORITY_ACTIVITY_FETCH_ENABLED=True,
    PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST,
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'dbid, uuid, position, expected_code',
    [
        pytest.param(
            'dbid', 'uuid', None, 200, id='coordinate from trackstory',
        ),
        pytest.param(
            'no',
            'coordinate',
            None,
            404,
            id='send 404 without passed coordinate or stored calculation',
        ),
        pytest.param(
            'no',
            'coordinate',
            list(constants.MSK_COORDS),
            200,
            id=' save passed coordinate and then make good response',
        ),
        pytest.param(
            'dbid',
            'hascalculation',
            None,
            200,
            id='good response for already saved coordinate',
        ),
    ],
)
async def test_handler(
        taxi_driver_priority,
        dap,
        mockserver,
        dbid: str,
        uuid: str,
        position: Optional[List[float]],
        expected_code: int,
):
    taxi_driver_priority = dap.create_driver_wrapper(
        taxi_driver_priority,
        dbid,
        uuid,
        user_agent=constants.DEFAULT_USER_AGENT,
    )

    if position is not None:
        response = await taxi_driver_priority.post(
            constants.VALUE_URL, {'position': position}, headers=_HEADERS,
        )
        assert response.status_code == 200

    response = await taxi_driver_priority.get(
        constants.VALUE_URL, headers=_HEADERS,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == utils.polling_response(1, 0, 1)
