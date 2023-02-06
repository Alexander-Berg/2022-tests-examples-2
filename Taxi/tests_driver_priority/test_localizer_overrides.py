import datetime
from typing import Any
from typing import List

# pylint: disable=F0401,C5521
from dap_tools.dap import dap_fixture  # noqa: F401 C5521
# pylint: enable=F0401,C5521
import pytest

from tests_driver_priority import constants
from tests_driver_priority import db_tools
from tests_driver_priority import payload_utils
from tests_driver_priority import utils

_NOW = datetime.datetime(2019, 7, 15, 13, 57, 8, tzinfo=datetime.timezone.utc)

_YANDEX_USER_AGENT = 'Taximeter 10.05 (1234)'
_YANGO_USER_AGENT = 'Taximeter-Yango 10.05'
_AZ_TAXIMETER_USER_AGENT = 'Taximeter-AZ 10.05'


def _get_priority_screen_items(yandex_team: str) -> List[Any]:
    return [
        payload_utils.ui_header_item(
            'Высокий приоритет',
            'Все заказы для вас одного',
            is_new_radar_ui=True,
        ),
        payload_utils.ui_priority_item(
            2,
            yandex_team,
            None,
            is_matched=True,
            new_icon=True,
            use_new_divider_type=True,
        ),
    ]


@pytest.mark.driver_tags_match(
    dbid='dbid_dev',
    uuid='uuid_dev',
    tags_info={
        'yandex': {
            'ttl': '2019-07-16T13:56:07.000+0000',
            'topics': ['priority'],
        },
    },
)
@pytest.mark.driver_trackstory(
    positions={
        'dbid_dev_uuid_dev': {
            'lon': 37.6,
            'lat': 55.75,
            'timestamp': int(_NOW.timestamp()),
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
        },
        {
            'name': 'br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'node',
            'parent_name': 'br_root',
        },
        {
            'name': 'br_moscow_adm',
            'name_en': 'Moscow (adm)',
            'name_ru': 'Москва (адм)',
            'node_type': 'node',
            'parent_name': 'br_moscow',
            'tariff_zones': ['moscow'],
        },
    ],
)
@pytest.mark.pgsql(
    'driver_priority',
    queries=db_tools.join_queries(
        [
            # company
            db_tools.insert_priority(0, 'company', True, 'company'),
            db_tools.insert_priority_relation('moscow', 0, False),
            db_tools.insert_preset(0, 0, 'company_moscow', _NOW),
            db_tools.insert_preset_relation('moscow', 0),
            db_tools.insert_version(
                0,
                0,
                20,
                {
                    'ranked_rule': [
                        # zero priority will be hidden
                        db_tools.make_tag_rule('mail_ru', 0),
                        db_tools.make_tag_rule('yandex', 2),
                    ],
                },
                db_tools.EMPTY_PAYLOAD,
                _NOW,
                _NOW,
            ),
            db_tools.insert_preset(
                2, 0, 'company_default', _NOW, is_default=True,
            ),
            db_tools.insert_version(
                2,
                2,
                0,
                db_tools.EMPTY_RULE,
                db_tools.EMPTY_PAYLOAD,
                _NOW,
                _NOW,
                disabled_condition={'value': True},
            ),
        ],
    ),
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.config(
    DRIVER_PRIORITY_NEW_RADAR_UI_MIN_VERSION={
        '__default__': {'enabled': True, 'major': 10, 'minor': 5},
    },
    PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST,
)
@pytest.mark.parametrize(
    'user_agent, expected_screen_items',
    [
        (_YANDEX_USER_AGENT, _get_priority_screen_items('Команда Яндекс')),
        (_YANGO_USER_AGENT, _get_priority_screen_items('Команда Yango')),
        (_AZ_TAXIMETER_USER_AGENT, _get_priority_screen_items('Команда AZ')),
    ],
)
async def test_localizer_overrides(
        driver_authorizer,
        taxi_driver_priority,
        dap,
        user_agent: str,
        expected_screen_items: List[Any],
):
    driver_authorizer.set_session('dbid_dev', 'session_0', 'uuid_dev')

    params = {
        'park_id': 'dbid_dev',
        'session': 'session_0',
        'lon': 37.6,
        'lat': 55.75,
    }

    headers = {'Accept-Language': 'ru', 'User-Agent': user_agent}
    expected_screen_response = {
        'ui': {'primary': {'items': expected_screen_items}},
    }

    taxi_driver_priority = dap.create_driver_wrapper(
        taxi_driver_priority, 'dbid_dev', 'uuid_dev', user_agent=user_agent,
    )

    await utils.ensure_polling_and_screen(
        taxi_driver_priority,
        headers,
        params,
        200,
        expected_screen_response,
        utils.polling_response(2, 0, 2),
        utils.polling_response(2, 0, 2),
    )
