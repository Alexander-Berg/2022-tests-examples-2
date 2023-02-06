import dataclasses
import typing as tp

import pytest

from mayak_inspector.common import utils
from mayak_inspector.common.jobs import extras
from mayak_inspector.common.services import ydb_events_provider
from mayak_inspector.storage.ydb import extractors
from test_mayak_inspector.stq import data

ACTION_COMMON = {
    'action_entity_id': 'mock_entity',
    'entity_type': 'contractor',
    'extra': {'metric': 1},
    'mayak_entity_uuid': 1,
    'mayak_import_uuid': 1,
    'status': 1,
    'tariff': 'econom',
    'zone': 'helsinki',
}
DEFAULT_RESPONSES: tp.List[tp.Dict] = [
    {
        **ACTION_COMMON,
        'action_params': {
            'entity_type': 'udid',
            'merge_policy': 'append',
            'provider_id': 'mayak-inspector',
            'tags': [
                {'name': 'ManyOTsWarning', 'ttl': 86400, 'id': 'mock_entity'},
            ],
        },
        'action_type': 'tagging',
        'mayak_action_uuid': 4425687227968574465,
        'rule_name': 'unique',
        'status': 1,
        'triggered_context': {
            'entity': data.MOCK_ENTITY_EXP,
            'tags': ['experiment::test_experiment'],
        },
    },
    {
        **ACTION_COMMON,
        'action_params': {
            'entity_type': 'udid',
            'merge_policy': 'append',
            'provider_id': 'mayak-inspector',
            'tags': [{'name': 'Metric1', 'ttl': 86400, 'id': 'mock_entity'}],
        },
        'action_type': 'tagging',
        'mayak_action_uuid': 13515917785780548924,
        'rule_name': 'cancel',
        'status': 1,
        'triggered_context': {'entity': data.MOCK_ENTITY_EXP, 'tags': []},
    },
    {
        **ACTION_COMMON,
        'action_params': {
            'author': 'me',
            'comment': '',
            'description': '',
            'followers': '',
            'mark': 1,
            'message': 'you low_tariff is revoked',
            'queue': 'TEST',
            'summary': 'block_tariff Mayak',
            'summonees': '',
            'tariff': 'low_tariff',
        },
        'action_type': 'tariff_block_startrek',
        'mayak_action_uuid': 139403711115008247,
        'rule_name': 'batching',
        'status': 2,
        'triggered_context': {'entity': data.MOCK_ENTITY_EXP, 'tags': []},
    },
]
RESPONSES_DRY_RUN: tp.List[tp.Dict] = [
    {**res, 'status': 3} for res in DEFAULT_RESPONSES
]
SIMPLE_EVENT: tp.Dict = dict(
    name='32',
    event_id='333',
    event_type='batching_check',
    timestamp=utils.now(),
    entity_id='mock_entity',
    zone='helsinki',
    tariff='econom',
    extra_data={'metric': 1},
    mayak_entity_uuid=1,
)
EVENT_WRONG_TARIFF: tp.Dict = {**SIMPLE_EVENT, 'tariff': 'wrong_tariff'}


@pytest.mark.now('2022-04-01T00:00:00')
@pytest.mark.client_experiments3(
    consumer='mayak_inspector_consumer',
    experiment_name='test_experiment',
    args=[
        {'name': 'unique_driver_id', 'type': 'string', 'value': 'mock_entity'},
        {'name': 'tariff_group', 'type': 'string', 'value': 'econom'},
    ],
    value=123,
)
@pytest.mark.rules_config(
    DEFAULT={
        'default': [
            {
                'id': '1',
                'name': 'unique',
                'zone': 'default',
                'tariff': 'econom',
                'actions': [
                    {
                        'action': [
                            {
                                'tags': [
                                    {'name': 'ManyOTsWarning', 'ttl': 86400},
                                ],
                                'type': 'tagging',
                            },
                        ],
                    },
                ],
                'tags': '\'experiment::test_experiment\'',
                'events': [{'topic': 'batching_check'}],
            },
            {
                'id': '1',
                'name': 'cancel',
                'zone': 'default',
                'tariff': 'econom',
                'actions': [
                    {
                        'action': [
                            {
                                'tags': [{'name': 'Metric1', 'ttl': 86400}],
                                'type': 'tagging',
                            },
                        ],
                        'expr': 'event.extra_data_json[\'metric\'] >= 1',
                    },
                ],
                'events': [{'topic': 'batching_check'}],
            },
            {
                'id': '1',
                'name': 'batching',
                'zone': 'default',
                'tariff': 'econom',
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'tariff_block_startrek',
                                'author': 'me',
                                'queue': 'TEST',
                                'summary': 'block_tariff Mayak',
                                'tariff': 'low_tariff',
                                'message': 'you low_tariff is revoked',
                                'mark': 1,
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'batching_check'}],
            },
        ],
    },
)
@pytest.mark.config(
    DRIVER_METRICS_TARIFF_TOPOLOGIES={
        '__default__': {'__default__': {'__default__': ['__default__']}},
        'mayak-inspector': {
            '__default__': {
                'comfort': ['comfort', 'economy'],
                'econom': ['econom'],
            },
            'helsinki': {'comfort': ['children', 'comfort']},
        },
    },
    MAYAK_INSPECTOR_ACTION_TYPE_SETTINGS={
        'tagging': dict(dry_run=False),
        'tariff_block_startrek': dict(dry_run=False),
    },
)
@pytest.mark.parametrize(
    'events, actions, expected_counter',
    [
        pytest.param([SIMPLE_EVENT], DEFAULT_RESPONSES, 2, id='simple'),
        pytest.param(
            [SIMPLE_EVENT],
            RESPONSES_DRY_RUN,
            0,
            id='dry_run',
            marks=[
                pytest.mark.config(
                    MAYAK_INSPECTOR_ACTION_TYPE_SETTINGS={
                        'tagging': dict(dry_run=True),
                        'tariff_block_startrek': dict(dry_run=True),
                    },
                ),
            ],
        ),
        pytest.param([EVENT_WRONG_TARIFF], [], 0, id='wrong_tariff'),
    ],
)
async def test_process_entity(
        stq3_context,
        patch,
        events,
        actions,
        expected_counter,
        mock_actions_history,
        mock_processor,
):
    do_action_path = (
        'mayak_inspector.common.models.actions.base_action'
        '.AbstractAction._do'
    )
    actions_counter = 0

    @patch(do_action_path)
    async def _do():
        nonlocal actions_counter
        actions_counter += 1
        return actions_counter

    await mock_processor(events)

    assert mock_actions_history == actions
    assert actions_counter == expected_counter


@pytest.mark.now('2022-04-01T00:00:00')
async def test_event_provider(patch, stq3_context):
    repo_module = 'mayak_inspector.storage.ydb.metrics.MetricsRepo'

    @patch(repo_module + '.get_import')
    async def _get_import(*args, **kwargs):
        return extractors.ImportRecord(
            mayak_import_uuid=1,
            name=str(),
            locked=False,
            loaded=False,
            created_at=utils.make_deadline(eta_seconds=-1),
            updated_at=utils.now(),
        )

    cursor = extractors.MetricsCursor(0, 0, 0, 0, True)
    events = [
        extractors.MetricsRecord(
            mayak_entity_uuid=1,
            created_at=utils.now(),
            original_entity_id='a1',
            metrics={},
        ),
    ]

    @patch(repo_module + '.get_cursor')
    async def _get_cursor(*args, **kwargs):
        return cursor

    @patch(repo_module + '.get_metrics_with_cursor')
    async def _get_metrics_with_cursor(*args, **kwargs):
        return events, cursor

    provider = ydb_events_provider.MetricsEventsProvider(stq3_context)
    res = await provider.fetch_unprocessed_events(
        params=dict(
            job_params=extras.ReadMetrics('1', 0, 0),
            loaded=True,
            config=dict(),
        ),
    )
    assert dataclasses.asdict(res[0]) == dict(
        entity_id='a1',
        events=[
            dict(
                event_id='15712760647471980745',
                timestamp=events[0].created_at,
                entity_id='a1',
                zone='default',
                event_type='contractor',
                modified={},
                short_name='abs',
                name='__undefined__',
                extra_data={},
                tariff=None,
                mayak_entity_uuid=1,
                zone_chain=['default'],
            ),
        ],
        extra=None,
    )
