import datetime
import json
import operator
from typing import Optional

import pytest

from tests_driver_priority import constants
from tests_driver_priority import db_tools
from tests_driver_priority.plugins import mock_priority_data as pd

_HOME_ZONE = 'moscow'

_NOW = datetime.datetime(2019, 7, 15, 13, 57, 8, tzinfo=datetime.timezone.utc)
_SINGLE = pd.PriorityRuleType.Single
_RANKED = pd.PriorityRuleType.Ranked
_EXCLUDED = pd.PriorityRuleType.Excluded
_TAG_RULE = pd.RuleType.TagRule


class Tag:
    def __init__(self, name, ttl=None, topics=None):
        self.name = name
        self.ttl = ttl
        self.topics = topics


class Priority:
    def __init__(
            self,
            name,
            value,
            title,
            subtitle=None,
            is_achievable=None,
            is_temporary=None,
            is_hidden=False,
            preset_name: Optional[str] = None,
            version_id: Optional[int] = None,
    ):
        self.name = name
        self.value = value
        self.title = title
        self.subtitle = subtitle
        self.is_achievable = is_achievable
        self.is_temporary = is_temporary
        self.is_hidden = is_hidden
        self.preset_name = preset_name
        self.version_id = version_id


def _response(
        stable_priority,
        temporary_priority,
        possible_priority,
        tags,
        rating,
        unique_driver_id,
        nearest_zone,
        agglomerations,
        priorities,
        contractor_profession='taxi',
):
    priority_items = {
        'stable': stable_priority,
        'temporary': temporary_priority,
        'possible': possible_priority,
    }

    tags_items = list()
    for tag in tags:
        item = {'name': tag.name}
        if tag.ttl:
            item['ttl'] = tag.ttl
        if tag.topics is not None:
            item['topics'] = tag.topics
        tags_items.append(item)

    screen_items = list()
    for priority in priorities:
        item = {
            'id': priority.name,
            'title': priority.title,
            'value': priority.value,
            'is_hidden': priority.is_hidden,
        }

        if priority.subtitle:
            item['subtitle'] = priority.subtitle
        if priority.preset_name:
            item['preset_name'] = priority.preset_name
        if priority.version_id is not None:
            item['version_id'] = priority.version_id

        item['status'] = (
            'achievable'
            if priority.is_achievable
            else 'temporary'
            if priority.is_temporary
            else 'stable'
        )

        screen_items.append(item)

    return {
        'priority': priority_items,
        'tags': tags_items,
        'rating': rating,
        'unique_driver_id': unique_driver_id,
        'nearest_zone': nearest_zone,
        'agglomerations': agglomerations,
        'screen': {'items': screen_items},
        'contractor_profession': contractor_profession,
    }


@pytest.mark.uservice_oneshot
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
    ],
)
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
    },
    udid='udid_dev',
)
@pytest.mark.driver_tags_match(
    dbid='dbid_excluded_by_experiment',
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
    },
    udid='udid_uuid_dev',
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
    udid='udid_mail',
)
@pytest.mark.driver_tags_match(
    dbid='dbid',
    uuid='uuid_eats',
    tags_info={
        'gold': {'topics': ['priority']},
        'eats_courier': {'topics': ['priority']},
        'developer': {'topics': ['priority']},
    },
    udid='udid_eats',
)
@pytest.mark.config(
    PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST,
    DRIVER_PRIORITY_PROFESSIONS_BY_PRIORITY_NAMES={
        '__default__': ['taxi'],
        'eats_priority': ['eats_courier'],
    },
)
@pytest.mark.priority_data(
    now=_NOW,
    data=[
        pd.PriorityData(
            'job',
            [
                pd.PrioritySettings(
                    ['moscow'],
                    10,
                    pd.PriorityRule(
                        _SINGLE, [(_TAG_RULE, 'developer', 2, None)],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                    is_achievable=True,
                    is_temporary=True,
                ),
            ],
        ),
        pd.PriorityData(
            'eats_priority',
            [
                pd.PrioritySettings(
                    ['moscow'],
                    11,
                    pd.PriorityRule(_SINGLE, [(_TAG_RULE, 'gold', 2, None)]),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                    is_achievable=True,
                ),
            ],
            tanker_keys_prefix='loyalty',
        ),
        pd.PriorityData(
            'company',
            [
                pd.PrioritySettings(
                    ['moscow'],
                    20,
                    pd.PriorityRule(
                        _RANKED,
                        [
                            (_TAG_RULE, 'mail_ru', 0, None),
                            (_TAG_RULE, 'yandex', 2, None),
                        ],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                ),
            ],
        ),
        pd.PriorityData(
            'employment',
            [
                pd.PrioritySettings(
                    ['moscow'],
                    30,
                    pd.PriorityRule(
                        _EXCLUDED,
                        [
                            (_TAG_RULE, 'individual_enterpreneur', 2, None),
                            (_TAG_RULE, 'selfemployed', 1, None),
                        ],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                    is_temporary=True,
                    is_achievable=True,
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'park_id, uuid, lon, lat, enable_moscow, expected_response',
    [
        (
            'dbid_dev',
            'uuid_dev',
            36.99,
            55.75,
            False,
            _response(
                stable_priority=2,
                temporary_priority=2,
                possible_priority=5,
                tags=[
                    Tag(
                        'developer',
                        ttl='2019-07-17T13:56:07+0000',
                        topics=['priority'],
                    ),
                    Tag(
                        'yandex',
                        ttl='2019-07-16T13:56:07+0000',
                        topics=['priority'],
                    ),
                ],
                rating=5.0,
                unique_driver_id='udid_dev',
                nearest_zone=_HOME_ZONE,
                agglomerations=[],
                priorities=[
                    Priority(
                        'company',
                        2,
                        'Команда Яндекс',
                        preset_name='preset5',
                        version_id=5,
                    ),
                    Priority(
                        'job',
                        2,
                        'Разработчик',
                        'Истекает через 1 д. 23 ч.',
                        is_temporary=True,
                        preset_name='preset1',
                        version_id=1,
                    ),
                    Priority(
                        'employment',
                        1,
                        'Смена формы занятости',
                        is_achievable=True,
                        preset_name='preset7',
                        version_id=7,
                    ),
                ],
            ),
        ),
        (
            'dbid',
            'uuid_eats',
            36.99,
            55.75,
            False,
            _response(
                stable_priority=2,
                temporary_priority=0,
                possible_priority=2,
                tags=[
                    Tag('developer', topics=['priority']),
                    Tag('eats_courier', topics=['priority']),
                    Tag('gold', topics=['priority']),
                ],
                rating=5.0,
                unique_driver_id='udid_eats',
                nearest_zone=_HOME_ZONE,
                agglomerations=[],
                priorities=[
                    Priority(
                        'eats_priority',
                        2,
                        'Золото',
                        subtitle='Программа лояльности: Золото',
                        preset_name='preset3',
                        version_id=3,
                    ),
                ],
                contractor_profession='eats_courier',
            ),
        ),
        (
            'dbid_mail',
            'uuid_mail',
            37.6,
            55.75,
            False,
            _response(
                stable_priority=0,
                temporary_priority=3,
                possible_priority=3,
                tags=[
                    Tag(
                        'developer',
                        ttl='2019-07-15T13:57:09+0000',
                        topics=['priority'],
                    ),
                    Tag('mail_ru', topics=['priority']),
                    Tag(
                        'selfemployed',
                        ttl='2019-07-15T13:57:07+0000',
                        topics=['priority'],
                    ),
                ],
                rating=5.0,
                unique_driver_id='udid_mail',
                nearest_zone=_HOME_ZONE,
                agglomerations=[],
                priorities=[
                    Priority(
                        'employment',
                        1,
                        'Самозанятый',
                        'Истекает через 1 мин.',
                        is_temporary=True,
                        preset_name='preset7',
                        version_id=7,
                    ),
                    Priority(
                        'company',
                        0,
                        'Команда Мейл.ру',
                        None,
                        is_hidden=True,
                        preset_name='preset5',
                        version_id=5,
                    ),
                    Priority(
                        'job',
                        2,
                        'Разработчик',
                        'Истекает через 1 мин.',
                        is_temporary=True,
                        preset_name='preset1',
                        version_id=1,
                    ),
                ],
            ),
        ),
        (
            'dbid_mail',
            'uuid_mail',
            37.6,
            54.2,
            True,  # Tula region
            _response(
                stable_priority=0,
                temporary_priority=0,
                possible_priority=0,
                tags=[
                    Tag(
                        'developer',
                        ttl='2019-07-15T13:57:09+0000',
                        topics=['priority'],
                    ),
                    Tag('mail_ru', topics=['priority']),
                    Tag(
                        'selfemployed',
                        ttl='2019-07-15T13:57:07+0000',
                        topics=['priority'],
                    ),
                ],
                rating=5.0,
                unique_driver_id='udid_mail',
                nearest_zone='tula',
                agglomerations=[],
                priorities=[],
            ),
        ),
        (
            'dbid_excluded_by_experiment',
            'uuid_dev',
            37.6,
            55.75,
            True,
            _response(
                stable_priority=0,
                temporary_priority=0,
                possible_priority=0,
                tags=[
                    Tag(
                        'developer',
                        ttl='2019-07-17T13:56:07+0000',
                        topics=['priority'],
                    ),
                    Tag(
                        'yandex',
                        ttl='2019-07-16T13:56:07+0000',
                        topics=['priority'],
                    ),
                ],
                rating=5.0,
                unique_driver_id='udid_uuid_dev',
                nearest_zone=_HOME_ZONE,
                agglomerations=[],
                priorities=[],
            ),
        ),
        (
            'dbid_mail',
            'uuid_mail',
            37.6,
            55.75,
            True,  # Experiment exclude
            _response(
                stable_priority=0,
                temporary_priority=0,
                possible_priority=0,
                tags=[
                    Tag(
                        'developer',
                        ttl='2019-07-15T13:57:09+0000',
                        topics=['priority'],
                    ),
                    Tag('mail_ru', topics=['priority']),
                    Tag(
                        'selfemployed',
                        ttl='2019-07-15T13:57:07+0000',
                        topics=['priority'],
                    ),
                ],
                rating=5.0,
                unique_driver_id='udid_mail',
                nearest_zone=_HOME_ZONE,
                agglomerations=[],
                priorities=[],
            ),
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.tvm2_ticket(
    {200: constants.TICKET_200_300, 300: constants.TICKET_300_200},
)
async def test_priorities(
        taxi_driver_priority,
        taxi_config,
        driver_profiles_mocks,
        testpoint,
        park_id,
        uuid,
        lon,
        lat,
        enable_moscow,
        expected_response,
):
    @testpoint('hide_zero_priority')
    def _hide_zero_priority(data):
        assert (
            False
        ), 'zero priorities should not be hidden in diagnostic handler'

    driver_profiles_mocks.set_taximeter_info(
        profile=f'{park_id}_{uuid}',
        platform='android',
        version='9.50',
        version_type='',
    )

    taxi_config.set(
        ENABLE_PRIORITY_BY_EXPERIMENTS={
            '__default__': False,
            'moscow': enable_moscow,
        },
    )

    response = await taxi_driver_priority.get(
        constants.DIAGNOSTICS_URL,
        params={'park_id': park_id, 'uuid': uuid, 'lon': lon, 'lat': lat},
        headers=constants.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    response_json = response.json()
    response_json['tags'].sort(key=operator.itemgetter('name'))
    assert response_json == expected_response
    assert not _hide_zero_priority.has_calls
    assert driver_profiles_mocks.has_calls('profiles/retrieve')


@pytest.mark.uservice_oneshot
@pytest.mark.now(_NOW.isoformat())
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
@pytest.mark.driver_tags_match(
    dbid='dbid_dev',
    uuid='uuid_dev',
    tags_info={
        'bronze': {
            'ttl': '2019-07-17T13:56:07.000+0000',
            'topics': ['rating'],
        },
        'gold': {'ttl': '2019-07-16T13:56:07.000+0000', 'topics': ['rating']},
    },
    udid='udid_dev',
)
@pytest.mark.driver_taximeter(
    profile='dbid_dev_uuid_dev',
    platform='android',
    version='9.50',
    version_type='',
)
@pytest.mark.config(
    PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST,
    ENABLE_PRIORITY_BY_EXPERIMENTS={'__default__': True},
    DRIVER_PRIORITY_APPLIED_TAGS_TOPICS={'topics': ['rating']},
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
                db_tools.DEFAULT_ACHIEVED_PAYLOAD,
                _NOW,
                _NOW,
                achievable_condition={'value': True},
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'park_id, uuid, lon, lat, expected_response',
    [
        (
            'dbid_dev',
            'uuid_dev',
            36.99,
            55.75,
            _response(
                stable_priority=6,
                temporary_priority=0,
                possible_priority=14,
                tags=[
                    Tag(
                        'bronze',
                        ttl='2019-07-17T13:56:07+0000',
                        topics=['rating'],
                    ),
                    Tag(
                        'gold',
                        ttl='2019-07-16T13:56:07+0000',
                        topics=['rating'],
                    ),
                ],
                rating=5.0,
                unique_driver_id='udid_dev',
                nearest_zone=_HOME_ZONE,
                agglomerations=['br_root'],
                priorities=[
                    Priority(
                        'loyalty',
                        6,
                        'Золото',
                        'Программа лояльности: Золото',
                        preset_name='loyalty_default',
                        version_id=1,
                    ),
                    Priority(
                        'loyalty',
                        8,
                        'Платина',
                        'Программа лояльности: Платина',
                        is_achievable=True,
                        preset_name='loyalty_default',
                        version_id=1,
                    ),
                ],
            ),
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.tvm2_ticket(
    {200: constants.TICKET_200_300, 300: constants.TICKET_300_200},
)
async def test_visible_priorities(
        taxi_driver_priority,
        driver_profiles_mocks,
        testpoint,
        park_id,
        uuid,
        lon,
        lat,
        expected_response,
):
    @testpoint('hide_zero_priority')
    def _hide_zero_priority(data):
        assert False

    response = await taxi_driver_priority.get(
        constants.DIAGNOSTICS_URL,
        params={'park_id': park_id, 'uuid': uuid, 'lon': lon, 'lat': lat},
        headers=constants.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    response_json = response.json()
    response_json['tags'].sort(key=operator.itemgetter('name'))
    assert response_json == expected_response
    assert driver_profiles_mocks.has_calls('profiles/retrieve')


@pytest.mark.uservice_oneshot
@pytest.mark.now(_NOW.isoformat())
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
            'tariff_zones': ['moscow'],
        },
    ],
)
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
            'topics': ['company', 'priority'],
        },
        'enable_exp': {'topics': ['priority', 'priority']},
    },
    udid='udid_dev',
)
@pytest.mark.driver_taximeter(
    profile='dbid_dev_uuid_dev',
    platform='android',
    version='9.50',
    version_type='',
)
@pytest.mark.config(
    PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST,
    ENABLE_PRIORITY_BY_EXPERIMENTS={'__default__': True},
    PRIORITY_ACTIVITY_FETCH_ENABLED=True,
)
@pytest.mark.parametrize('dms_not_found_error', [False, True])
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.tvm2_ticket(
    {200: constants.TICKET_200_300, 300: constants.TICKET_300_200},
)
async def test_activity_priorities(
        taxi_driver_priority,
        mockserver,
        driver_profiles_mocks,
        testpoint,
        dms_not_found_error,
):
    @testpoint('hide_zero_priority')
    def _hide_zero_priority(data):
        assert False

    @mockserver.json_handler(
        '/driver-metrics-storage/v1/completion_scores/progress',
    )
    def _dms_handler(request):
        assert request.json['unique_driver_id'] == 'udid_dev'
        assert request.json['tariff_zone'] == 'moscow'
        request_tags = request.json['tags']
        request_tags.sort()
        assert request_tags == ['developer', 'enable_exp', 'yandex']

        if dms_not_found_error:
            dms_response = {'code': '404', 'message': 'not found'}
            return mockserver.make_response(json.dumps(dms_response), 404)

        dms_response = {
            'completion_score': 0,
            'levels': [
                {'priority': 1, 'scores_to_reach': 1},
                {'priority': 2, 'scores_to_reach': 2, 'is_current': True},
                {'priority': 3, 'scores_to_reach': 3, 'is_current': False},
                {'priority': 4, 'scores_to_reach': 4},
            ],
        }
        return mockserver.make_response(json.dumps(dms_response), 200)

    park_id = 'dbid_dev'
    uuid = 'uuid_dev'
    lon = 36.99
    lat = 55.75

    response = await taxi_driver_priority.get(
        constants.DIAGNOSTICS_URL,
        params={'park_id': park_id, 'uuid': uuid, 'lon': lon, 'lat': lat},
        headers=constants.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert _dms_handler.has_calls
    assert driver_profiles_mocks.has_calls('profiles/retrieve')
