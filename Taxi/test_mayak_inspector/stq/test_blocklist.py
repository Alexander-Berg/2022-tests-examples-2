import typing as tp

import pytest

from mayak_inspector.common import utils
from test_mayak_inspector.stq import data as test_data


ACTION_COMMON = {
    'action_entity_id': 'mock_entity',
    'action_type': 'blocklist',
    'entity_type': 'contractor',
    'extra': {},
    'mayak_entity_uuid': 1,
    'mayak_import_uuid': 1,
    'rule_name': 'unique',
    'status': 1,
    'tariff': 'econom',
    'triggered_context': {'entity': test_data.MOCK_ENTITY, 'tags': []},
    'zone': 'helsinki',
}
DEFAULT_ACTIONS = [
    {
        **ACTION_COMMON,
        'action_params': {
            'entity_type': 'driver',
            'comment': 'internal comment for admin',
            'expires_after_min': 120,
            'mechanics': 'blocklist.mechanics.support_taxi_urgent',
            'message_key': (
                'blocklist.support_passenger_claim.aggressive_driver'
            ),
        },
        'mayak_action_uuid': 4425687227968574465,
    },
    {
        **ACTION_COMMON,
        'action_params': {
            'entity_type': 'car',
            'comment': 'internal comment for admin',
            'expires_after_min': 120,
            'mechanics': 'blocklist.mechanics.support_taxi_urgent',
            'message_key': (
                'blocklist.support_passenger_claim.wrong_license_plate'
            ),
        },
        'mayak_action_uuid': 12694725239660896804,
    },
]
ACTIONS_ERROR = [
    {
        **ACTION_COMMON,
        'action_entity_id': 'wrong_udid',
        'action_params': {
            'entity_type': 'driver',
            'comment': 'internal comment for admin',
            'expires_after_min': 120,
            'mechanics': 'blocklist.mechanics.support_taxi_urgent',
            'message_key': (
                'blocklist.support_passenger_claim.aggressive_driver'
            ),
        },
        'mayak_action_uuid': 15341855544509417885,
        'status': 4,
        'triggered_context': {'entity': test_data.WRONG_ENTITY, 'tags': []},
    },
    {
        **ACTION_COMMON,
        'action_entity_id': 'wrong_udid',
        'action_params': {
            'entity_type': 'car',
            'comment': 'internal comment for admin',
            'expires_after_min': 120,
            'mechanics': 'blocklist.mechanics.support_taxi_urgent',
            'message_key': (
                'blocklist.support_passenger_claim.wrong_license_plate'
            ),
        },
        'mayak_action_uuid': 12350672509064291168,
        'status': 4,
        'triggered_context': {'entity': test_data.WRONG_ENTITY, 'tags': []},
    },
]
SKIPPED_ACTIONS: tp.List[tp.Dict] = [
    {**DEFAULT_ACTIONS[0], 'status': 4},
    {**DEFAULT_ACTIONS[1], 'status': 4},
]

DEFAULT_RULE = {
    'id': '1',
    'name': 'unique',
    'zone': 'default',
    'tariff': 'econom',
    'actions': [
        {
            'action': [
                {
                    'entity_type': 'driver',
                    'type': 'blocklist',
                    'comment': 'internal comment for admin',
                    'mechanics': 'blocklist.mechanics.support_taxi_urgent',
                    'expires_after_min': 120,
                    'message_key': (
                        'blocklist.support_passenger_claim'
                        '.aggressive_driver'
                    ),
                },
                {
                    'entity_type': 'car',
                    'type': 'blocklist',
                    'comment': 'internal comment for admin',
                    'mechanics': 'blocklist.mechanics.support_taxi_urgent',
                    'expires_after_min': 120,
                    'message_key': (
                        'blocklist.support_passenger_claim'
                        '.wrong_license_plate'
                    ),
                },
            ],
        },
    ],
    'events': [{'topic': 'batching_check'}],
}
DEFAULT_EVENT = dict(
    name='32',
    event_id='333',
    event_type='batching_check',
    timestamp=utils.now(),
    entity_id='mock_entity',
    zone='helsinki',
    tariff='econom',
    mayak_entity_uuid=1,
)
WRONG_UID_EVENT: tp.Dict = {**DEFAULT_EVENT, 'entity_id': 'wrong_udid'}
DEFAULT_HEADERS = [
    ('4333208194337163425', '123', 'robot-test'),
    ('16858613320571086120', '123', 'robot-test'),
]


@pytest.mark.now('2022-04-01T00:00:00')
@pytest.mark.rules_config(DEFAULT={'default': [DEFAULT_RULE]})
@pytest.mark.config(
    DRIVER_METRICS_TARIFF_TOPOLOGIES={
        '__default__': {'__default__': {'__default__': ['econom']}},
    },
)
@pytest.mark.parametrize(
    'events, expected_headers, expected_queries, expected_history',
    [
        pytest.param(
            [DEFAULT_EVENT],
            DEFAULT_HEADERS,
            [
                {
                    'comment': 'internal comment for admin',
                    'expires': '2022-04-01T05:00:00+03:00',
                    'kwargs': {'license_id': 'pd_id_park_mock_entity'},
                    'mechanics': 'blocklist.mechanics.support_taxi_urgent',
                    'predicate_id': '33333333-3333-3333-3333-333333333333',
                    'reason': {
                        'key': (
                            'blocklist.support_passenger_claim'
                            '.aggressive_driver'
                        ),
                    },
                },
                {
                    'comment': 'internal comment for admin',
                    'expires': '2022-04-01T05:00:00+03:00',
                    'kwargs': {
                        'car_number': (
                            'car_number_park_car_id_park_mock_entity'
                        ),
                    },
                    'mechanics': 'blocklist.mechanics.support_taxi_urgent',
                    'predicate_id': '11111111-1111-1111-1111-111111111111',
                    'reason': {
                        'key': (
                            'blocklist.support_passenger_claim'
                            '.wrong_license_plate'
                        ),
                    },
                },
            ],
            DEFAULT_ACTIONS,
            id='default',
        ),
        pytest.param(
            [WRONG_UID_EVENT], [], [], ACTIONS_ERROR, id='wrong_udid',
        ),
    ],
)
@pytest.mark.config(
    MAYAK_INSPECTOR_ACTION_TYPE_SETTINGS={'blocklist': dict(dry_run=False)},
)
async def test_blocklist(
        stq3_context,
        patch,
        mockserver,
        events,
        expected_headers,
        expected_queries,
        expected_history,
        mock_actions_history,
        mock_processor,
):
    @mockserver.json_handler('/tags/v1/match')
    async def tags_match(*args, **kwargs):
        return {}

    headers = list()
    queries = list()

    @mockserver.json_handler('/blocklist/admin/blocklist/v1/add')
    async def blocklist_add(request, *args, **kwargs):
        headers.append(
            (
                request.headers['X-Idempotency-Token'],
                request.headers['X-Yandex-Uid'],
                request.headers['X-Yandex-Login'],
            ),
        )

        data = request.json
        queries.append(data)
        return {'block_id': '123'}

    await mock_processor(events)

    assert tags_match.times_called or not expected_history
    assert blocklist_add.times_called or not expected_queries
    assert headers == expected_headers
    assert queries == expected_queries
    assert mock_actions_history == expected_history


@pytest.mark.now('2022-04-01T00:00:00')
@pytest.mark.rules_config(DEFAULT={'default': [DEFAULT_RULE]})
@pytest.mark.config(
    DRIVER_METRICS_TARIFF_TOPOLOGIES={
        '__default__': {'__default__': {'__default__': ['econom']}},
    },
)
@pytest.mark.parametrize(
    'events, passed_since_min, expected_history',
    [
        pytest.param(
            [DEFAULT_EVENT],
            0,
            SKIPPED_ACTIONS,
            id='still_blocked',
            marks=[
                pytest.mark.config(
                    MAYAK_INSPECTOR_ACTION_TYPE_SETTINGS={
                        'blocklist': dict(dry_run=False),
                    },
                ),
            ],
        ),
        pytest.param(
            [DEFAULT_EVENT],
            150,  # 150 > action.params.expires_min
            SKIPPED_ACTIONS,
            id='on_cooldown',
            marks=[
                pytest.mark.config(
                    MAYAK_INSPECTOR_ACTION_TYPE_SETTINGS={
                        'blocklist': dict(
                            dry_run=False, minimum_interval_min=60,
                        ),
                    },
                ),
            ],
        ),
        pytest.param(
            [DEFAULT_EVENT],
            150,
            DEFAULT_ACTIONS,
            id='after_cooldown',
            marks=[
                pytest.mark.config(
                    MAYAK_INSPECTOR_ACTION_TYPE_SETTINGS={
                        'blocklist': dict(
                            dry_run=False, minimum_interval_min=15,
                        ),
                    },
                ),
            ],
        ),
    ],
)
async def test_blocklist_repeat(
        stq3_context,
        patch,
        mockserver,
        events,
        passed_since_min,
        expected_history,
        mock_actions_history,
        mock_processor,
        mock_get_actions_history_last,
):
    @mockserver.json_handler('/tags/v1/match')
    async def tags_match(*args, **kwargs):
        return {}

    @mockserver.json_handler('/blocklist/admin/blocklist/v1/add')
    async def _blocklist_add(_request, *args, **kwargs):
        return {'block_id': '123'}

    updated_at = utils.make_deadline(eta_seconds=-passed_since_min * 60)
    mock_get_actions_history_last(DEFAULT_ACTIONS, updated_at)

    await mock_processor(events)

    assert tags_match.times_called or not expected_history
    assert mock_actions_history == expected_history
