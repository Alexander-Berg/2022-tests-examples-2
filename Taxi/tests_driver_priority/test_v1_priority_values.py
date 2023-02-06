# pylint: disable=import-error
import datetime
import operator

from fbs.driver_priority.handlers.v1_priority_values import Response
import pytest
import pytz

from tests_driver_priority import constants
from tests_driver_priority import db_tools
from tests_driver_priority.plugins import mock_priority_data as pd


_CONTENT_TYPE = 'application/x-flatbuffers'

_REQUEST_BODY = {
    'chunks': [
        {
            'tariff_zone': 'moscow',
            'drivers': [
                {'dbid': 'dbid0', 'uuid': 'uuid0'},
                {'dbid': 'dbid', 'uuid': 'uuideats'},
                {'dbid': 'dbid0', 'uuid': 'activity_excluded'},
                {'dbid': 'invld', 'uuid': 'invld'},  # no udid
                {'dbid': 'dbid1', 'uuid': 'uuid1'},
                {'dbid': 'dbid2', 'uuid': 'uuid2'},  # no tags - zero value
            ],
        },
        {
            'tariff_zone': 'tula',
            'drivers': [
                {'dbid': 'dbid3', 'uuid': 'uuid3'},
                {'dbid': 'abc', 'uuid': 'abc'},
                {'dbid': 'xyz', 'uuid': 'xyz'},
                {'dbid': 'xyz', 'uuid': 'abc'},
            ],
        },
    ],
}

_NOW = datetime.datetime.now(tz=pytz.timezone('UTC'))

_SINGLE = pd.PriorityRuleType.Single
_RANKED = pd.PriorityRuleType.Ranked
_EXCLUDED = pd.PriorityRuleType.Excluded
_ACTIVITY = pd.PriorityRuleType.Activity

_TAG_RULE = pd.RuleType.TagRule
_RATING_RULE = pd.RuleType.RatingRule
_CAR_YEAR_RULE = pd.RuleType.CarYearRule
_ACTIVITY_RULE = pd.RuleType.ActivityRule


def _parse_values(priority_fbs):
    values = []
    for index in range(priority_fbs.ValuesLength()):
        value = priority_fbs.Values(index)
        values.append(
            {
                'priority_name': value.PriorityName().decode('utf-8'),
                'value': value.Value(),
            },
        )
    return values


def _parse_priorities(chunk_fbs):
    priorities = []
    for index in range(chunk_fbs.PrioritiesLength()):
        priority = chunk_fbs.Priorities(index)
        priorities.append(
            {
                'profile': priority.Profile().decode('utf-8'),
                'value': _parse_values(priority),
            },
        )
    return priorities


def _parse_response(response_fbs):
    response = Response.Response.GetRootAsResponse(response_fbs, 0)
    chunks = []
    for index in range(response.ChunksLength()):
        chunk = response.Chunks(index)
        chunks.append({'priorities': _parse_priorities(chunk)})

    return {'chunks': chunks}


def _decode_response(response):
    assert response.status_code == 200
    assert response.headers['Content-Type'] == _CONTENT_TYPE
    return _parse_response(response.content)


@pytest.mark.now(_NOW.isoformat())
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
                        _SINGLE, [(_TAG_RULE, 'developer', 10, None)],
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
                            (
                                _CAR_YEAR_RULE,
                                (False, 2018, 'car_year'),
                                -3,
                                None,
                            ),
                            (
                                _CAR_YEAR_RULE,
                                (True, 2020, 'car_year'),
                                4,
                                None,
                            ),
                        ],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                    is_achievable=True,
                ),
            ],
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
                            (_TAG_RULE, 'yandex', 20, None),
                        ],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                ),
            ],
        ),
        pd.PriorityData(
            'recently_selfemployed',
            [
                pd.PrioritySettings(
                    ['moscow'],
                    60,
                    pd.PriorityRule(
                        _RANKED,
                        [
                            (_TAG_RULE, 'selfemployed_6m_or_less', 60, None),
                            (_RATING_RULE, (1, 4.999, 'rating'), 60, None),
                        ],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                    is_achievable={
                        'none_of': ['selfemployed', 'individual_entrepreneur'],
                    },
                ),
            ],
        ),
        pd.PriorityData(
            'activity',
            [
                pd.PrioritySettings(
                    ['__default__'],
                    70,
                    pd.PriorityRule(
                        _ACTIVITY, [(_ACTIVITY_RULE, 'activity', None, None)],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                ),
            ],
        ),
    ],
)
@pytest.mark.config(PRIORITY_ACTIVITY_FETCH_ENABLED=True)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.driver_tags_match(
    dbid='dbid0',
    uuid='uuid0',
    tags_info={'developer': {'topics': ['priority']}},
    udid='udid_first',
)
@pytest.mark.driver_tags_match(
    dbid='dbid0',
    uuid='activity_excluded',
    tags_info={'developer': {'topics': ['priority']}},
    udid='udid_excluded',
)
@pytest.mark.driver_tags_match(
    dbid='dbid1',
    uuid='uuid1',
    tags_info={
        'selfemployed': {'topics': ['priority']},
        'yandex': {'topics': ['priority', 'company']},
    },
    udid='udid_first',
)
@pytest.mark.driver_tags_match(dbid='dbid2', uuid='uuid2', udid='udid_first')
@pytest.mark.driver_tags_match(
    dbid='dbid3',
    uuid='uuid3',
    tags_info={
        'selfemployed': {'topics': ['priority']},
        'developer': {'topics': ['priority']},
        'yandex': {'topics': ['priority', 'company']},
    },
    udid='udid_second',
)
@pytest.mark.driver_tags_match(dbid='abc', uuid='abc', udid='udid_second')
@pytest.mark.driver_tags_match(dbid='xyz', uuid='xyz', udid='udid_second')
@pytest.mark.driver_tags_match(dbid='xyz', uuid='abc', udid='udid_second')
@pytest.mark.drivers_car_ids(
    data={f'dbid{i}_uuid{i}': f'carid{i}' for i in range(1, 4)},
)
@pytest.mark.fleet_vehicles(
    data={
        'dbid0_carid0': {'year': 2019},  # no match because of rule
        'dbid1_carid1': {'year': 2020},  # +4
        'dbid2_carid2': {'year': 2022},  # +4
        'dbid3_carid3': {'year': 2018},  # -3
    },
)
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
            'tariff_zones': ['moscow', 'tula'],
        },
    ],
)
@pytest.mark.parametrize('topics', (['priority'], None, ['company']))
async def test_priority_values(
        taxi_driver_priority,
        driver_ratings_mocks,
        mockserver,
        priority_data,
        taxi_config,
        topics,
):
    taxi_config.set_values(
        {
            'DRIVER_PRIORITY_APPLIED_TAGS_TOPICS': (
                {'topics': topics} if topics is not None else {}
            ),
        },
    )

    @mockserver.json_handler('/driver-metrics-storage/v1/priority/fetch-bulk')
    def _dms_handler(request):
        priority_values = []
        for chunk in request.json['chunks']:
            for driver in chunk['drivers']:
                unique_driver_id = driver['unique_driver_id']
                assert unique_driver_id != 'udid_excluded'
                tags = driver['tags']
                value = None
                if unique_driver_id == 'udid_first':
                    value = 5 if 'developer' in tags else 2
                priority_values.append(
                    {'unique_driver_id': unique_driver_id, 'value': value},
                )
        return {'priority_values': priority_values}

    response = await taxi_driver_priority.post(
        constants.VALUES_URL, _REQUEST_BODY,
    )
    response_chunks = _decode_response(response)['chunks']
    for priority in response_chunks[0]['priorities']:
        priority['value'].sort(key=operator.itemgetter('priority_name'))

    expected_chunks = [
        {
            'priorities': [
                {'profile': 'dbid0_uuid0', 'value': []},
                {'profile': 'dbid_uuideats', 'value': []},
                {'profile': 'dbid0_activity_excluded', 'value': []},
                {'profile': 'invld_invld', 'value': []},
                {
                    'profile': 'dbid1_uuid1',
                    'value': [
                        {'priority_name': 'activity', 'value': 2},
                        {'priority_name': 'clean_car', 'value': 4},
                        {'priority_name': 'company', 'value': 20},
                    ],
                },
                {
                    'profile': 'dbid2_uuid2',
                    'value': [
                        {'priority_name': 'activity', 'value': 2},
                        {'priority_name': 'clean_car', 'value': 4},
                    ],
                },
            ],
        },
        {
            'priorities': [
                {
                    'profile': 'dbid3_uuid3',
                    'value': [{'priority_name': 'clean_car', 'value': -3}],
                },
                {'profile': 'abc_abc', 'value': []},
                {'profile': 'xyz_xyz', 'value': []},
                {'profile': 'xyz_abc', 'value': []},
            ],
        },
    ]

    # temporary:
    # will be excluded after avoid config DRIVER_PRIORITY_APPLIED_TAGS_TOPICS,
    # add 'job' priority match into expected_chunks
    if topics is None or topics == ['priority']:
        activity_priority = {'priority_name': 'activity', 'value': 5}
        job_priority = {'priority_name': 'job', 'value': 10}
        expected_chunks[0]['priorities'][0]['value'].append(activity_priority)
        expected_chunks[0]['priorities'][0]['value'].append(job_priority)
        expected_chunks[0]['priorities'][2]['value'].append(job_priority)
    else:
        activity_priority = {'priority_name': 'activity', 'value': 2}
        expected_chunks[0]['priorities'][0]['value'].append(activity_priority)

    assert driver_ratings_mocks.has_calls('/v2/driver/rating/batch-retrieve')
    assert _dms_handler.has_calls
    assert response_chunks == expected_chunks


@pytest.mark.now(_NOW.isoformat())
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
            # job for eats_courier only
            db_tools.insert_priority(2, 'eats_priority', True, 'job'),
            db_tools.insert_priority_relation('br_root', 2, False),
            db_tools.insert_preset(
                2, 2, 'eats_default', _NOW, is_default=True,
            ),
            db_tools.insert_version(
                2,
                2,
                45,
                {
                    'single_rule': {
                        'tag_name': 'developer',
                        'priority_value': {'backend': 5, 'display': 1},
                    },
                },
                db_tools.DEFAULT_ACHIEVED_PAYLOAD,
                _NOW,
                _NOW,
                achievable_condition={'value': True},
            ),
        ],
    ),
)
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
            'tariff_zones': ['moscow', 'tula'],
        },
    ],
)
@pytest.mark.config(
    DRIVER_PRIORITY_PROFESSIONS_BY_PRIORITY_NAMES={
        '__default__': ['taxi'],
        'eats_priority': ['eats_courier'],
    },
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.driver_tags_match(
    dbid='dbid0', uuid='uuid0', tags_info={'gold': {'topics': ['priority']}},
)
@pytest.mark.driver_tags_match(
    dbid='dbid1',
    uuid='uuid1',
    tags_info={
        'bronze': {'topics': ['priority']},
        'yandex': {'topics': ['priority']},
    },
)
@pytest.mark.driver_tags_match(
    dbid='dbid',
    uuid='uuideats',
    tags_info={
        'developer': {'topics': ['priority']},
        'eats_courier': {'topics': ['priority']},
    },
)
@pytest.mark.driver_tags_match(
    dbid='dbid3',
    uuid='uuid3',
    tags_info={
        'developer': {'topics': ['priority']},
        'selfemployed': {'topics': ['priority']},
        'gold': {'topics': ['priority']},
    },
)
async def test_priority_backend_values(taxi_driver_priority, priority_data):
    response = await taxi_driver_priority.post(
        constants.VALUES_URL, _REQUEST_BODY,
    )
    response_chunks = _decode_response(response)
    assert response_chunks == {
        'chunks': [
            {
                'priorities': [
                    {
                        'profile': 'dbid0_uuid0',
                        'value': [{'priority_name': 'loyalty', 'value': 3}],
                    },
                    {
                        'profile': 'dbid_uuideats',
                        'value': [
                            {'priority_name': 'eats_priority', 'value': 5},
                        ],
                    },
                    {'profile': 'dbid0_activity_excluded', 'value': []},
                    {'profile': 'invld_invld', 'value': []},
                    {
                        'profile': 'dbid1_uuid1',
                        'value': [{'priority_name': 'loyalty', 'value': 1}],
                    },
                    {'profile': 'dbid2_uuid2', 'value': []},
                ],
            },
            {
                'priorities': [
                    {
                        'profile': 'dbid3_uuid3',
                        'value': [{'priority_name': 'loyalty', 'value': 3}],
                    },
                    {'profile': 'abc_abc', 'value': []},
                    {'profile': 'xyz_xyz', 'value': []},
                    {'profile': 'xyz_abc', 'value': []},
                ],
            },
        ],
    }


@pytest.mark.config(ENABLE_PRIORITY_VALUES=False)
async def test_priority_values_disabled(taxi_driver_priority):
    response = await taxi_driver_priority.post(
        constants.VALUES_URL, _REQUEST_BODY,
    )
    assert _decode_response(response) == {'chunks': []}
