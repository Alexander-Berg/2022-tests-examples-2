import collections
import copy
import datetime
import json

import pytest

from tests_dispatch_buffer import utils

ORDER_ID_1 = 'order_id_1'
ORDER_ID_2 = 'order_id_2'
ORDER_ID_3 = 'order_id_3'
ORDER_ID_4 = 'order_id_4'
ORDER_ID_5 = 'order_id_5'
DBID_1 = 'dbid1'
DBID_2 = 'dbid2'
DBID_3 = 'dbid3'
UUID_1 = 'uuid1'
UUID_2 = 'uuid2'
UUID_3 = 'uuid3'

ORDER_META = {
    'allowed_classes': ['econom'],
    'point': [37.622648, 55.756032],
    'destination': [37.622648, 55.756032],
    'order': {
        'nearest_zone': 'example',
        'created': (
            datetime.datetime.now() + datetime.timedelta(hours=1)
        ).timestamp(),
        'request': {
            'source': {'geopoint': [37.622648, 55.756032]},
            'due': (
                datetime.datetime.now() + datetime.timedelta(hours=1)
            ).timestamp(),
        },
    },
    'service': 'taxi',
}

RAW_CANDIDATE = {
    'car_number': 'some_number',
    'allowed_classes': ['econom'],
    'unique_driver_id': 'some_id',
    'position': [37.622647, 55.756032],
    'profile': {'grades': {'g_econom': 1, 'g_minivan': 1}},
    'route_info': {'distance': 15000, 'time': 200, 'approximate': False},
    'license_id': 'license_id',
    'status': {'driver': 'free'},
    'chain_info': {
        'destination': [55.0, 35.0],
        'left_dist': 100,
        'left_time': 10,
        'order_id': 'some_order_id',
    },
    'metadata': {'reposition_check_required': False},
}

ASSIGNMENT_REQUEST = {
    ORDER_ID_1: [
        {
            'dbid': DBID_1,
            'uuid': UUID_1,
            'route_time': 100,
            'route_dist': 3000,
        },
        {
            'dbid': DBID_2,
            'uuid': UUID_2,
            'route_time': 300,
            'route_dist': 1000,
        },
    ],
    ORDER_ID_2: [],
    ORDER_ID_3: [
        {
            'dbid': DBID_3,
            'uuid': UUID_3,
            'route_time': 200,
            'route_dist': 1000,
        },
    ],
}

SCORING_RESPONSE = [
    {'candidates': [{'id': f'{DBID_1}_{UUID_1}', 'score': 200}]},
    {'candidates': [{'id': f'{DBID_3}_{UUID_3}', 'score': 200}]},
]


def create_candidate(dbid, uuid, route_time, route_dist):
    result = copy.deepcopy(RAW_CANDIDATE)
    result['id'] = f'{dbid}_{uuid}'
    result['dbid'] = dbid
    result['uuid'] = uuid
    result['route_info']['time'] = route_time
    result['route_info']['distance'] = route_dist
    return result


def _insert_order(pgsql, **kwargs):
    now = datetime.datetime.now()

    order_meta = copy.deepcopy(ORDER_META)
    order_meta.update(kwargs)
    if kwargs.get('classes') is not None:
        order_meta['allowed_classes'] = [kwargs['classes'][2:-2]]

    params = {
        'service': 'taxi',
        'user_id': 'user_id',
        'zone_id': 'moscow',
        'agglomeration': 'example_agglomeration',
        'created': now + datetime.timedelta(hours=1),
        'dispatch_status': 'idle',
        'classes': '{"econom"}',
        'order_lookup': 'ROW(0,1,3)',
        'order_meta': json.dumps(order_meta),
    }
    params.update(kwargs)

    utils.insert_order(pgsql, **params)


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.config(
    METRIX_AGGREGATION=[
        {
            'rule': {'and': [{'none_of': []}]},
            'value': [
                {
                    'rule_type': 'grouping',
                    'label_name': 'tariff_group',
                    'groups': [
                        {
                            'group_name': 'econom_group',
                            'values': ['econom', 'uberstart'],
                        },
                        {
                            'group_name': 'business_group',
                            'values': ['business', 'comfortplus'],
                        },
                    ],
                    'use_others': False,
                },
            ],
        },
    ],
)
async def test_assignment_metrics(
        taxi_dispatch_buffer,
        pgsql,
        mockserver,
        taxi_dispatch_buffer_monitor,
        mocked_time,
):
    await taxi_dispatch_buffer.tests_control(reset_metrics=True)

    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        order_id = request.json['order_id']
        drivers = ASSIGNMENT_REQUEST.get(order_id, [])
        response = {'candidates': []}
        for driver in drivers:
            response['candidates'].append(
                create_candidate(
                    driver['dbid'],
                    driver['uuid'],
                    driver['route_time'],
                    driver['route_dist'],
                ),
            )
        return response

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock_driver_scoring_bulk(_):
        return {'responses': SCORING_RESPONSE}

    now = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    mocked_time.set(now)
    await taxi_dispatch_buffer.tests_control(invalidate_caches=False)

    orders_kwargs = [
        {'order_id': ORDER_ID_1},
        {'order_id': ORDER_ID_2, 'draw_cnt': 3},
        {'order_id': ORDER_ID_3, 'classes': '{"business"}'},
        {
            'order_id': ORDER_ID_4,
            'classes': '{"business"}',
            'dispatch_status': 'dispatched',
        },
        {'order_id': ORDER_ID_5, 'dispatch_status': 'removed'},
    ]
    for order_kwargs in orders_kwargs:
        _insert_order(pgsql, **order_kwargs)

    await taxi_dispatch_buffer.run_periodic_task('buffer-statistics')

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    mocked_time.set(now + datetime.timedelta(seconds=6))
    await taxi_dispatch_buffer.tests_control(invalidate_caches=False)

    metrics = await taxi_dispatch_buffer_monitor.get_metric(
        'dispatch_buffer_metrics',
    )

    by_tariff = metrics['example_agglomeration']['']
    asserts = {
        'econom_group': [
            ('orders_dispatched_in_draw', 1.0),
            ('orders_in_draw', 2.0),
            ('orders_new_in_draw', 1.0),
            ('orders_in_buffer', 3.0),
            ('orders_without_candidates', 1.0),
            ('orders_with_minimal_score_winner', 1.0),
            ('candidates_in_draw', 2.0),
            ('candidates_in_draw_after_filtering', 1.0),
        ],
        'business_group': [
            ('orders_dispatched_in_draw', 1.0),
            ('orders_in_draw', 1.0),
            ('orders_new_in_draw', 1.0),
            ('orders_in_buffer', 2.0),
            ('orders_with_minimal_score_winner', 1.0),
            ('candidates_in_draw', 1.0),
            ('candidates_in_draw_after_filtering', 1.0),
        ],
    }
    all_tariffs_expected = collections.defaultdict(int)
    all_tariffs_got = collections.defaultdict(int)
    for tariff, a_metrics in asserts.items():
        for true_metric in a_metrics:
            assert by_tariff[tariff]['taxi'][true_metric[0]] == true_metric[1]
            all_tariffs_expected[true_metric[0]] += true_metric[1]
            all_tariffs_got[true_metric[0]] += by_tariff[tariff]['taxi'][
                true_metric[0]
            ]

    for key in all_tariffs_expected:
        assert all_tariffs_expected[key] == all_tariffs_got[key]

    by_status = metrics['example_agglomeration']
    assert by_status['idle']['']['taxi']['orders_in_buffer'] == 3.0
    assert by_status['dispatched']['']['taxi']['orders_in_buffer'] == 1.0
    assert by_status['removed']['']['taxi']['orders_in_buffer'] == 1.0

    eta_time_in_draw = by_status['']['']['taxi']['eta_time_in_draw']
    assert eta_time_in_draw['p0'] == 100
    assert eta_time_in_draw['p100'] == 200

    eta_dist_in_draw = by_status['']['']['taxi']['eta_dist_in_draw']
    assert eta_dist_in_draw['p0'] == 1000
    assert eta_dist_in_draw['p100'] == 2047

    score_in_draw = by_status['']['']['taxi']['score_in_draw']
    assert score_in_draw['p0'] == 200
    assert score_in_draw['p100'] == 200


@pytest.mark.pgsql('driver_dispatcher', files=['dispatch_meta_insert.sql'])
@pytest.mark.suspend_periodic_tasks('buffer-statistics')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.config(
    METRIX_AGGREGATION=[
        {
            'rule': {'and': [{'none_of': []}]},
            'value': [
                {
                    'rule_type': 'grouping',
                    'label_name': 'tariff_group',
                    'groups': [
                        {
                            'group_name': 'econom_group',
                            'values': ['econom', 'uberstart'],
                        },
                        {
                            'group_name': 'business_group',
                            'values': ['business', 'comfortplus'],
                        },
                    ],
                    'use_others': False,
                },
            ],
        },
    ],
)
async def test_buffer_metrics(
        taxi_dispatch_buffer, taxi_dispatch_buffer_monitor, mocked_time,
):
    now = datetime.datetime.utcnow()
    mocked_time.set(now)
    await taxi_dispatch_buffer.tests_control(invalidate_caches=False)

    await taxi_dispatch_buffer.run_periodic_task('buffer-statistics')

    mocked_time.set(now + datetime.timedelta(seconds=6))
    await taxi_dispatch_buffer.tests_control(invalidate_caches=False)

    metrics = await taxi_dispatch_buffer_monitor.get_metric(
        'dispatch_buffer_metrics',
    )

    # agglomeration -> status -> tariff -> metrics
    assert metrics['']['']['']['taxi']['orders_in_buffer'] == 3

    assert metrics['']['idle']['']['taxi']['orders_in_buffer'] == 2
    assert metrics['']['dispatched']['']['taxi']['orders_in_buffer'] == 1
