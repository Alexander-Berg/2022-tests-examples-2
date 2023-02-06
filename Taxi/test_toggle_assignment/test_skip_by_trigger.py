import copy
import datetime
import json

import pytest

from tests_dispatch_buffer import utils
from tests_dispatch_buffer.test_toggle_assignment import data


@pytest.mark.config(
    DISPATCH_BUFFER_ENABLED=False,
    DISPATCH_BUFFER_ETA_TRIGGER={
        '__default__': {
            '__default__': [
                {'ETA': 400, 'TIME_IN_BUFFER': 1500},
                {'ETA': 600, 'TIME_IN_BUFFER': 2500},
            ],
        },
    },
    DISPATCH_BUFFER_SURGE_TRIGGER={
        '__default__': {
            '__default__': [
                {'SURGE': 2.0, 'TIME_IN_BUFFER': 1000},
                {'SURGE': 4.0, 'TIME_IN_BUFFER': 2000},
            ],
        },
    },
    DELAYED_SECONDS_TO_DUE_TO_START_LOOKUP=1,
)
@pytest.mark.parametrize(
    'surge_value, eta, agglomeration_delay, assigned',
    [(0, 0, 0, 1), (2.0, 0, 0, 0), (0, 400, 0, 0), (0, 0, 2000, 0)],
)
async def test_skip_by_triggers(
        taxi_dispatch_buffer,
        taxi_dispatch_buffer_monitor,
        mocked_time,
        pgsql,
        mockserver,
        testpoint,
        taxi_config,
        surge_value,
        eta,
        agglomeration_delay,
        assigned,
        experiments3,
):
    order_meta = copy.deepcopy(data.ORDER_META)
    order_meta['order']['request']['surge_price'] = surge_value
    created = mocked_time.now().replace(tzinfo=datetime.timezone.utc)
    due = created + datetime.timedelta(minutes=9)
    order_meta['order']['request']['due'] = due.timestamp()
    order_meta['order']['created'] = created.timestamp()

    candidate = copy.deepcopy(data.CANDIDATE)
    candidate['route_info']['time'] = eta

    experiments3.add_config(
        **utils.agglomeration_settings(
            'example_agglomeration',
            {
                'ENABLED': True,
                'OLD_LOOKUP_FALLBACK_WAIT_SECONDS': 30,
                'DISPATCH_ORDER_AFTER_FIRST_RUN_SECONDS': agglomeration_delay,
                'RUNNING_INTERVAL': 60,
                'APPLY_RESULTS': False,
                'APPLY_ALGORITHM': 'hungarian',
                'ORDERS_LIMIT': 0,
            },
        ),
    )
    mocked_time.set(created)
    await taxi_dispatch_buffer.invalidate_caches()

    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert request.headers.get('Content-Type') == 'application/json'
        candidate2 = copy.deepcopy(candidate)
        candidate2['dbid'] = 'dbid1'
        candidate2['uuid'] = 'uuid1'
        candidate2['id'] = f'{candidate2["dbid"]}_{candidate2["uuid"]}'
        candidate2['route_info']['time'] = 0

        return {'candidates': [candidate, candidate2]}

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock_driver_scoring_bulk(request):
        return {'responses': [data.SCORING_RESPONSE]}

    @mockserver.json_handler('/lookup/event')
    def _mock_lookup_event(raw_request):
        request = json.loads(raw_request.get_data())
        assert request.get('status') == 'found'
        assert request.get('candidate') == candidate

        return {
            'status': True,
            'timeout_ms': 200,
            'attempts': 1,
            'callback': {
                'url': (
                    mockserver.url('/lookup/event')
                    + '?order_id=8fa174f64a0b4d8488395bc9f652addd'
                ),
                'timeout_ms': 300,
                'attempts': 1,
            },
        }

    @testpoint('assignment_stats')
    def assignment_stats(t_data):
        return t_data

    utils.insert_order(
        pgsql,
        service='taxi',
        user_id='user_id',
        order_id='8fa174f64a0b4d8488395bc9f652addd',
        zone_id='example',
        classes='{"econom"}',
        agglomeration='example_agglomeration',
        created=created,
        due=due,
        dispatch_status='idle',
        order_meta=json.dumps(order_meta),
    )

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    stats = (await assignment_stats.wait_call())['t_data']
    assert stats['pending_orders'] == 1
    assert stats['dispatched_orders'] == assigned

    if assigned == 0:
        mocked_time.set(created + datetime.timedelta(seconds=15))
        await taxi_dispatch_buffer.tests_control(invalidate_caches=False)

        metrics = await taxi_dispatch_buffer_monitor.get_metric(
            'dispatch_buffer_metrics',
        )
        metrics = metrics['example_agglomeration']['']['business']
        assert metrics['taxi']['eta_delay_applied'] == 1


@pytest.mark.config(
    DISPATCH_BUFFER_ENABLED=False,
    DISPATCH_BUFFER_ETA_TRIGGER={
        '__default__': {
            '__default__': [
                {'ETA': 400, 'TIME_IN_BUFFER': 1500},
                {'ETA': 600, 'TIME_IN_BUFFER': 2500},
            ],
        },
    },
    DISPATCH_BUFFER_SURGE_TRIGGER={
        '__default__': {
            '__default__': [
                {'SURGE': 2.0, 'TIME_IN_BUFFER': 1000},
                {'SURGE': 4.0, 'TIME_IN_BUFFER': 2000},
            ],
        },
    },
)
async def test_disable_eta_delay_flag(
        taxi_dispatch_buffer,
        pgsql,
        mockserver,
        testpoint,
        taxi_config,
        mocked_time,
):
    order_meta = copy.deepcopy(data.ORDER_META)
    order_meta['order']['request']['surge_price'] = 0
    created = mocked_time.now().replace(tzinfo=datetime.timezone.utc)
    due = created + datetime.timedelta(minutes=9)
    order_meta['order']['request']['due'] = due.timestamp()
    order_meta['order']['created'] = created.timestamp()
    candidate = copy.deepcopy(data.CANDIDATE)
    candidate['route_info']['time'] = 0
    taxi_config.set_values(
        dict(
            DISPATCH_BUFFER={
                'example_agglomeration': {
                    'ENABLED': True,
                    'ZONES': ['example'],
                    'OLD_LOOKUP_FALLBACK_WAIT_SECONDS': 30,
                    'DISPATCH_ORDER_AFTER_FIRST_RUN_SECONDS': 2000,
                    'RUNNING_INTERVAL': 60,
                    'APPLY_RESULTS': False,
                    'APPLY_ALGORITHM': 'hungarian',
                    'ORDERS_LIMIT': 0,
                },
            },
        ),
    )
    mocked_time.set(created)
    await taxi_dispatch_buffer.invalidate_caches()

    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert request.headers.get('Content-Type') == 'application/json'
        candidate2 = copy.deepcopy(candidate)
        candidate2['dbid'] = 'dbid1'
        candidate2['uuid'] = 'uuid1'
        candidate2['id'] = f'{candidate2["dbid"]}_{candidate2["uuid"]}'
        candidate2['route_info']['time'] = 0
        return {'candidates': [candidate, candidate2]}

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock_driver_scoring_bulk(request):
        return {
            'responses': [
                {
                    'candidates': [{'id': 'dbid0_uuid0', 'score': 200}],
                    'search': {
                        'order_id': '8fa174f64a0b4d8488395bc9f652addd',
                        'disable_eta_delay': True,
                    },
                },
            ],
        }

    @mockserver.json_handler('/lookup/event')
    def _mock_lookup_event(raw_request):
        request = json.loads(raw_request.get_data())
        assert request.get('status') == 'found'
        assert request.get('candidate') == candidate

        return {
            'status': True,
            'timeout_ms': 200,
            'attempts': 1,
            'callback': {
                'url': (
                    mockserver.url('/lookup/event')
                    + '?order_id=8fa174f64a0b4d8488395bc9f652addd'
                ),
                'timeout_ms': 300,
                'attempts': 1,
            },
        }

    @testpoint('assignment_stats')
    def assignment_stats(t_data):
        return t_data

    utils.insert_order(
        pgsql,
        service='taxi',
        user_id='user_id',
        order_id='8fa174f64a0b4d8488395bc9f652addd',
        zone_id='example',
        classes='{"econom"}',
        agglomeration='example_agglomeration',
        created=created,
        due=due,
        dispatch_status='idle',
        order_meta=json.dumps(order_meta),
    )

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    stats = (await assignment_stats.wait_call())['t_data']
    assert stats['pending_orders'] == 1
    assert stats['dispatched_orders'] == 1
