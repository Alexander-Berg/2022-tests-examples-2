#  pylint: disable=protected-access
# pylint: disable=C0302
import datetime
import json

import pytest

from metrics_processing.rules.common import RuleType

from taxi_driver_metrics.common.models import DmsEventsProvider
from taxi_driver_metrics.common.models import DriverInfo
from taxi_driver_metrics.common.models import Events
from taxi_driver_metrics.common.models import ItemBasedEntityProcessor
from taxi_driver_metrics.common.models import Processor
from taxi_driver_metrics.common.models import run_dms_processing
from taxi_driver_metrics.common.models.action import ActivityChangeAction
from taxi_driver_metrics.common.models.rules import rule_utils

SOME_UDID = '5b05621ee6c22ea2654849c0'
TST_UDID = '5b05621ee6c22ea2654849c9'
TST_ZONE = 'bangladesh'
TANKER_KEY = 'tk'
TIMESTAMP = datetime.datetime(2020, 2, 12)
EVENT_TIMESTAMP = TIMESTAMP - datetime.timedelta(seconds=5)
TST_PARAMS = {'max_batch_size': 10, 'worker_id': 1, 'workers_count': 2}

CRM_HUB_BASE_URL = '/crm-hub/'
NEW_COMMUNICATION_URL = f'{CRM_HUB_BASE_URL}v1/communication/new'


def _create_test_event(
        event_id='event_id',
        timestamp=EVENT_TIMESTAMP,
        udid=TST_UDID,
        event_type='test',
):
    return Events.UnifiedEvent(
        event_id=event_id,
        timestamp=timestamp,
        entity_id=udid,
        event_type=event_type,
    )


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.config(DRIVER_METRICS_USE_UNIFIED_PROCESSING=True)
async def test_run_dms_processing(stq3_context, patch):
    @patch('taxi_driver_metrics.common.models._processor.Processor.process')
    async def process(params):
        assert params == TST_PARAMS

    await run_dms_processing(stq3_context, **TST_PARAMS)
    assert process.calls


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.now(TIMESTAMP.isoformat())
async def test_starting_processing(stq3_context, dms_mockserver, patch):
    app = stq3_context
    processor = Processor(app)

    event = _create_test_event('37')
    await processor.event_provider.save_event(event)

    @patch(
        'metrics_processing.models.processor_abc.'
        'AbstractEntityProcessor.process_entity',
    )
    async def process_entity(entity_id, events, params):
        assert entity_id == TST_UDID
        assert all(params[k] == v for k, v in TST_PARAMS.items())
        assert events[0].entity_id == event.entity_id
        assert events[0].zone == event.zone
        assert events[0].order_id == event.order_id
        assert events[0].descriptor == event.descriptor
        assert events[0].event_type == event.event_type

    await processor.process(TST_PARAMS)
    assert process_entity.calls


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.now(TIMESTAMP.isoformat())
async def test_processing_events(stq3_context, dms_mockserver, patch):
    app = stq3_context
    processor = Processor(app)

    await processor.event_provider.save_event(
        _create_test_event('37', udid=TST_UDID),
    )
    await processor.event_provider.save_event(
        _create_test_event('38', udid=SOME_UDID),
    )

    @patch(
        'taxi_driver_metrics.common.models._new_processor.'
        'ItemBasedEntityProcessor._handle_event',
    )
    async def handle_event(params):
        assert all(params[k] == v for k, v in TST_PARAMS.items())

    @patch(
        'taxi_driver_metrics.common.models._new_processor.'
        'ItemBasedEntityProcessor._handle_event',
    )
    async def handle_event_new(params):
        assert all(params[k] == v for k, v in TST_PARAMS.items())

    await processor.process(TST_PARAMS)

    assert len(handle_event.calls) == 2 or len(handle_event_new.calls) == 2


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.config(
    DRIVER_METRICS_USE_UNIFIED_PROCESSING=True,
    DRIVER_METRICS_ENABLE_TAGGING_RULES=True,
)
@pytest.mark.rules_config(
    TAGGING={
        'default': [
            {
                'name': '2 events = f',
                'events_period_sec': 4000,
                'events_to_trigger_cnt': 2,
                'events': [{'topic': 'test'}],
                'actions': [
                    {'action': [{'type': 'tagging', 'tags': [{'name': 'f'}]}]},
                ],
            },
            {
                'name': '2 events = q',
                'events_period_sec': 4000,
                'events_to_trigger_cnt': 2,
                'events': [{'topic': 'not_test'}],
                'actions': [
                    {'action': [{'type': 'tagging', 'tags': [{'name': 'q'}]}]},
                ],
            },
        ],
    },
)
async def test_multiple_events_rules_new(
        stq3_context, dms_mockserver, caplog, tags_service_mock,
):
    def upload_check(*args, **kwargs):
        request = args[0]
        data = request.json
        assert data
        assert data['tags']
        entity_id = data['tags'][0]['match']['id']
        entity_type = data['entity_type']
        assert entity_id == TST_UDID
        assert entity_type == 'udid'

    tags_patch = tags_service_mock(upload_check=upload_check)
    app = stq3_context
    dms_mockserver.init_activity({TST_UDID: 93})
    event_provider = DmsEventsProvider(app)
    await event_provider.save_event(
        _create_test_event(event_id='history', event_type='not_test'),
    )
    await run_dms_processing(app, **TST_PARAMS)

    await event_provider.save_event(
        _create_test_event('current', event_type='not_test'),
    )
    await event_provider.save_event(_create_test_event('78'))
    await event_provider.save_event(_create_test_event('88'))

    await run_dms_processing(app, **TST_PARAMS)

    assert tags_patch.tags_upload.times_called == 2
    all_tags = []
    for record in caplog.records:
        if 'event_loggers' in record.pathname:
            log_data = json.loads(record.message)
            assert log_data['entity_id'] == TST_UDID
            assert log_data['entity_type'] == 'driver'
            # because id is incremental, can't exactly define
            assert 'event_id' in log_data
            assert 'event_type' in log_data
            assert 'event_zone' in log_data
            assert log_data['event_name'] == '__undefined__'
            assert log_data['context']['driver']['activity'] == 93
            all_tags.append(
                log_data['rules']['action_result']['tags'][0]['name'],
            )
    assert sorted(all_tags) == ['f', 'q']


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.config(DRIVER_METRICS_USE_UNIFIED_PROCESSING=True)
async def test_acquire_context(stq3_context, dms_mockserver, entity_processor):
    app = stq3_context

    event_provider = DmsEventsProvider(app)

    # fill history with some events
    await event_provider.save_event(_create_test_event('1'))
    await event_provider.save_event(_create_test_event('2'))
    await event_provider.save_event(_create_test_event('3'))
    await run_dms_processing(app, **TST_PARAMS)

    # pylint: disable=protected-access
    driver = await entity_processor._acquire_context(entity_id=TST_UDID)

    assert len(driver.events_history) == 3


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.config(
    DRIVER_METRICS_ENTITY_PROCESSING_CHUNK_SIZE=4,
    DRIVER_METRICS_USE_UNIFIED_PROCESSING=True,
    DRIVER_METRICS_ENABLE_TAGGING_RULES=True,
)
@pytest.mark.rules_config(
    TAGGING={
        'default': [
            {
                'name': 'async events',
                'events_period_sec': 4000,
                'events_to_trigger_cnt': 1,
                'events': [{'topic': 'test'}],
                'actions': [
                    {
                        'action': [
                            {'type': 'tagging', 'tags': [{'name': 'async'}]},
                            {
                                'type': 'tagging',
                                'tags': [{'name': 'another_tag'}],
                            },
                        ],
                    },
                ],
            },
        ],
    },
)
async def test_multiple_drivers_async(
        stq3_context, dms_mockserver, tags_service_mock,
):
    udid_calls = {TST_UDID: 0, SOME_UDID: 0}
    event_provider = DmsEventsProvider(stq3_context)

    def upload_check(*args, **kwargs):
        request = args[0]
        data = request.json
        assert data
        assert data['tags']
        entity_id = data['tags'][0]['match']['id']
        entity_type = data['entity_type']
        assert entity_id in (TST_UDID, SOME_UDID)
        udid_calls[entity_id] += 1
        assert entity_type == 'udid'

    tags_patch = tags_service_mock(upload_check=upload_check)

    app = stq3_context
    await event_provider.save_event(_create_test_event('1', udid=TST_UDID))

    await event_provider.save_event(_create_test_event('2', udid=SOME_UDID))

    await run_dms_processing(app, **TST_PARAMS)

    assert tags_patch.tags_upload.times_called == 4
    assert udid_calls == {TST_UDID: 2, SOME_UDID: 2}


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.parametrize('dms_activity', [92, 93, None])
@pytest.mark.config(
    DRIVER_METRICS_NEW_ACTIVITY_RULES={
        rule_utils.CONFIG_DEFAULT: [
            {
                'actions': [{'action': [{'type': 'activity', 'value': 5}]}],
                'events': [{'name': 'complete', 'topic': 'order'}],
                'name': 'ActivityTrip',
            },
        ],
    },
)
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
async def test_dms_abs(
        dms_activity,
        stq3_context,
        dms_mockserver,
        fake_event_provider,
        mockserver,
):
    app = stq3_context
    events_provider = DmsEventsProvider(app)

    dms_mockserver.init_activity({TST_UDID: dms_activity})

    driver = await DriverInfo.make(
        app,
        TST_UDID,
        fake_event_provider([]),
        TIMESTAMP,
        from_handler=False,
        starting_dms_activity=dms_activity,
    )
    activity = dms_mockserver.activity_storage.get(TST_UDID)

    assert driver.activity == dms_activity == activity

    await events_provider.save_event(
        Events.OrderEvent(
            event_id='event_id',
            timestamp=TIMESTAMP,
            entity_id=TST_UDID,
            descriptor=Events.EventTypeDescriptor(event_name='complete'),
        ),
    )

    await run_dms_processing(app, 1)

    driver = await DriverInfo.make(
        app, TST_UDID, fake_event_provider([]), TIMESTAMP,
    )
    activity = dms_mockserver.activity_storage.get(TST_UDID)

    assert driver.activity == activity
    assert driver.activity == 100 if dms_activity is None else dms_activity + 5


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.parametrize(
    'history_length, event_period',
    [(2, 46800), (1, 46799), (1, 7200), (0, 7199), (0, 3600), (0, 0)],
)
@pytest.mark.now(TIMESTAMP.isoformat())
async def test_event_period(
        stq3_context, dms_mockserver, history_length, event_period,
):
    app = stq3_context

    processing_params = {
        'master_worker_interval_msec': 800,
        'workers_num': 10,
        'max_delay_for_worker_spawn_msec': 50,
        'events_butch_size': 10,
        'event_period_seconds': event_period,
    }

    app.config.DRIVER_METRICS_EVENT_PROCESSING_PARAMS = processing_params

    old_timestamp = TIMESTAMP - datetime.timedelta(seconds=46800)
    new_timestamp = TIMESTAMP - datetime.timedelta(seconds=7200)

    entity_processor = ItemBasedEntityProcessor(app)
    # pylint:disable=protected-access
    await entity_processor._event_provider.save_event(
        Events.UnifiedEvent('event_id1', old_timestamp, TST_UDID),
    )
    await entity_processor._event_provider.save_event(
        Events.UnifiedEvent('event_id2', new_timestamp, TST_UDID),
    )
    await run_dms_processing(app, 100)

    # pylint: disable=protected-access
    context = await entity_processor._acquire_context(TST_UDID)

    assert len(context.events_history) == history_length


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
async def test_action_with_none_activity(stq3_context, patch):
    driver = DriverInfo(TST_UDID)

    assert driver.activity is None

    event = Events.UnifiedEvent(
        event_id='event_id', timestamp=TIMESTAMP, entity_id=TST_UDID,
    )

    action = ActivityChangeAction(
        app=stq3_context, event=event, entity=driver, value=30,
    )

    @patch(
        'taxi_driver_metrics.common.models.driver_info'
        '.DriverInfo._commit_unique_driver_changes',
    )
    async def _commit(*_a, **_kw):
        return

    await action.do_action()
    action.modify_local_context()

    assert driver.activity == 30


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.parametrize('dms_activity', [93, 94, None])
@pytest.mark.parametrize(
    'mongo_activity',
    [
        pytest.param(
            None, marks=[pytest.mark.filldb(unique_drivers='none_activity')],
        ),
        pytest.param(93, marks=[pytest.mark.filldb(unique_drivers='common')]),
    ],
)
@pytest.mark.now(TIMESTAMP.isoformat())
async def test_none_activity(
        stq3_context,
        dms_mockserver,
        dms_activity,
        mongo_activity,
        event_provider,
):
    app = stq3_context

    if dms_activity:
        dms_mockserver.init_activity({TST_UDID: dms_activity})

    event = Events.UnifiedEvent(
        event_id='event_id', timestamp=TIMESTAMP, entity_id=TST_UDID,
    )
    # pylint: disable=protected-access
    await event_provider.save_event(event)
    await run_dms_processing(app, 100)
    assert dms_mockserver.events_unprocessed_list.times_called == 1

    # actual logic
    expected_activity_to_set = dms_activity or 100
    if dms_activity:
        expected_activity_change = (
            expected_activity_to_set - dms_activity
        ) or None
    else:
        expected_activity_change = 100
    ##

    assert dms_mockserver.event_complete.times_called == 1
    complete_call = dms_mockserver.event_complete.next_call()['request'].json

    if expected_activity_change is not None:
        assert (
            complete_call['activity']['increment'] == expected_activity_change
        )
        assert (
            complete_call['activity']['value_to_set']
            == expected_activity_to_set
        )
    else:
        assert not complete_call.get('activity')


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.rules_config(
    LOYALTY={
        'default': [
            {
                'name': 'activity_1',
                'events': [{'topic': 'order'}],
                'actions': [{'action': [{'type': 'loyalty', 'value': 1}]}],
            },
        ],
        'moscow': [
            {
                'name': 'activity_2',
                'events': [{'topic': 'order'}],
                'actions': [{'action': [{'type': 'loyalty', 'value': 2}]}],
            },
        ],
        'node:submoscow': [
            {
                'name': 'activity_3',
                'events': [{'topic': 'order'}],
                'actions': [{'action': [{'type': 'loyalty', 'value': 3}]}],
            },
        ],
        'subsubmoscow': [
            {
                'name': 'activity_4',
                'events': [{'topic': 'order'}],
                'actions': [{'action': [{'type': 'loyalty', 'value': 4}]}],
            },
        ],
    },
)
@pytest.mark.config(DRIVER_METRICS_USE_AGGLOMERATIONS=True)
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'name': 'submoscow',
            'name_en': 'SubMoscow',
            'name_ru': 'ПодМосква',
            'node_type': 'node',
            'parent_name': 'br_root',
            'tariff_zones': ['subsubmoscow'],
        },
    ],
)
@pytest.mark.filldb(unique_drivers='common')
async def test_zone_references_processing(
        stq3_context, cached_journals, dms_mockserver, entity_processor, patch,
):
    # pylint: disable=protected-access
    app = stq3_context

    @patch(
        'taxi_driver_metrics.common.utils.'
        '_tags_manager.TagsManager'
        '.fetch_experiment_tags',
    )
    def _fetch_experiment_tags(*args, **kwargs):
        return {'use_agglomerations'}

    dms_mockserver.init_activity({TST_UDID: 30})

    event = Events.OrderEvent(
        descriptor=Events.EventTypeDescriptor('complete'),
        timestamp=TIMESTAMP,
        zone='subsubmoscow',
        driver_id='',
        event_id='123',
        order_id='order_id',
        entity_id=TST_UDID,
    )
    await entity_processor._event_provider.save_event(event)
    await run_dms_processing(app, 100)

    actions = cached_journals[-1].actions[RuleType.LOYALTY]

    actions_context = [{'accrual': item.action.accrual} for item in actions]

    # Because of subsubmoscow includes submoscow node results
    # is the triggered actions from zones default, submoscow and subsubmoscow
    assert actions_context == [{'accrual': 1}, {'accrual': 3}, {'accrual': 4}]


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.rules_config(
    LOYALTY={
        'default': [
            {
                'name': 'loyalty',
                'events': [{'topic': 'order'}],
                'actions': [
                    {
                        'action': [{'type': 'loyalty', 'value': 1}],
                        'expr': 'event.stable_random <= 0.3',
                    },
                    {
                        'action': [{'type': 'loyalty', 'value': 2}],
                        'expr': (
                            '0.3 < event.stable_random '
                            'and event.stable_random <= 0.8'
                        ),
                    },
                    {'action': [{'type': 'loyalty', 'value': 3}]},
                ],
            },
        ],
    },
)
@pytest.mark.parametrize('random_number', (r / 10 for r in range(10)))
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
async def test_random_numbers(
        stq3_context,
        cached_journals,
        dms_mockserver,
        entity_processor,
        patch,
        random_number,
):
    # pylint: disable=protected-access
    dms_mockserver.init_activity({TST_UDID: 30})

    @patch('random.random')
    def _():
        return random_number

    event = Events.OrderEvent(
        descriptor=Events.EventTypeDescriptor('complete'),
        timestamp=TIMESTAMP,
        zone='spb',
        driver_id='',
        event_id='123',
        order_id='order_id',
        entity_id=TST_UDID,
    )
    await entity_processor._event_provider.save_event(event)
    await run_dms_processing(stq3_context, 100)
    actions = cached_journals[-1].actions[RuleType.LOYALTY]
    actions_context = [{'accrual': item.action.accrual} for item in actions]

    if random_number <= 0.3:
        assert actions_context == [{'accrual': 1}]
    elif 0.3 < random_number <= 0.8:
        assert actions_context == [{'accrual': 2}]
    else:
        assert actions_context == [{'accrual': 3}]


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.config(DRIVER_METRICS_ENABLE_TAGGING_RULES=True)
@pytest.mark.rules_config(
    TAGGING={
        'default': [
            {
                'actions': [
                    {
                        'action': [
                            {
                                'campaign_id': 'communication_69',
                                'type': 'communications',
                                'entity_type': 'park_profile_id',
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'unique3',
            },
        ],
    },
)
@pytest.mark.filldb(unique_drivers='common')
async def test_processing_communications(
        stq3_context,
        taxi_config,
        mockserver,
        entity_processor,
        dms_mockserver,
):
    # pylint: disable=protected-access
    @mockserver.json_handler(NEW_COMMUNICATION_URL)
    async def mock_new_communication(*_args, **_kwargs):
        return

    event = Events.OrderEvent(
        descriptor=Events.EventTypeDescriptor('complete'),
        timestamp=TIMESTAMP,
        zone='spb',
        driver_id='driver_id',
        event_id='123',
        order_id='order_id',
        entity_id=TST_UDID,
        dbid_uuid='dbid',
    )
    await entity_processor._event_provider.save_event(event)
    await run_dms_processing(stq3_context, 100)

    assert mock_new_communication.times_called
    communications_call = mock_new_communication.next_call()['_args'][0].json
    del communications_call['event_timestamp']
    assert communications_call == {
        'campaign_id': 'communication_69',
        'entity_id': 'dbid',
        'event_id': '1',
        'extra_data': {
            'activity_value': 0,
            'descriptor': {'tags': None, 'type': 'complete'},
            'dispatch_id': None,
            'distance_to_a': 0,
            'driver_id': 'driver_id',
            'dtags': None,
            'rtags': None,
            'sp': None,
            'sp_alpha': None,
            'tariff_class': None,
            'time_to_a': 0,
            'replace_activity_with_priority': False,
            'calculate_priority': False,
        },
    }
