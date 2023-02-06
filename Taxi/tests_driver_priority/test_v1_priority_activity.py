# pylint: disable=too-many-lines
import dataclasses
import datetime
import json
from typing import List
from typing import Optional

# pylint: disable=F0401,C5521
from dap_tools.dap import dap_fixture  # noqa: F401 C5521
# pylint: enable=F0401,C5521
import pytest

from tests_driver_priority import constants
from tests_driver_priority import db_tools
from tests_driver_priority import payload_utils
from tests_driver_priority import utils


_HOME_ZONE = 'moscow'
_IOS_USER_AGENT = 'Taximeter 1.0 ios'
_NOW = datetime.datetime(2019, 7, 15, 13, 57, 8, tzinfo=datetime.timezone.utc)

# duration in seconds
_MINUTE = 60
_HOUR = 60 * _MINUTE
_DAY = 24 * _HOUR


@dataclasses.dataclass
class Immunity:
    count: int


@dataclasses.dataclass
class Blocking:
    duration_seconds: int


@dataclasses.dataclass
class Benefits:
    immunity: Optional[Immunity]


@dataclasses.dataclass
class Punishments:
    blocking: Optional[Blocking]


@dataclasses.dataclass
class Level:
    priority: int
    scores_to_reach: int
    is_current: bool = False
    benefits: Optional[Benefits] = None
    punishments: Optional[Punishments] = None


@dataclasses.dataclass
class ScoresProgress:
    completion_score: int
    levels: List[Level]


_PUNISHMENTS = Punishments(Blocking(60 * 60))
_BENEFITS = Benefits(Immunity(1))


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    PRIORITY_ACTIVITY_FETCH_ENABLED=True,
    DRIVER_PRIORITY_SCREEN_TITLES_BY_VALUE={
        '__default__': {
            '__default__': {
                'description': 'priority_view.normal_priority_description',
                'payload': {
                    'header': 'priority_view.metrics.title',
                    'text': 'priority_view.metrics.default_description',
                },
                'thresholds': [],
                'title': 'priority_view.normal_priority_title',
            },
        },
    },
    ENABLE_PRIORITY_BY_EXPERIMENTS={'__default__': True},
    PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST,
)
@pytest.mark.driver_tags_match(
    dbid='dbid_dev',
    uuid='uuid_dev',
    udid='udid_dev',
    tags_info={'enable_exp': {'topics': ['priority']}},
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
            'region_id': '213',
        },
    ],
)
@pytest.mark.driver_taximeter(
    profile='dbid_dev_uuid_dev',
    platform='android',
    version='9.50',
    version_type='',
)
@pytest.mark.pgsql(
    'driver_priority',
    queries=db_tools.join_queries(
        [
            # activity priority
            db_tools.insert_priority(
                1,
                'activity',
                True,
                'activity',
                can_contain_activity_rule=True,
            ),
            db_tools.insert_priority_relation(constants.BR_ROOT, 1, False),
            db_tools.insert_preset(1, 1, 'default', _NOW, is_default=True),
            db_tools.insert_version(
                1,
                1,
                1,
                db_tools.ACTIVITY_RULE,
                db_tools.DEFAULT_ACHIEVED_PAYLOAD,
                _NOW,
                _NOW,
            ),
        ],
    ),
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.tvm2_ticket(
    {200: constants.TICKET_200_300, 300: constants.TICKET_300_200},
)
@pytest.mark.parametrize(
    'scores_progress, expected_scale_items_file_postfix',
    [
        pytest.param(
            ScoresProgress(
                0,
                [
                    Level(
                        -1,
                        -2,
                        punishments=Punishments(
                            Blocking(_DAY + _HOUR + _MINUTE),
                        ),
                    ),
                    Level(-1, -1),
                    Level(0, 0, is_current=True),
                    Level(1, 1),
                    Level(1, 2, benefits=_BENEFITS),
                ],
            ),
            'zero_priority.json',
            id='zero priority',
        ),
        pytest.param(
            ScoresProgress(
                1,
                [
                    Level(
                        -1,
                        -2,
                        punishments=Punishments(Blocking(_DAY + _HOUR)),
                    ),
                    Level(-1, -1),
                    Level(0, 0),
                    Level(1, 1, is_current=True, benefits=_BENEFITS),
                ],
            ),
            'max_priority.json',
            id='max priority',
        ),
        pytest.param(
            ScoresProgress(
                10,
                [
                    Level(
                        -1,
                        -2,
                        punishments=Punishments(Blocking(_DAY + _HOUR)),
                    ),
                    Level(-1, -1),
                    Level(0, 0),
                    Level(1, 1, is_current=True, benefits=_BENEFITS),
                ],
            ),
            'max_priority.json',
            id='max over priority',
        ),
        pytest.param(
            ScoresProgress(
                -2,
                [
                    Level(
                        -1,
                        -2,
                        is_current=True,
                        punishments=Punishments(Blocking(2 * _DAY + _MINUTE)),
                    ),
                    Level(-1, -1),
                    Level(0, 0),
                    Level(1, 1),
                    Level(1, 2, benefits=_BENEFITS),
                ],
            ),
            'min_priority.json',
            id='min priority',
        ),
        pytest.param(
            ScoresProgress(
                -3,
                [
                    Level(
                        -1,
                        -2,
                        is_current=True,
                        punishments=Punishments(Blocking(2 * _DAY + _MINUTE)),
                    ),
                    Level(-1, -1),
                    Level(0, 0),
                    Level(1, 1),
                    Level(1, 2, benefits=_BENEFITS),
                ],
            ),
            'min_priority.json',
            id='min over priority',
        ),
        pytest.param(
            ScoresProgress(
                -1,
                [
                    Level(
                        -1,
                        -2,
                        punishments=Punishments(Blocking(2 * _DAY + _MINUTE)),
                    ),
                    Level(-1, -1, is_current=True),
                    Level(0, 0),
                    Level(1, 1),
                    Level(1, 2, benefits=_BENEFITS),
                ],
            ),
            'min_non_block_priority.json',
            id='min non-block priority',
        ),
        pytest.param(
            ScoresProgress(
                1,
                [
                    Level(-1, -2, punishments=Punishments(Blocking(_DAY))),
                    Level(-1, -1),
                    Level(0, 0),
                    Level(1, 1, is_current=True),
                    Level(2, 3),
                    Level(2, 4, benefits=_BENEFITS),
                ],
            ),
            'positive_zero_completed_orders.json',
            id='positive sub priorities (zero completed orders)',
        ),
        pytest.param(
            ScoresProgress(
                2,
                [
                    Level(-1, -2, punishments=Punishments(Blocking(_HOUR))),
                    Level(-1, -1),
                    Level(0, 0),
                    Level(1, 1, is_current=True),
                    Level(2, 3),
                    Level(2, 4, benefits=_BENEFITS),
                ],
            ),
            'positive_one_completed_orders.json',
            id='positive sub priorities (one completed orders)',
        ),
        pytest.param(
            ScoresProgress(
                3,
                [
                    Level(-1, -2, punishments=Punishments(Blocking(_MINUTE))),
                    Level(-1, -1),
                    Level(0, 0),
                    Level(1, 1, is_current=True),
                    Level(2, 5),
                    Level(2, 6, benefits=_BENEFITS),
                ],
            ),
            'positive_two_completed_orders.json',
            id='positive sub priorities (two completed orders)',
        ),
        pytest.param(
            ScoresProgress(
                -1,
                [
                    Level(
                        -1,
                        -2,
                        punishments=Punishments(
                            Blocking(_HOUR + 30 * _MINUTE),
                        ),
                    ),
                    Level(-1, -1, is_current=True),
                    Level(0, 2),
                    Level(2, 4),
                    Level(2, 5, benefits=_BENEFITS),
                ],
            ),
            'negative_zero_completed_orders.json',
            id='negative sub priorities (zero completed orders)',
        ),
        pytest.param(
            ScoresProgress(
                0,
                [
                    Level(-1, -2, punishments=Punishments(Blocking(_HOUR))),
                    Level(-1, -1, is_current=True),
                    Level(0, 2),
                    Level(2, 4),
                    Level(2, 5, benefits=_BENEFITS),
                ],
            ),
            'negative_one_completed_orders.json',
            id='negative sub priorities (one completed orders)',
        ),
        pytest.param(
            ScoresProgress(
                1,
                [
                    Level(-1, -2, punishments=Punishments(Blocking(_HOUR))),
                    Level(-1, -1, is_current=True),
                    Level(0, 2),
                    Level(1, 3, benefits=Benefits(Immunity(1))),
                ],
            ),
            'negative_two_completed_orders.json',
            id='negative sub priorities (two completed orders)',
        ),
        pytest.param(
            ScoresProgress(
                99,
                [
                    Level(-1, -2, punishments=_PUNISHMENTS),
                    Level(-1, -1),
                    Level(0, 0),
                    Level(7, 97),
                    Level(7, 98),
                    Level(7, 99, is_current=True, benefits=_BENEFITS),
                ],
            ),
            'multi_equal_positive_priorities_top.json',
            id='multi equal positive priorities (top current)',
        ),
        pytest.param(
            ScoresProgress(
                98,
                [
                    Level(-1, -2, punishments=_PUNISHMENTS),
                    Level(-1, -1),
                    Level(0, 0),
                    Level(7, 97),
                    Level(7, 98, is_current=True),
                    Level(7, 99, benefits=_BENEFITS),
                ],
            ),
            'multi_equal_positive_priorities_middle.json',
            id='multi equal positive priorities (middle current)',
        ),
        pytest.param(
            ScoresProgress(
                97,
                [
                    Level(-1, -2, punishments=_PUNISHMENTS),
                    Level(-1, -1),
                    Level(0, 0),
                    Level(7, 97, is_current=True),
                    Level(7, 98),
                    Level(7, 99, benefits=_BENEFITS),
                ],
            ),
            'multi_equal_positive_priorities_bottom.json',
            id='some equal positive priorities (bottom current)',
        ),
        pytest.param(
            ScoresProgress(
                -1,
                [
                    Level(-10, -4, punishments=_PUNISHMENTS),
                    Level(-10, -3),
                    Level(-10, -2),
                    Level(-10, -1, is_current=True),
                    Level(0, 0),
                    Level(1, 1, benefits=_BENEFITS),
                ],
            ),
            'multi_equal_negative_priorities_top.json',
            id='multi equal negative priorities (top current)',
        ),
        pytest.param(
            ScoresProgress(
                -2,
                [
                    Level(-10, -4, punishments=_PUNISHMENTS),
                    Level(-10, -3),
                    Level(-10, -2, is_current=True),
                    Level(-10, -1),
                    Level(0, 0),
                    Level(1, 1, benefits=_BENEFITS),
                ],
            ),
            'multi_equal_negative_priorities_middle.json',
            id='multi equal negative priorities (middle current)',
        ),
        pytest.param(
            ScoresProgress(
                -3,
                [
                    Level(-10, -4, punishments=_PUNISHMENTS),
                    Level(-10, -3, is_current=True),
                    Level(-10, -2),
                    Level(-10, -1),
                    Level(0, 0),
                    Level(1, 1, benefits=_BENEFITS),
                ],
            ),
            'multi_equal_negative_priorities_bottom.json',
            id='multi equal negative priorities (bottom current)',
        ),
        pytest.param(
            ScoresProgress(
                1,
                [
                    Level(-1, -2, punishments=Punishments(Blocking(1))),
                    Level(-1, -1),
                    Level(0, 0),
                    Level(1, 1, is_current=True),
                ],
            ),
            'no_benefits.json',
            id='no benefits at all',
        ),
        pytest.param(
            ScoresProgress(
                2,
                [
                    Level(-1, -2, punishments=Punishments(Blocking(1))),
                    Level(-1, -1),
                    Level(0, 0),
                    Level(1, 1),
                    Level(1, 2, is_current=True, benefits=_BENEFITS),
                    Level(1, 3, benefits=_BENEFITS),
                ],
            ),
            'multi_benefits.json',
            id='multi benefits',
        ),
    ],
)
async def test_activity_payload(
        taxi_driver_priority,
        driver_authorizer,
        dap,
        mockserver,
        testpoint,
        load_json,
        scores_progress,
        expected_scale_items_file_postfix,
):
    park_id = 'dbid_dev'
    uuid = 'uuid_dev'

    @mockserver.json_handler(
        '/driver-metrics-storage/v1/completion_scores/progress',
    )
    def _dms_handler(request):
        assert request.json['unique_driver_id'] == 'udid_dev'
        assert request.json['tariff_zone'] == _HOME_ZONE
        assert request.json['tags'] == ['enable_exp']

        dms_response = dataclasses.asdict(scores_progress)
        return mockserver.make_response(json.dumps(dms_response), 200)

    id_index = 0

    @testpoint('id_generate')
    def _id_generate(arg):
        nonlocal id_index
        id_index += 1
        return {'id': 'generated_id_' + str(id_index)}

    driver_authorizer.set_session(park_id, 'session_0', uuid)
    taxi_driver_priority = dap.create_driver_wrapper(
        taxi_driver_priority, park_id, uuid, user_agent=_IOS_USER_AGENT,
    )

    header = {
        'Accept-Language': constants.DEFAULT_ACCEPT_LANGUAGE,
        'User-Agent': _IOS_USER_AGENT,
    }

    params = {
        'park_id': 'dbid_dev',
        'session': 'session_0',
        'lon': 37.6,
        'lat': 55.75,
    }

    current_level = next(
        (level for level in scores_progress.levels if level.is_current),
    )

    next_scores_priority = next(
        (
            level.scores_to_reach
            - max(
                scores_progress.completion_score,
                scores_progress.levels[1].scores_to_reach,
            )
            for level in scores_progress.levels
            if level.priority > current_level.priority
        ),
        None,
    )

    subtitle = (
        str(next_scores_priority) + ' заказ(а/ов) до повышения'
        if next_scores_priority
        else 'Достигнут максимальный уровень'
    )

    expected_activity_items = load_json(
        'screen_' + expected_scale_items_file_postfix,
    )
    items = [
        payload_utils.ui_header_item(),
        payload_utils.ui_priority_item(
            current_level.priority,
            'Активность',
            subtitle,
            is_matched=True,
            new_icon=True,
            payload=payload_utils.get_activity_payload(
                expected_activity_items,
            ),
        ),
    ]
    expected_screen_response = {'ui': {'primary': {'items': items}}}
    expected_polling_response = utils.polling_response(
        current_level.priority, 0, max(current_level.priority, 0),
    )

    await utils.ensure_polling_and_screen(
        taxi_driver_priority,
        header,
        params,
        200,
        expected_screen_response,
        expected_polling_response,
        expected_polling_response,
    )

    params = {'park_id': park_id, 'uuid': uuid, 'lon': 37.6, 'lat': 55.75}
    expected_activity_scaler = load_json(
        'diagnostics_' + expected_scale_items_file_postfix,
    )
    response = await taxi_driver_priority.get(
        constants.DIAGNOSTICS_URL,
        params=params,
        headers=constants.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['activity_scaler'] == expected_activity_scaler
