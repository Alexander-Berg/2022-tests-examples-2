import typing as tp

import pytest

from mayak_inspector.common import utils
from test_mayak_inspector.stq import data as test_data


DEFAULT_EVENT = {
    'name': '32',
    'event_id': '333',
    'event_type': 'batching_check',
    'timestamp': utils.now(),
    'entity_id': 'mock_entity',
    'zone': 'helsinki',
    'mayak_entity_uuid': 1,
    'tariff': 'econom',
}
WRONG_UID_EVENT: tp.Dict = {**DEFAULT_EVENT, 'entity_id': 'wrong_udid'}

ACTION_COMMON = {
    'action_entity_id': 'mock_entity',
    'action_type': 'qc_invites',
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
ACTION_PARAMS_COMMON = {'comment': 'Razberites s gospodinom', 'exam': 'dkvu'}

DEFAULT_ACTIONS = [
    {
        **ACTION_COMMON,
        'action_params': {
            **ACTION_PARAMS_COMMON,
            'entity_type': 'driver',
            'reason': {'keys': ['first_key', 'second_key']},
            'sanctions': ['no_macdonalds'],
            'media': ['lol'],
            'expires_after_sec': 10,
        },
        'mayak_action_uuid': 4425687227968574465,
        'triggered_context': {'entity': test_data.MOCK_ENTITY, 'tags': []},
    },
    {
        **ACTION_COMMON,
        'action_params': {**ACTION_PARAMS_COMMON, 'entity_type': 'car'},
        'mayak_action_uuid': 12694725239660896804,
        'triggered_context': {'entity': test_data.MOCK_ENTITY, 'tags': []},
    },
]
ACTIONS_ERROR = [
    {
        **ACTION_COMMON,
        'action_entity_id': 'wrong_udid',
        'action_params': {
            **ACTION_PARAMS_COMMON,
            'entity_type': 'driver',
            'reason': {'keys': ['first_key', 'second_key']},
            'sanctions': ['no_macdonalds'],
            'media': ['lol'],
            'expires_after_sec': 10,
        },
        'mayak_action_uuid': 15341855544509417885,
        'status': 4,
        'triggered_context': {'entity': test_data.WRONG_ENTITY, 'tags': []},
    },
    {
        **ACTION_COMMON,
        'action_entity_id': 'wrong_udid',
        'action_params': {**ACTION_PARAMS_COMMON, 'entity_type': 'car'},
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
                    **ACTION_PARAMS_COMMON,
                    'type': 'qc_invites',
                    'entity_type': 'driver',
                    'expires_after_sec': 10,
                    'reason': {'keys': ['first_key', 'second_key']},
                    'sanctions': ['no_macdonalds'],
                    'media': ['lol'],
                },
                {
                    **ACTION_PARAMS_COMMON,
                    'type': 'qc_invites',
                    'entity_type': 'car',
                },
            ],
        },
    ],
    'events': [{'topic': 'batching_check'}],
}
DEFAULT_HEADERS = [
    ('4333208194337163425', '123', 'robot-test'),
    ('16858613320571086120', '123', 'robot-test'),
]


@pytest.mark.now('2022-04-01T00:00:00')
@pytest.mark.rules_config(DEFAULT={'default': [DEFAULT_RULE]})
@pytest.mark.parametrize(
    'events, expected_headers, expected_queries, expected_history',
    [
        pytest.param(
            [DEFAULT_EVENT],
            DEFAULT_HEADERS,
            [
                {
                    **ACTION_PARAMS_COMMON,
                    'entity_type': 'driver',
                    'expires': '2022-04-01T03:00:10+03:00',
                    'filters': {'license_pd_id': 'pd_id_park_mock_entity'},
                    'identity_type': 'service',
                    'media': ['lol'],
                    'reason': {'keys': ['first_key', 'second_key']},
                    'sanctions': ['no_macdonalds'],
                },
                {
                    **ACTION_PARAMS_COMMON,
                    'entity_type': 'car',
                    'filters': {
                        'car_number': (
                            'car_number_park_car_id_park_mock_entity'
                        ),
                    },
                    'identity_type': 'service',
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
    MAYAK_INSPECTOR_ACTION_TYPE_SETTINGS={'qc_invites': dict(dry_run=False)},
)
@pytest.mark.config(
    DRIVER_METRICS_TARIFF_TOPOLOGIES={
        '__default__': {'__default__': {'__default__': ['econom']}},
    },
)
async def test_qc_invites(
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

    @mockserver.json_handler('/qc-invites/admin/qc-invites/v1/invite')
    async def qc_invite(request, *args, **kwargs):
        headers.append(
            (
                request.headers['X-Idempotency-Token'],
                request.headers['X-Yandex-Uid'],
                request.headers['X-Yandex-Login'],
            ),
        )

        data = request.json
        queries.append(data)
        return {'invite_id': '123'}

    await mock_processor(events)

    assert tags_match.times_called or not expected_history
    assert qc_invite.times_called or not expected_queries
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
            id='not_expired',
            marks=[
                pytest.mark.config(
                    MAYAK_INSPECTOR_ACTION_TYPE_SETTINGS={
                        'qc_invites': dict(dry_run=False),
                    },
                ),
            ],
        ),
        pytest.param(
            [DEFAULT_EVENT],
            1,  # 1 minute > action.params.expires_after_sec
            SKIPPED_ACTIONS,
            id='on_cooldown',
            marks=[
                pytest.mark.config(
                    MAYAK_INSPECTOR_ACTION_TYPE_SETTINGS={
                        'qc_invites': dict(
                            dry_run=False, minimum_interval_min=60,
                        ),
                    },
                ),
            ],
        ),
        pytest.param(
            [DEFAULT_EVENT],
            61,
            DEFAULT_ACTIONS,
            id='after_cooldown',
            marks=[
                pytest.mark.config(
                    MAYAK_INSPECTOR_ACTION_TYPE_SETTINGS={
                        'qc_invites': dict(
                            dry_run=False, minimum_interval_min=60,
                        ),
                    },
                ),
            ],
        ),
    ],
)
async def test_qc_invites_repeat(
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

    @mockserver.json_handler('/qc-invites/admin/qc-invites/v1/invite')
    async def _qc_invite(_request, *args, **kwargs):
        return {'invite_id': '123'}

    updated_at = utils.make_deadline(eta_seconds=-passed_since_min * 60)
    mock_get_actions_history_last(DEFAULT_ACTIONS, updated_at)

    await mock_processor(events)

    assert tags_match.times_called or not expected_history
    assert mock_actions_history == expected_history
