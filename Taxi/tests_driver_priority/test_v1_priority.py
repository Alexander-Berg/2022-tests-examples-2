# pylint: disable=too-many-lines
import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

# pylint: disable=F0401,C5521
from dap_tools.dap import dap_fixture  # noqa: F401 C5521
# pylint: enable=F0401,C5521
import pytest

from tests_driver_priority import constants
from tests_driver_priority import db_tools
from tests_driver_priority import payload_utils
from tests_driver_priority import utils
from tests_driver_priority.plugins import mock_priority_data as pd


_IOS_USER_AGENT = 'Taximeter 1.0 ios'
_NEW_RANKED_USER_AGENT = 'Taximeter 9.21 (1234)'
_NEW_RADAR_UI_USER_AGENT = 'Taximeter 10.05 (1240)'
_IOS_RANKED_USER_AGENT = 'Taximeter 1.1 ios'
_YANGO_USER_AGENT = 'Taximeter 10.05'
_AZ_TAXIMETER_USER_AGENT = 'Taximeter-Yango 10.05'

_HOME_ZONE = 'moscow'

_COLOR_WHITE = '#FFFFFF'
_COLOR_LIGHT_GRAY = '#C4C2BE'
_COLOR_GRAY = '#9E9B98'
_COLOR_DARK_GRAY = '#21201F'
_COLOR_LIGHT_RED = '#F5523A'
_COLOR_DARK_RED = '#FA3E2C'
_COLOR_YELLOW = '#FCB000'

_NOW = datetime.datetime(2019, 7, 15, 13, 57, 8, tzinfo=datetime.timezone.utc)

_SINGLE = pd.PriorityRuleType.Single
_RANKED = pd.PriorityRuleType.Ranked
_EXCLUDED = pd.PriorityRuleType.Excluded
_TAG_RULE = pd.RuleType.TagRule
_RATING_RULE = pd.RuleType.RatingRule
_CAR_YEAR = pd.RuleType.CarYearRule

_LOYALTY_RANKED_RULE: List[payload_utils.RankedPriority] = [
    payload_utils.RankedPriority(1, 'bronze', 'Бронза'),
    payload_utils.RankedPriority(3, 'gold', 'Золото'),
    payload_utils.RankedPriority(7, 'platinum', 'Платина'),
]


# pylint: disable=too-many-arguments
@pytest.mark.config(PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST)
@pytest.mark.driver_tags_match(
    dbid='abc_0', uuid='uuid_0', tags_info={'tag_0': {'topics': ['priority']}},
)
@pytest.mark.parametrize(
    'request_headers, request_params, expected_code, expected_screen_response,'
    'expected_polling_response, expected_value_response',
    [
        (
            {},
            {},
            400,
            {'code': '400', 'message': 'Missing lon in query'},
            {'code': '400', 'message': 'Missing lon in query'},
            {
                'code': '400',
                'message': 'Missing/empty header "X-Driver-Session"',
            },
        ),
        (
            constants.DEFAULT_HEADERS,
            {'park_id': 'park_0', 'lon': 1.0, 'lat': 1.0},
            400,
            {
                'code': '400',
                'message': 'Missing/empty header "X-Driver-Session"',
            },
            {
                'code': '400',
                'message': 'Missing/empty header "X-Driver-Session"',
            },
            {
                'code': '400',
                'message': 'Missing/empty header "X-Driver-Session"',
            },
        ),
        (
            constants.DEFAULT_HEADERS,
            {
                'park_id': 'park_0',
                'session': 'session_0',
                'lon': 1.0,
                'lat': 1.0,
            },
            404,
            {'code': '404', 'message': 'Not Found'},
            {'code': '404', 'message': 'Not Found'},
            {'code': '404', 'message': 'Not Found'},
        ),
        (
            constants.DEFAULT_HEADERS,
            {
                'park_id': 'park_0',
                'session': 'session_0',
                'lon': 37.6,
                'lat': 55.75,
            },
            200,
            {'ui': {'primary': {'items': [payload_utils.ui_header_item()]}}},
            utils.polling_response(0, 0, 0),
            utils.polling_response(0, 0, 0),
        ),
    ],
)
@pytest.mark.tvm2_ticket(
    {200: constants.TICKET_200_300, 300: constants.TICKET_300_200},
)
async def test_request_params(
        taxi_driver_priority,
        driver_authorizer,
        driver_trackstory_mock,
        dap,
        request_headers: Dict[str, Any],
        request_params: Dict[str, Any],
        expected_code: int,
        expected_screen_response,
        expected_polling_response,
        expected_value_response,
):
    driver_authorizer.set_session('park_0', 'session_0', 'driver_0')

    lon = request_params.get('lon')
    lat = request_params.get('lat')
    if lon is not None and lat is not None:
        driver_trackstory_mock.positions['park_0_driver_0'] = {
            'lon': lon,
            'lat': lat,
            'timestamp': int(_NOW.timestamp()),
        }

    call_value_handler = False
    if 'session' in request_params:
        call_value_handler = True
        taxi_driver_priority = dap.create_driver_wrapper(
            taxi_driver_priority,
            'park_0',
            'driver_0',
            user_agent=constants.DEFAULT_USER_AGENT,
        )

    await utils.ensure_polling_and_screen(
        taxi_driver_priority,
        request_headers,
        request_params,
        expected_code,
        expected_screen_response,
        expected_polling_response,
        expected_value_response,
        call_value_handler=call_value_handler,
    )


@pytest.mark.parametrize(
    'park, session, expected_code',
    [
        (None, 'session_valid', 400),
        ('park_valid', None, 400),
        ('park_0', 'session_0', 401),
        ('', 'session_valid', 400),
        ('park_valid', '', 400),
        ('park_valid', 'session_valid', 200),
    ],
)
@pytest.mark.tvm2_ticket(
    {200: constants.TICKET_200_300, 300: constants.TICKET_300_200},
)
@pytest.mark.driver_trackstory(
    positions={
        'park_valid_driver_id': {
            'lon': 37.6,
            'lat': 55.75,
            'timestamp': int(_NOW.timestamp()),
        },
    },
)
@pytest.mark.config(PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST)
async def test_authorization(
        taxi_driver_priority,
        driver_authorizer,
        park: str,
        session: str,
        expected_code: int,
):
    driver_authorizer.set_session('park_valid', 'session_valid', 'driver_id')

    params: Dict[str, Any] = {'lon': 37.6, 'lat': 55.75}
    if session is not None:
        params['session'] = session
    if park is not None:
        params['park_id'] = park

    await utils.ensure_polling_and_screen(
        taxi_driver_priority,
        constants.DEFAULT_HEADERS,
        params,
        expected_code,
        None,
        None,
        None,
        call_value_handler=False,
    )


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.driver_tags_match(
    dbid='dbid_dev',
    uuid='uuid_dev',
    tags_info={'frauder': {'topics': ['topic_tst', 'priority']}},
)
@pytest.mark.driver_tags_match(
    dbid='dbid_developer',
    uuid='uuid_developer',
    tags_info={'developer': {'topics': ['topic_tst', 'priority']}},
)
@pytest.mark.parametrize(
    'park_id, session, uuid, expected_code, expected_response',
    [
        (
            'dbid_dev',
            'session_dev',
            'uuid_dev',
            500,
            {
                'code': '500',
                'message': (
                    'Translation [taximeter_messages]'
                    '[priority_view.priorities.frauder.frauder_text]'
                ),
            },
        ),
        (
            'dbid_developer',
            'session_dev',
            'uuid_developer',
            500,
            {
                'code': '500',
                'message': (
                    'Translation [taximeter_messages]'
                    '[priority_view.priorities.not_existing.developer_text]'
                ),
            },
        ),
    ],
)
@pytest.mark.config(
    ENABLE_PRIORITY_BY_EXPERIMENTS={'__default__': True},
    PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST,
)
@pytest.mark.priority_data(
    now=_NOW,
    data=[
        pd.PriorityData(
            'frauder',
            [
                pd.PrioritySettings(
                    ['__default__'],
                    10,
                    pd.PriorityRule(
                        _SINGLE, [(_TAG_RULE, 'frauder', 10, None)],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                ),
            ],
        ),
        pd.PriorityData(
            'job',
            [
                pd.PrioritySettings(
                    ['__default__'],
                    10,
                    pd.PriorityRule(
                        _SINGLE, [(_TAG_RULE, 'developer', 10, None)],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                ),
            ],
            tanker_keys_prefix='not_existing',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.tvm2_ticket(
    {200: constants.TICKET_200_300, 300: constants.TICKET_300_200},
)
async def test_no_localizations(
        taxi_driver_priority,
        driver_authorizer,
        driver_trackstory_mock,
        park_id: str,
        session: str,
        uuid: str,
        expected_code: int,
        expected_response: Dict[str, Any],
):
    driver_authorizer.set_session(park_id, session, uuid)
    driver_trackstory_mock.positions[f'{park_id}_{uuid}'] = {
        'lon': 37.6,
        'lat': 55.75,
        'timestamp': int(_NOW.timestamp()),
    }

    response = await taxi_driver_priority.get(
        constants.SCREEN_URL,
        headers=constants.DEFAULT_HEADERS,
        params={
            'park_id': park_id,
            'session': session,
            'lon': 37.6,
            'lat': 55.75,
        },
    )
    assert response.json() == expected_response
    assert response.status_code == expected_code


_GOT_NO_LOYALTY_PAYLOAD = {
    'type': 'navigate_priority_details',
    'ui': {
        'primary': {
            'items': [
                {
                    'horizontal_divider_type': 'none',
                    'subtitle': 'Вы еще не участвуете в программе лояльности',
                    'gravity': 'left',
                    'type': 'header',
                },
                {
                    'horizontal_divider_type': 'none',
                    'text': 'Но вы можете это исправить',
                    'type': 'text',
                },
                {
                    'type': 'header',
                    'gravity': 'left',
                    'subtitle': 'Преимущества',
                    'subtitle_size': 'small',
                    'horizontal_divider_type': 'none',
                },
                {
                    'horizontal_divider_type': 'none',
                    'text': 'следующие',
                    'type': 'text',
                },
                {
                    'type': 'tip_detail',
                    'title': 'Одна комиссия',
                    'subtitle': 'только Яндексу',
                    'primary_max_lines': 1,
                    'secondary_max_lines': 1,
                    'left_tip': {'background_color': '#fcb000', 'text': '1'},
                    'horizontal_divider_type': 'bottom_icon',
                },
                {
                    'type': 'tip_detail',
                    'title': 'Легальный доход',
                    'primary_max_lines': 2,
                    'left_tip': {'background_color': '#fcb000', 'text': '2'},
                    'horizontal_divider_type': 'bottom_icon',
                },
            ],
        },
    },
}


_LOYALTY_ACHIEVED = {
    'main_title': 'loyal',
    'constructor': [{'text': 'loyal_explanation'}],
    'button': {
        'text': 'button_explanation',
        'action': {'url': 'ya.ru', 'title': 'link_title', 'is_external': True},
    },
}
_LOYALTY_ACHIEVABLE = {
    'main_title': 'not_loyal',
    'constructor': [
        {'text': 'not_loyal_explanation'},
        {
            'title': 'pros',
            'text': 'pros_explanation',
            'numbered_list': [
                {
                    'title': 'one_commission',
                    'subtitle': 'one_commission_explanation',
                },
                {'title': 'legal_income'},
            ],
        },
    ],
}
_JOB_ACHIEVED = {
    'main_title': 'job',
    'constructor': [{'text': 'job_explanation'}],
    'button': {
        'text': 'button_explanation',
        'action': {'url': 'ya.ru', 'title': 'link_title', 'is_external': True},
    },
}


# pylint: disable=too-many-arguments
@pytest.mark.driver_tags_match(
    dbid='dbid_dev',
    uuid='uuid_dev',
    tags_info={
        'developer': {
            'ttl': '2019-07-17T13:56:07.000+0000',
            'topics': ['priority'],
        },
        'yandex': {
            'ttl': '2019-07-16T13:56:07.000+0000',
            'topics': ['priority'],
        },
        'gold': {'topics': ['commissions', 'priority']},
    },
)
@pytest.mark.driver_tags_match(
    dbid='dbid_mail',
    uuid='uuid_mail',
    tags_info={
        'selfemployed': {
            'ttl': '2019-07-15T13:57:07.000+0000',
            'topics': ['priority'],
        },
        'mail_ru': {'topics': ['priority']},
        'developer': {
            'ttl': '2019-07-15T13:57:09.000+0000',
            'topics': ['priority'],
        },
    },
)
@pytest.mark.driver_tags_match(
    dbid='dbid_eats',
    uuid='uuid_eats',
    tags_info={
        'eats_courier': {'topics': ['priority']},
        'developer': {
            'ttl': '2019-07-15T13:57:09.000+0000',
            'topics': ['priority'],
        },
        'selfemployed': {
            'ttl': '2019-07-15T13:57:07.000+0000',
            'topics': ['priority'],
        },
        'mail_ru': {'topics': ['priority']},
    },
)
@pytest.mark.driver_tags_match(
    dbid='dbid_bad',
    uuid='uuid_bad',
    tags_info={
        'dirty_car': {
            'ttl': '2019-07-15T13:57:09.000+0000',
            'topics': ['priority'],
        },
    },
)
@pytest.mark.driver_tags_match(
    dbid='dbid_cant_have_clean_car',
    uuid='uuid_cant_have_clean_car',
    tags_info={
        'i_cant_have_clean_car': {
            'ttl': '2019-07-15T13:57:09.000+0000',
            'topics': ['priority'],
        },
        'clean_car': {
            'ttl': '2019-07-15T13:57:09.000+0000',
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
        {
            'name': 'br_mytishchi',
            'name_en': 'Mytishchi',
            'name_ru': 'Мытищи',
            'node_type': 'node',
            'parent_name': 'br_moscow_adm',
            'tariff_zones': ['mytishchi'],
            'region_id': '10740',
        },
        {
            'name': 'br_tula',
            'name_en': 'Tula',
            'name_ru': 'Тула',
            'node_type': 'node',
            'parent_name': 'br_moscow_adm',
            'tariff_zones': ['tula'],
            'region_id': '15',
        },
    ],
)
@pytest.mark.config(PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST)
@pytest.mark.pgsql(
    'driver_priority',
    queries=db_tools.join_queries(
        [
            # company
            db_tools.insert_priority(0, 'company', True, 'company'),
            db_tools.insert_priority_relation('moscow', 0, False),
            db_tools.insert_priority_relation('br_mytishchi', 0, False),
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
            db_tools.insert_preset(1, 0, 'company_br_mytishchi', _NOW),
            db_tools.insert_preset_relation('br_mytishchi', 1),
            db_tools.insert_version(
                1,
                1,
                20,
                {'single_rule': db_tools.make_tag_rule('mail_ru', 1)},
                db_tools.EMPTY_PAYLOAD,
                _NOW,
                _NOW,
                achievable_condition={'value': False},
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
            # employment
            db_tools.insert_priority(1, 'employment', True, 'employment'),
            db_tools.insert_priority_relation('moscow', 1, False),
            db_tools.insert_preset(3, 1, 'employment_moscow', _NOW),
            db_tools.insert_preset_relation('moscow', 3),
            db_tools.insert_version(
                3,
                3,
                30,
                {
                    'excluding_rule': [
                        db_tools.make_tag_rule('individual_enterpreneur', 2),
                        db_tools.make_tag_rule('selfemployed', 1),
                    ],
                },
                db_tools.EMPTY_PAYLOAD,
                _NOW,
                _NOW,
                temporary_condition={'value': True},
                achievable_condition={'value': True},
            ),
            db_tools.insert_preset(
                4, 1, 'employment_default', _NOW, is_default=True,
            ),
            db_tools.insert_version(
                4,
                4,
                0,
                db_tools.EMPTY_RULE,
                db_tools.EMPTY_PAYLOAD,
                _NOW,
                _NOW,
                disabled_condition={'value': True},
            ),
            # loyalty
            db_tools.insert_priority(2, 'loyalty', True, 'loyalty'),
            db_tools.insert_priority_relation('br_root', 2, False),
            db_tools.insert_preset(5, 2, 'loyalty_moscow', _NOW),
            db_tools.insert_preset_relation('moscow', 5),
            db_tools.insert_version(
                5,
                5,
                40,
                {
                    'ranked_rule': [
                        db_tools.make_tag_rule('bronze', 1),
                        db_tools.make_tag_rule('gold', 3),
                        db_tools.make_tag_rule('platinum', 7),
                    ],
                },
                _LOYALTY_ACHIEVED,
                _NOW,
                _NOW,
                achievable_condition={'value': True},
                achievable_payload=_LOYALTY_ACHIEVABLE,
            ),
            db_tools.insert_preset(
                6, 2, 'loyalty_default', _NOW, is_default=True,
            ),
            db_tools.insert_version(
                6,
                6,
                0,
                db_tools.EMPTY_RULE,
                _LOYALTY_ACHIEVED,
                _NOW,
                _NOW,
                disabled_condition={'value': True},
                achievable_payload=_LOYALTY_ACHIEVABLE,
            ),
            # stocks
            db_tools.insert_priority(3, 'stocks', True, 'stocks'),
            db_tools.insert_priority_relation('moscow', 3, False),
            db_tools.insert_preset(7, 3, 'stocks_moscow', _NOW),
            db_tools.insert_preset_relation('moscow', 7),
            db_tools.insert_version(
                7,
                7,
                50,
                {'single_rule': db_tools.make_tag_rule('stocks_holder', 5)},
                db_tools.EMPTY_PAYLOAD,
                _NOW,
                _NOW,
                achievable_condition={'all_of': ['yandex', 'developer']},
            ),
            db_tools.insert_preset(
                8, 3, 'stocks_default', _NOW, is_default=True,
            ),
            db_tools.insert_version(
                8,
                8,
                0,
                db_tools.EMPTY_RULE,
                db_tools.EMPTY_PAYLOAD,
                _NOW,
                _NOW,
                disabled_condition={'value': True},
            ),
            # recently_selfemployed
            db_tools.insert_priority(
                4, 'recently_selfemployed', True, 'recently_selfemployed',
            ),
            db_tools.insert_priority_relation('moscow', 4, False),
            db_tools.insert_preset(9, 4, 'stocks_moscow', _NOW),
            db_tools.insert_preset_relation('moscow', 9),
            db_tools.insert_version(
                9,
                9,
                60,
                {
                    'single_rule': db_tools.make_tag_rule(
                        'selfemployed_6m_or_less', 6,
                    ),
                },
                db_tools.EMPTY_PAYLOAD,
                _NOW,
                _NOW,
                achievable_condition={
                    'none_of': ['selfemployed', 'individual_entrepreneur'],
                },
            ),
            db_tools.insert_preset(
                10, 4, 'stocks_default', _NOW, is_default=True,
            ),
            db_tools.insert_version(
                10,
                10,
                0,
                db_tools.EMPTY_RULE,
                db_tools.EMPTY_PAYLOAD,
                _NOW,
                _NOW,
                disabled_condition={'value': True},
            ),
            # dirty_car
            db_tools.insert_priority(5, 'dirty_car', True, 'dirty_car'),
            db_tools.insert_priority_relation('moscow', 5, False),
            db_tools.insert_preset(11, 5, 'dirty_car_moscow', _NOW),
            db_tools.insert_preset_relation('moscow', 11),
            db_tools.insert_version(
                11,
                11,
                10,
                {'single_rule': db_tools.make_tag_rule('dirty_car', -1)},
                db_tools.EMPTY_PAYLOAD,
                _NOW,
                _NOW,
                achievable_condition={'value': False},
            ),
            db_tools.insert_preset(
                12, 5, 'dirty_car_default', _NOW, is_default=True,
            ),
            db_tools.insert_version(
                12,
                12,
                0,
                db_tools.EMPTY_RULE,
                db_tools.EMPTY_PAYLOAD,
                _NOW,
                _NOW,
                disabled_condition={'value': True},
            ),
            # clean_car
            db_tools.insert_priority(6, 'clean_car', True, 'clean_car'),
            db_tools.insert_priority_relation('moscow', 6, False),
            db_tools.insert_preset(13, 6, 'clean_car_moscow', _NOW),
            db_tools.insert_preset_relation('moscow', 13),
            db_tools.insert_version(
                13,
                13,
                80,
                {'single_rule': db_tools.make_tag_rule('clean_car', 1)},
                db_tools.EMPTY_PAYLOAD,
                _NOW,
                _NOW,
                disabled_condition={'any_of': ['i_cant_have_clean_car']},
            ),
            db_tools.insert_preset(
                14, 6, 'clean_car_default', _NOW, is_default=True,
            ),
            db_tools.insert_version(
                14,
                14,
                0,
                db_tools.EMPTY_RULE,
                db_tools.EMPTY_PAYLOAD,
                _NOW,
                _NOW,
                disabled_condition={'value': True},
            ),
            # job
            db_tools.insert_priority(7, 'job', True, 'job'),
            db_tools.insert_priority_relation('br_root', 7, False),
            db_tools.insert_preset(15, 7, 'job_moscow', _NOW),
            db_tools.insert_preset_relation('moscow', 15),
            db_tools.insert_version(
                15,
                15,
                10,
                {'single_rule': db_tools.make_tag_rule('developer', 2)},
                db_tools.EMPTY_PAYLOAD,
                _NOW,
                _NOW,
                achievable_condition={'value': True},
                temporary_condition={'value': True},
            ),
            db_tools.insert_preset(16, 7, 'job_br_tula', _NOW),
            db_tools.insert_preset_relation('br_tula', 16),
            db_tools.insert_version(
                16,
                16,
                10,
                {'single_rule': db_tools.make_tag_rule('developer', 2)},
                _JOB_ACHIEVED,
                _NOW,
                _NOW,
                achievable_condition={'value': True},
                temporary_condition={'value': True},
            ),
            db_tools.insert_preset(
                17, 7, 'job_default', _NOW, is_default=True,
            ),
            db_tools.insert_version(
                17,
                17,
                0,
                {'single_rule': db_tools.make_tag_rule('developer', 2)},
                db_tools.EMPTY_PAYLOAD,
                _NOW,
                _NOW,
                achievable_condition={'value': True},
                temporary_condition={'value': True},
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'park_id, uuid, lon, lat, enable_moscow, user_agent, '
    'expected_hidden_priorities, expected_screen_response_items, '
    'summary_values',
    [
        (
            'dbid_dev',
            'uuid_dev',
            37.6,
            55.75,
            False,
            constants.DEFAULT_USER_AGENT,
            [],
            [
                payload_utils.ui_header_item(
                    'Наивысший приоритет', 'Так держать',
                ),
                payload_utils.ui_priority_item(
                    3,
                    'Золото',
                    'Программа лояльности: Золото',
                    is_matched=True,
                    payload=payload_utils.get_payload('Лояльность', 'есть'),
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    2, 'Команда Яндекс', None, is_matched=True, new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    2,
                    'Разработчик',
                    'Истекает через 1 д. 23 ч.',
                    is_matched=True,
                    is_temporary=True,
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    6,
                    'Самозанятый с недавнего ' 'времени',
                    None,
                    is_matched=False,
                    is_disabled=True,
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    5,
                    'Владелец опционов',
                    None,
                    is_matched=False,
                    is_disabled=True,
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    4,  # 4 = 7 (platinum) - 3 (gold)
                    'Платина',
                    'Программа лояльности: Платина',
                    is_matched=False,
                    is_disabled=True,
                    payload=_GOT_NO_LOYALTY_PAYLOAD,
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    1,
                    'Смена формы занятости',
                    None,
                    is_matched=False,
                    is_disabled=True,
                    new_icon=True,
                ),
            ],
            utils.summary_values(5, 2, 23),
        ),
        (
            'dbid_dev',
            'uuid_dev',
            37.6,
            55.75,
            False,
            _NEW_RADAR_UI_USER_AGENT,
            [],
            [
                payload_utils.ui_header_item(
                    'Наивысший приоритет', 'Так держать', is_new_radar_ui=True,
                ),
                payload_utils.ui_priority_item(
                    3,
                    'Золото',
                    'Программа лояльности: Золото',
                    is_matched=True,
                    payload=payload_utils.get_payload('Лояльность', 'есть'),
                    new_icon=True,
                    use_new_divider_type=True,
                ),
                payload_utils.ui_priority_item(
                    2, 'Команда Яндекс', None, is_matched=True, new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    2,
                    'Разработчик',
                    'Истекает через 1 д. 23 ч.',
                    is_matched=True,
                    is_temporary=True,
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    6,
                    'Самозанятый с недавнего времени',
                    None,
                    is_matched=False,
                    is_disabled=True,
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    5,
                    'Владелец опционов',
                    None,
                    is_matched=False,
                    is_disabled=True,
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    4,  # 4 = 7 (platinum) - 3 (gold)
                    'Платина',
                    'Программа лояльности: Платина',
                    is_matched=False,
                    is_disabled=True,
                    payload=_GOT_NO_LOYALTY_PAYLOAD,
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    1,
                    'Смена формы занятости',
                    None,
                    is_matched=False,
                    is_disabled=True,
                    new_icon=True,
                ),
            ],
            utils.summary_values(5, 2, 23),
        ),
        (
            'dbid_mail',
            'uuid_mail',
            37.6,
            55.75,
            False,
            constants.DEFAULT_USER_AGENT,
            ['company'],
            [
                payload_utils.ui_header_item(
                    'Высокий приоритет', 'Все заказы для вас одного',
                ),
                payload_utils.ui_priority_item(
                    1,
                    'Самозанятый',
                    'Истекает через 1 мин.',
                    is_matched=True,
                    is_temporary=True,
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    2,
                    'Разработчик',
                    'Истекает через 1 мин.',
                    is_matched=True,
                    is_temporary=True,
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    1,
                    'Бронза',
                    'Программа лояльности: Бронза',
                    is_matched=False,
                    is_disabled=True,
                    payload=_GOT_NO_LOYALTY_PAYLOAD,
                    new_icon=True,
                ),
            ],
            utils.summary_values(0, 3, 4),
        ),
        (
            'dbid_mail',
            'uuid_mail',
            37.6,
            54.2,  # Tula region
            True,
            constants.DEFAULT_USER_AGENT,
            [],
            [
                payload_utils.ui_header_item(),
                payload_utils.ui_priority_item(
                    2,  # br_root priority
                    'Разработчик',
                    'Истекает через 1 мин.',
                    is_matched=True,
                    is_temporary=True,
                    payload=payload_utils.get_payload(
                        'Разработчик', 'на месте',
                    ),
                ),
            ],
            utils.summary_values(0, 2, 2),
        ),
        pytest.param(
            'dbid_eats',
            'uuid_eats',
            37.6,
            54.2,  # Tula region
            True,
            constants.DEFAULT_USER_AGENT,
            [],
            [
                payload_utils.ui_header_item(
                    'Приоритет еды',
                    'Описание приоритета еды',
                    payload_header='Заголовок пейлоада приоритета еды',
                    payload_text='Текст пейлоада приоритета еды',
                ),
            ],
            utils.summary_values(0, 0, 0),
            id='test eats priority disabling',
        ),
        pytest.param(
            'dbid_eats',
            'uuid_eats',
            37.6,
            54.2,  # Tula region
            True,
            constants.DEFAULT_USER_AGENT,
            [],
            [
                payload_utils.ui_header_item(
                    'Приоритет еды',
                    'Описание приоритета еды',
                    payload_header='Заголовок пейлоада приоритета еды',
                    payload_text='Текст пейлоада приоритета еды',
                ),
                payload_utils.ui_priority_item(
                    2,  # br_root priority
                    'Разработчик',
                    'Истекает через 1 мин.',
                    is_matched=True,
                    is_temporary=True,
                    payload=payload_utils.get_payload(
                        'Разработчик', 'на месте',
                    ),
                ),
            ],
            utils.summary_values(0, 2, 2),
            marks=[
                pytest.mark.config(
                    DRIVER_PRIORITY_PROFESSIONS_BY_PRIORITY_NAMES={
                        '__default__': ['taxi'],
                        'job': ['eats_courier'],
                    },
                ),
            ],
            id='test eats priority switcher',
        ),
        (
            'dbid_mail',
            'uuid_mail',
            37.738,
            56.05,  # Mytishchi region
            True,
            constants.DEFAULT_USER_AGENT,
            [],
            [
                payload_utils.ui_header_item(
                    'Наивысший приоритет', 'Так держать',
                ),  # special title for br_mytishchi
                payload_utils.ui_priority_item(
                    1,
                    'Команда Мейл.ру',
                    None,  # has subtitle key with empty translation
                    is_matched=True,
                ),
                payload_utils.ui_priority_item(
                    2,  # br_root priority
                    'Разработчик',
                    'Истекает через 1 мин.',
                    is_matched=True,
                    is_temporary=True,
                    new_icon=True,
                ),
            ],
            utils.summary_values(1, 2, 3),
        ),
        (
            'dbid_excluded_by_experiment',
            'uuid_unknown',
            37.6,
            55.75,
            True,
            constants.DEFAULT_USER_AGENT,
            [],
            [payload_utils.ui_header_item()],
            utils.summary_values(0, 0, 0),
        ),
        (
            'dbid_bad',
            'uuid_bad',
            37.6,
            55.75,
            True,
            _IOS_USER_AGENT,
            [],
            [
                payload_utils.ui_header_item(
                    'Низкий приоритет', 'Не все заказы для вас одного',
                ),
                payload_utils.ui_priority_item(
                    -1, 'Грязная машина', None, is_matched=True, new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    6,
                    'Самозанятый с недавнего времени',
                    None,
                    is_matched=False,
                    is_disabled=True,
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    1,
                    'Бронза',
                    'Программа лояльности: Бронза',
                    is_matched=False,
                    is_disabled=True,
                    payload=_GOT_NO_LOYALTY_PAYLOAD,
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    1,
                    'Смена формы занятости',
                    None,
                    is_matched=False,
                    is_disabled=True,
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    2,
                    'Разработчик',
                    None,
                    is_matched=False,
                    is_disabled=True,
                    new_icon=True,
                ),
            ],
            utils.summary_values(-1, 0, 10),
        ),
        (
            'dbid_mail',
            'uuid_mail',
            37.6,
            55.75,
            True,  # Experiment exclude
            constants.DEFAULT_USER_AGENT,
            [],
            [payload_utils.ui_header_item()],
            utils.summary_values(0, 0, 0),
        ),
        (
            'dbid_cant_have_clean_car',
            'uuid_cant_have_clean_car',
            37.6,
            55.75,
            True,
            constants.DEFAULT_USER_AGENT,
            [],
            [
                payload_utils.ui_header_item(
                    'Высокий приоритет', 'Все заказы для вас одного',
                ),
                payload_utils.ui_priority_item(
                    6,
                    'Самозанятый с недавнего времени',
                    None,
                    is_matched=False,
                    is_disabled=True,
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    1,
                    'Бронза',
                    'Программа лояльности: Бронза',
                    is_matched=False,
                    is_disabled=True,
                    payload=_GOT_NO_LOYALTY_PAYLOAD,
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    1,
                    'Смена формы занятости',
                    None,
                    is_matched=False,
                    is_disabled=True,
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    2,
                    'Разработчик',
                    None,
                    is_matched=False,
                    is_disabled=True,
                    new_icon=True,
                ),
            ],
            utils.summary_values(0, 0, 10),
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.tvm2_ticket(
    {200: constants.TICKET_200_300, 300: constants.TICKET_300_200},
)
async def test_priorities(
        taxi_driver_priority,
        driver_trackstory_mock,
        driver_profiles_mocks,
        driver_authorizer,
        testpoint,
        dap,
        park_id: str,
        uuid: str,
        lon: float,
        lat: float,
        enable_moscow: bool,
        user_agent: str,
        expected_hidden_priorities,
        expected_screen_response_items,
        summary_values,
        taxi_config,
        driver_ratings_mocks,
        mock_fleet_vehicles,
):
    @testpoint('hide_zero_priority')
    def _hide_zero_priority(data):
        assert data['name'] in expected_hidden_priorities

    taxi_config.set(
        ENABLE_PRIORITY_BY_EXPERIMENTS={
            '__default__': False,
            'moscow': enable_moscow,
        },
    )

    driver_authorizer.set_session(park_id, 'session_0', uuid)
    driver_trackstory_mock.positions[f'{park_id}_{uuid}'] = {
        'lon': lon,
        'lat': lat,
        'timestamp': int(_NOW.timestamp()),
    }
    taxi_driver_priority = dap.create_driver_wrapper(
        taxi_driver_priority, park_id, uuid, user_agent=user_agent,
    )

    params = {
        'park_id': park_id,
        'session': 'session_0',
        'lon': lon,
        'lat': lat,
    }
    headers = {
        'Accept-Language': constants.DEFAULT_ACCEPT_LANGUAGE,
        'User-Agent': user_agent,
    }
    expected_screen_response = {
        'ui': {'primary': {'items': expected_screen_response_items}},
    }

    expected_polling_response = {'priority': summary_values}
    expected_fleet_response = {
        'summary': summary_values,
        'header': {
            'title': expected_screen_response_items[0]['title'],
            'subtitle': expected_screen_response_items[0]['subtitle'],
        },
        'priority_items': [
            utils.make_fleet_item(item)
            for item in expected_screen_response_items[1:]
        ],
    }

    await utils.ensure_polling_and_screen(
        taxi_driver_priority,
        headers,
        params,
        200,
        expected_screen_response,
        expected_polling_response,
        expected_polling_response,
    )

    await utils.ensure_fleet(
        driver_trackstory_mock,
        driver_profiles_mocks,
        taxi_driver_priority,
        lat,
        lon,
        park_id,
        uuid,
        expected_fleet_response,
    )

    # each testpoint call present twice because priority calculator has
    # been called 4 times in 4 different handlers
    assert (
        _hide_zero_priority.times_called == len(expected_hidden_priorities) * 4
    )
    assert not driver_ratings_mocks.has_calls('/v2/driver/rating')
    assert not mock_fleet_vehicles.has_calls()


# pylint: disable=too-many-arguments
@pytest.mark.driver_tags_match(
    dbid='dbid_dev',
    uuid='uuid_dev',
    tags_info={
        'developer': {
            'ttl': '2019-07-17T13:56:07.000+0000',
            'topics': ['priority'],
        },
        'yandex': {
            'ttl': '2019-07-16T13:56:07.000+0000',
            'topics': ['priority'],
        },
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
            'tariff_zones': ['moscow'],
        },
    ],
)
@pytest.mark.config(
    PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST,
    ENABLE_PRIORITY_BY_EXPERIMENTS={'__default__': True},
)
@pytest.mark.pgsql(
    'driver_priority',
    queries=db_tools.join_queries(
        [
            # loyalty
            db_tools.insert_priority(1, 'loyalty', True, 'loyalty'),
            db_tools.insert_priority_relation('br_root', 1, False),
            db_tools.insert_preset(
                1, 1, 'loyalty_default', _NOW, is_default=True,
            ),
            db_tools.insert_version(
                1,
                1,
                40,
                {
                    'ranked_rule': [
                        db_tools.make_tag_rule('bronze', 1, display=4),
                        db_tools.make_tag_rule('gold', 3, display=6),
                        db_tools.make_tag_rule('platinum', 7, display=14),
                    ],
                },
                _LOYALTY_ACHIEVED,
                _NOW,
                _NOW,
                achievable_condition={'value': True},
                achievable_payload=_LOYALTY_ACHIEVABLE,
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'park_id, uuid, lon, lat, '
    'expected_screen_response_items, expected_polling_response',
    [
        (
            'dbid_dev',
            'uuid_dev',
            37.6,
            55.75,
            [
                payload_utils.ui_header_item(
                    'Наивысший приоритет', 'Так держать',
                ),
                payload_utils.ui_priority_item(
                    6,
                    'Золото',
                    'Программа лояльности: Золото',
                    is_matched=True,
                    payload=payload_utils.get_payload('Лояльность', 'есть'),
                ),
                payload_utils.ui_priority_item(
                    8,
                    'Платина',
                    'Программа лояльности: Платина',
                    is_matched=False,
                    is_disabled=True,
                    payload=_GOT_NO_LOYALTY_PAYLOAD,
                ),
            ],
            utils.polling_response(6, 0, 14),
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.tvm2_ticket(
    {200: constants.TICKET_200_300, 300: constants.TICKET_300_200},
)
async def test_priorities_visible_value(
        taxi_driver_priority,
        driver_authorizer,
        driver_trackstory_mock,
        dap,
        testpoint,
        priority_data,
        park_id: str,
        uuid: str,
        lon: float,
        lat: float,
        expected_screen_response_items,
        expected_polling_response,
):
    @testpoint('hide_zero_priority')
    def _hide_zero_priority(data):
        assert False

    driver_authorizer.set_session(park_id, 'session_0', uuid)
    driver_trackstory_mock.positions[f'{park_id}_{uuid}'] = {
        'lon': lon,
        'lat': lat,
        'timestamp': int(_NOW.timestamp()),
    }
    taxi_driver_priority = dap.create_driver_wrapper(
        taxi_driver_priority,
        park_id,
        uuid,
        user_agent=constants.DEFAULT_USER_AGENT,
    )

    params = {
        'park_id': park_id,
        'session': 'session_0',
        'lon': lon,
        'lat': lat,
    }

    headers = {
        'Accept-Language': constants.DEFAULT_ACCEPT_LANGUAGE,
        'User-Agent': constants.DEFAULT_USER_AGENT,
    }
    expected_screen_response = {
        'ui': {'primary': {'items': expected_screen_response_items}},
    }

    await utils.ensure_polling_and_screen(
        taxi_driver_priority,
        headers,
        params,
        200,
        expected_screen_response,
        expected_polling_response,
        expected_polling_response,
    )


# pylint: disable=too-many-arguments
@pytest.mark.driver_tags_match(
    dbid='dbid', uuid='uuid', tags_info={}, udid='udid',
)
@pytest.mark.driver_tags_match(
    dbid='dbid', uuid='uuid2', tags_info={}, udid='udidlowrating',
)
@pytest.mark.driver_tags_match(
    dbid='dbid', uuid='uuid3', tags_info={}, udid='udid3',
)
@pytest.mark.driver_tags_match(
    dbid='dbid', uuid='uuid5', tags_info={}, udid='udid',
)
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
            'tariff_zones': ['moscow'],
        },
    ],
)
@pytest.mark.drivers_car_ids(
    data={
        'dbid_noyear': 'carid',
        'dbid_uuid2': 'carid2',
        'dbid_uuid3': 'carid3',
        'dbid_uuid4': 'oldcar',
        'dbid_uuid5': 'newcar',
    },
)
@pytest.mark.config(
    PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST,
    ENABLE_PRIORITY_BY_EXPERIMENTS={'__default__': True},
)
@pytest.mark.driver_ratings(
    ratings=[
        {'unique_driver_id': 'udid', 'rating': 4.94},
        {'unique_driver_id': 'udidlowrating', 'rating': 4.0},
        {'unique_driver_id': 'udid3', 'rating': 4.94},
    ],
)
@pytest.mark.fleet_vehicles(
    data={
        'dbid_noyear': {},
        'dbid_carid2': {'year': 2018},
        'dbid_carid3': {'year': 2017},
        'dbid_oldcar': {'year': 2002},
        'dbid_newcar': {'year': 2022},
    },
)
@pytest.mark.priority_data(
    now=_NOW,
    data=[
        pd.PriorityData(
            'job',
            [
                pd.PrioritySettings(
                    ['moscow', 'br_root'],
                    10,
                    pd.PriorityRule(
                        _SINGLE,
                        [(_RATING_RULE, (4.9, 4.95, 'rating'), 2, None)],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                    is_achievable=True,
                    is_temporary=True,
                ),
            ],
        ),
        pd.PriorityData(
            'clean_car',
            [
                pd.PrioritySettings(
                    ['moscow', 'br_root'],
                    15,
                    pd.PriorityRule(
                        _EXCLUDED,
                        [
                            (_CAR_YEAR, (True, 2020, 'clean_car'), 4, None),
                            (_CAR_YEAR, (True, 2010, 'clean_car'), 2, None),
                            (_CAR_YEAR, (False, 2010, 'clean_car'), -5, None),
                        ],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                    is_achievable=True,
                ),
            ],
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.tvm2_ticket(
    {200: constants.TICKET_200_300, 300: constants.TICKET_300_200},
)
@pytest.mark.parametrize(
    'park_id, uuid, expected_calls, priority_values',
    [
        ('dbid', 'uuid', (True, True, False), (0, 2, 4)),
        ('dbid', 'noyear', (False, True, True), (0, 0, 4)),
        ('dbid', 'uuid2', (True, True, True), (2, 0, 4)),
        ('dbid', 'uuid3', (True, True, True), (2, 2, 4)),
        ('dbid', 'uuid4', (False, True, True), (-5, 0, 2)),
        ('dbid', 'uuid5', (True, True, True), (4, 2, 6)),
    ],
)
async def test_priorities_from_new_data_sources(
        taxi_driver_priority,
        driver_authorizer,
        driver_trackstory_mock,
        dap,
        testpoint,
        priority_data,
        driver_ratings_mocks,
        driver_profiles_mocks,
        mock_fleet_vehicles,
        park_id: str,
        uuid: str,
        expected_calls: Tuple[bool, bool, bool],
        priority_values: Tuple[int, int, int],
):
    @testpoint('hide_zero_priority')
    def _hide_zero_priority(data):
        assert False

    lon = 37.6
    lat = 55.75

    driver_authorizer.set_session(park_id, 'session_0', uuid)
    driver_trackstory_mock.positions[f'{park_id}_{uuid}'] = {
        'lon': lon,
        'lat': lat,
        'timestamp': int(_NOW.timestamp()),
    }
    taxi_driver_priority = dap.create_driver_wrapper(
        taxi_driver_priority,
        park_id,
        uuid,
        user_agent=constants.DEFAULT_USER_AGENT,
    )

    params = {
        'park_id': park_id,
        'session': 'session_0',
        'lon': lon,
        'lat': lat,
    }

    headers = {
        'Accept-Language': constants.DEFAULT_ACCEPT_LANGUAGE,
        'User-Agent': constants.DEFAULT_USER_AGENT,
    }

    response = utils.polling_response(*priority_values)
    await utils.ensure_polling_and_screen(
        taxi_driver_priority, headers, params, 200, None, response, response,
    )

    ratings_call, profiles_call, fleet_vehicles_call = expected_calls
    assert driver_ratings_mocks.has_calls('/v2/driver/rating') == ratings_call
    assert (
        driver_profiles_mocks.has_calls('cars/retrieve_by_driver_id')
        == profiles_call
    )
    assert mock_fleet_vehicles.has_calls() == fleet_vehicles_call


@pytest.mark.driver_tags_match(
    dbid='dbid_dev',
    uuid='uuid_dev',
    tags_info={
        'developer': {
            'ttl': '2019-07-17T13:56:07.000+0000',
            'topics': ['priority'],
        },
        'yandex': {
            'ttl': '2019-07-16T13:56:07.000+0000',
            'topics': ['priority'],
        },
        'gold': {'topics': ['commissions', 'priority']},
    },
)
@pytest.mark.driver_tags_match(
    dbid='max',
    uuid='ranked',
    tags_info={'platinum': {'topics': ['priority']}},
)
@pytest.mark.driver_tags_match(
    dbid='not', uuid='ranked', tags_info={'yandex': {'topics': ['priority']}},
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
@pytest.mark.config(
    DRIVER_PRIORITY_NEW_RANKED_PRIORITY_SCREEN={
        '__default__': {'enabled': False, 'major': 0, 'minor': 0},
        'android': {'enabled': True, 'major': 9, 'minor': 21},
        'ios': {'enabled': False, 'major': 1, 'minor': 1},
    },
    ENABLE_PRIORITY_BY_EXPERIMENTS={'__default__': True, 'moscow': False},
    PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST,
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
            # loyalty
            db_tools.insert_priority(2, 'loyalty', True, 'loyalty'),
            db_tools.insert_priority_relation('br_root', 2, False),
            db_tools.insert_preset(5, 2, 'loyalty_moscow', _NOW),
            db_tools.insert_preset_relation('moscow', 5),
            db_tools.insert_version(
                5,
                5,
                40,
                {
                    'ranked_rule': [
                        db_tools.make_tag_rule('bronze', 1),
                        db_tools.make_tag_rule('gold', 3),
                        db_tools.make_tag_rule('platinum', 7),
                    ],
                },
                _LOYALTY_ACHIEVED,
                _NOW,
                _NOW,
                achievable_condition={'value': True},
                achievable_payload=_LOYALTY_ACHIEVABLE,
            ),
            db_tools.insert_preset(
                6, 2, 'loyalty_default', _NOW, is_default=True,
            ),
            db_tools.insert_version(
                6,
                6,
                0,
                db_tools.EMPTY_RULE,
                _LOYALTY_ACHIEVED,
                _NOW,
                _NOW,
                disabled_condition={'value': True},
                achievable_payload=_LOYALTY_ACHIEVABLE,
            ),
            # job
            db_tools.insert_priority(7, 'job', True, 'job'),
            db_tools.insert_priority_relation('br_root', 7, False),
            db_tools.insert_preset(15, 7, 'job_moscow', _NOW),
            db_tools.insert_preset_relation('moscow', 15),
            db_tools.insert_version(
                15,
                15,
                10,
                {'single_rule': db_tools.make_tag_rule('developer', 2)},
                db_tools.EMPTY_PAYLOAD,
                _NOW,
                _NOW,
                achievable_condition={'value': True},
                temporary_condition={'value': True},
            ),
            db_tools.insert_preset(
                17, 7, 'job_default', _NOW, is_default=True,
            ),
            db_tools.insert_version(
                17,
                17,
                0,
                {'single_rule': db_tools.make_tag_rule('developer', 2)},
                db_tools.EMPTY_PAYLOAD,
                _NOW,
                _NOW,
                achievable_condition={'value': True},
                temporary_condition={'value': True},
            ),
        ],
    ),
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.tvm2_ticket(
    {200: constants.TICKET_200_300, 300: constants.TICKET_300_200},
)
@pytest.mark.parametrize(
    'park_id, uuid, user_agent, use_new_ranked_payload, expected_screen, '
    'expected_polling_response',
    [
        (
            'dbid_dev',
            'uuid_dev',
            constants.DEFAULT_USER_AGENT,
            False,
            [
                payload_utils.ui_header_item(
                    'Наивысший приоритет', 'Так держать',
                ),
                payload_utils.ui_priority_item(
                    3,
                    'Золото',
                    'Программа лояльности: Золото',
                    is_matched=True,
                    payload=payload_utils.get_payload('Лояльность', 'есть'),
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    2, 'Команда Яндекс', None, is_matched=True, new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    2,
                    'Разработчик',
                    'Истекает через 1 д. 23 ч.',
                    is_matched=True,
                    is_temporary=True,
                    new_icon=True,
                ),
                payload_utils.ui_priority_item(
                    4,  # 4 = 7 (platinum) - 3 (gold)
                    'Платина',
                    'Программа лояльности: Платина',
                    is_matched=False,
                    is_disabled=True,
                    payload=_GOT_NO_LOYALTY_PAYLOAD,
                    new_icon=True,
                ),
            ],
            utils.polling_response(5, 2, 11),
        ),
        (
            'dbid_dev',
            'uuid_dev',
            _NEW_RANKED_USER_AGENT,
            True,
            [
                payload_utils.ui_header_item(
                    'Наивысший приоритет', 'Так держать',
                ),
                payload_utils.ui_priority_item(
                    3,
                    'Золото',
                    'Программа лояльности: Золото',
                    is_matched=True,
                    payload=payload_utils.get_ranked_payload(
                        'Лояльность', 'есть', _LOYALTY_RANKED_RULE[::-1], 1,
                    ),
                    new_icon=True,
                    ranker_priority_max_value=_LOYALTY_RANKED_RULE[
                        -1
                    ].priority,
                ),
                # this ranked priority doesn't have new payload because it has
                # non-positive priorities
                payload_utils.ui_priority_item(
                    2,
                    'Команда Яндекс',
                    None,
                    is_matched=True,
                    new_icon=True,
                    ranker_priority_max_value=None,
                ),
                payload_utils.ui_priority_item(
                    2,
                    'Разработчик',
                    'Истекает через 1 д. 23 ч.',
                    is_matched=True,
                    is_temporary=True,
                    new_icon=True,
                ),
            ],
            utils.polling_response(5, 2, 11),
        ),
        (
            'dbid_dev',
            'uuid_dev',
            _NEW_RADAR_UI_USER_AGENT,
            True,
            [
                payload_utils.ui_header_item(
                    'Наивысший приоритет', 'Так держать', is_new_radar_ui=True,
                ),
                payload_utils.ui_priority_item(
                    3,
                    'Золото',
                    'Программа лояльности: Золото',
                    is_matched=True,
                    payload=payload_utils.get_ranked_payload(
                        'Лояльность', 'есть', _LOYALTY_RANKED_RULE[::-1], 1,
                    ),
                    new_icon=True,
                    ranker_priority_max_value=_LOYALTY_RANKED_RULE[
                        -1
                    ].priority,
                    use_new_divider_type=True,
                ),
                # this ranked priority doesn't have new payload because it has
                # non-positive priorities
                payload_utils.ui_priority_item(
                    2,
                    'Команда Яндекс',
                    None,
                    is_matched=True,
                    new_icon=True,
                    ranker_priority_max_value=None,
                ),
                payload_utils.ui_priority_item(
                    2,
                    'Разработчик',
                    'Истекает через 1 д. 23 ч.',
                    is_matched=True,
                    is_temporary=True,
                    new_icon=True,
                ),
            ],
            utils.polling_response(5, 2, 11),
        ),
        (
            'max',
            'ranked',
            _NEW_RANKED_USER_AGENT,
            True,
            [
                payload_utils.ui_header_item(
                    'Наивысший приоритет', 'Так держать',
                ),
                payload_utils.ui_priority_item(
                    7,
                    'Платина',
                    'Программа лояльности: Платина',
                    is_matched=True,
                    payload=payload_utils.get_ranked_payload(
                        'Лояльность', 'есть', _LOYALTY_RANKED_RULE[::-1], 0,
                    ),
                    new_icon=True,
                    ranker_priority_max_value=_LOYALTY_RANKED_RULE[
                        -1
                    ].priority,
                ),
                payload_utils.ui_priority_item(
                    2,
                    'Разработчик',
                    None,
                    is_matched=False,
                    is_disabled=True,
                    new_icon=True,
                ),
            ],
            utils.polling_response(7, 0, 9),
        ),
        (
            'not',
            'ranked',
            _NEW_RANKED_USER_AGENT,
            True,
            [
                payload_utils.ui_header_item(
                    'Высокий приоритет', 'Все заказы для вас одного',
                ),
                payload_utils.ui_priority_item(
                    2,
                    'Команда Яндекс',
                    None,
                    is_matched=True,
                    new_icon=True,
                    ranker_priority_max_value=None,
                ),
                payload_utils.ui_priority_item(
                    1,
                    'Бронза',
                    'Программа лояльности: Бронза',
                    is_matched=False,
                    payload=payload_utils.get_ranked_payload(
                        'Вы еще не участвуете в программе лояльности',
                        'Но вы можете это исправить',
                        _LOYALTY_RANKED_RULE[::-1],
                        3,
                        has_button=False,
                    ),
                    new_icon=True,
                    ranker_priority_max_value=_LOYALTY_RANKED_RULE[
                        -1
                    ].priority,
                    is_disabled=True,
                ),
                payload_utils.ui_priority_item(
                    2,
                    'Разработчик',
                    None,
                    is_matched=False,
                    new_icon=True,
                    is_disabled=True,
                ),
            ],
            utils.polling_response(2, 0, 5),
        ),
    ],
)
async def test_updated_ranked_payload(
        taxi_driver_priority,
        driver_authorizer,
        driver_trackstory_mock,
        dap,
        testpoint,
        park_id: str,
        uuid: str,
        user_agent,
        use_new_ranked_payload,
        expected_screen: List[Any],
        expected_polling_response: Dict[str, Any],
):
    id_index = 0

    @testpoint('id_generate')
    def _id_generate(arg):
        nonlocal id_index
        id_index += 1
        return {'id': 'generated_id_' + str(id_index)}

    @testpoint('hide_zero_priority')
    def _hide_zero_priority(data):
        assert False

    driver_authorizer.set_session(park_id, 'session_0', uuid)
    driver_trackstory_mock.positions[f'{park_id}_{uuid}'] = {
        'lon': 37.6,
        'lat': 55.75,
        'timestamp': int(_NOW.timestamp()),
    }
    taxi_driver_priority = dap.create_driver_wrapper(
        taxi_driver_priority, park_id, uuid, user_agent=user_agent,
    )

    params = {
        'park_id': park_id,
        'session': 'session_0',
        'lon': 37.6,
        'lat': 55.75,
    }

    headers = {
        'Accept-Language': constants.DEFAULT_ACCEPT_LANGUAGE,
        'User-Agent': user_agent,
    }
    expected_screen_response = {'ui': {'primary': {'items': expected_screen}}}

    await utils.ensure_polling_and_screen(
        taxi_driver_priority,
        headers,
        params,
        200,
        expected_screen_response,
        expected_polling_response,
        expected_polling_response,
    )
