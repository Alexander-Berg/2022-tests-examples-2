import datetime

import pytest
import pytz

from tests_driver_priority import constants
from tests_driver_priority import utils
from tests_driver_priority.plugins import mock_priority_data as pd


_NOW = datetime.datetime.now(tz=pytz.timezone('UTC'))
_SINGLE = pd.PriorityRuleType.Single
_TAG_RULE = pd.RuleType.TagRule


async def _ensure_response(taxi_driver_priority, expected_values):
    params = {
        'park_id': 'dbid',
        'session': 'session_0',
        'lon': constants.MSK_COORDS[0],
        'lat': constants.MSK_COORDS[1],
    }

    response = await taxi_driver_priority.get(
        constants.POLLING_URL,
        params=params,
        headers=constants.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == expected_values


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.driver_tags_match(
    dbid='dbid',
    uuid='uuid0',
    tags_info={
        'developer': {
            'ttl': '2019-07-17T13:56:07.000+0000',
            'topics': ['priority'],
        },
    },
)
@pytest.mark.driver_tags_match(
    dbid='dbid',
    uuid='uuid1',
    tags_info={
        'developer': {
            'ttl': '2019-07-17T13:56:07.000+0000',
            'topics': ['priority'],
        },
        'unemployed': {
            'ttl': '2019-07-16T13:56:07.000+0000',
            'topics': ['priority'],
        },
    },
)
@pytest.mark.config(PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST)
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
                        _SINGLE,
                        [
                            (
                                _TAG_RULE,
                                'cool_developer',
                                2,
                                {
                                    'and': [
                                        {'all_of': ['developer']},
                                        {'none_of': ['unemployed']},
                                    ],
                                },
                            ),
                        ],
                    ),
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
    'dbid_uuid, should_have_priority',
    [('dbid_uuid0', True), ('dbid_uuid1', False)],
)
async def test_priority_logical_rule(
        taxi_driver_priority,
        driver_authorizer,
        dbid_uuid,
        should_have_priority,
):
    [park_id, uuid] = dbid_uuid.split('_')

    driver_authorizer.set_session(park_id, 'session_0', uuid)

    value = 2 if should_have_priority else 0
    await _ensure_response(
        taxi_driver_priority, utils.polling_response(value, 0, value),
    )


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.driver_tags_match(
    dbid='dbid',
    uuid='uuid0',
    tags_info={
        'bad_mood': {
            'ttl': '2019-07-17T13:56:07.000+0000',
            'topics': ['priority'],
        },
        '25_yo': {
            'ttl': '2019-07-17T13:56:07.000+0000',
            'topics': ['priority'],
        },
    },
)
@pytest.mark.driver_tags_match(
    dbid='dbid',
    uuid='uuid1',
    tags_info={
        'bad_mood': {
            'ttl': '2019-07-17T13:56:07.000+0000',
            'topics': ['priority'],
        },
        'teenager': {
            'ttl': '2019-07-16T13:56:07.000+0000',
            'topics': ['priority'],
        },
    },
)
@pytest.mark.config(PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST)
@pytest.mark.priority_data(
    now=_NOW,
    data=[
        pd.PriorityData(
            'alcohol',
            [
                pd.PrioritySettings(
                    ['__default__'],
                    10,
                    pd.PriorityRule(
                        _SINGLE, [(_TAG_RULE, 'alcohol', 2, None)],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                    is_achievable={
                        'and': [
                            {'all_of': ['bad_mood']},
                            {'none_of': ['teenager']},
                        ],
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.tvm2_ticket(
    {200: constants.TICKET_200_300, 300: constants.TICKET_300_200},
)
@pytest.mark.parametrize(
    'dbid_uuid, is_priority_achievable',
    [('dbid_uuid0', True), ('dbid_uuid1', False)],
)
async def test_achievable_logical_rule(
        taxi_driver_priority,
        driver_authorizer,
        dbid_uuid,
        is_priority_achievable,
):
    [park_id, uuid] = dbid_uuid.split('_')

    driver_authorizer.set_session(park_id, 'session_0', uuid)

    value = 2 if is_priority_achievable else 0
    await _ensure_response(
        taxi_driver_priority, utils.polling_response(0, 0, value),
    )


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.driver_tags_match(
    dbid='dbid',
    uuid='uuid0',
    tags_info={
        'alcohol': {
            'ttl': '2019-07-17T13:56:07.000+0000',
            'topics': ['priority'],
        },
    },
)
@pytest.mark.config(PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST)
@pytest.mark.priority_data(
    now=_NOW,
    data=[
        pd.PriorityData(
            'drunk',
            [
                pd.PrioritySettings(
                    ['__default__'],
                    10,
                    pd.PriorityRule(
                        _SINGLE,
                        [(_TAG_RULE, 'alcohol', 2, {'all_of': ['alcohol']})],
                    ),
                    pd.PriorityPayload(pd.EMPTY_PAYLOAD),
                ),
            ],
        ),
    ],
)
@pytest.mark.tvm2_ticket(
    {200: constants.TICKET_200_300, 300: constants.TICKET_300_200},
)
async def test_simple_logical_rule(taxi_driver_priority, driver_authorizer):
    park_id = 'dbid'
    uuid = 'uuid0'

    driver_authorizer.set_session(park_id, 'session_0', uuid)

    await _ensure_response(
        taxi_driver_priority, utils.polling_response(2, 0, 2),
    )
