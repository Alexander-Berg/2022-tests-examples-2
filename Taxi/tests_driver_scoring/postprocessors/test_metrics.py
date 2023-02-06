import datetime

import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets

BODY_1 = {
    'request': {
        'search': {
            'order': {
                'request': {
                    'source': {'geopoint': [39.60258, 52.569089]},
                    'surge_price': 1.5,
                },
                'nearest_zone': 'lipetsk',
            },
            'allowed_classes': ['econom'],
        },
        'candidates': [
            {
                'id': 'dbid1_uuid1',
                'route_info': {
                    'time': 1001,
                    'distance': 1,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['econom'],
            },
            {
                'id': 'dbid3_uuid3',
                'route_info': {
                    'time': 500,
                    'distance': 1,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['econom'],
                'metadata': {'reposition_check_required': True},
            },
            {
                'id': 'dbid0_uuid0',
                'route_info': {
                    'time': 1000,
                    'distance': 1,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['econom'],
            },
            {
                'id': 'dbid2_uuid2',
                'route_info': {
                    'time': 600,
                    'distance': 1,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['econom'],
                'metadata': {'reposition_check_required': True},
            },
            {  # penalty: 0
                'id': 'dbid4_uuid4',
                'route_info': {
                    'time': 500,
                    'distance': 3200,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['econom'],
                'metadata': {'reposition_check_required': True},
            },
        ],
    },
    'intent': 'dispatch-buffer',
}

BODY_2 = {
    'request': {
        'search': {
            'order': {
                'request': {
                    'source': {'geopoint': [39.60258, 52.569089]},
                    'surge_price': 1.5,
                },
                'nearest_zone': 'moscow',
            },
            'allowed_classes': ['business'],
        },
        'candidates': [
            {
                'id': 'dbid1_uuid1',
                'route_info': {
                    'time': 1001,
                    'distance': 1,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['business'],
            },
            {
                'id': 'dbid3_uuid3',
                'route_info': {
                    'time': 500,
                    'distance': 1,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['business'],
                'metadata': {'reposition_check_required': True},
            },
        ],
    },
    'intent': 'dispatch-buffer',
}

BODY_3 = {
    'request': {
        'search': {
            'order': {
                'request': {
                    'source': {'geopoint': [39.60258, 52.569089]},
                    'surge_price': 1.5,
                },
                'nearest_zone': 'spb',
            },
            'allowed_classes': ['uberstart'],
        },
        'candidates': [
            {
                'id': 'dbid1_uuid1',
                'route_info': {
                    'time': 1001,
                    'distance': 1,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['uberstart'],
            },
            {
                'id': 'dbid3_uuid3',
                'route_info': {
                    'time': 500,
                    'distance': 1,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['uberstart'],
                'metadata': {'reposition_check_required': True},
            },
        ],
    },
    'intent': 'dispatch-buffer',
}

BODY_4 = {
    'request': {
        'search': {
            'order': {
                'request': {
                    'source': {'geopoint': [39.60258, 52.569089]},
                    'surge_price': 1.5,
                },
                'nearest_zone': 'spb',
            },
            'allowed_classes': ['business'],
        },
        'candidates': [
            {
                'id': 'dbid1_uuid1',
                'route_info': {
                    'time': 1001,
                    'distance': 1,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['business'],
            },
            {
                'id': 'dbid3_uuid3',
                'route_info': {
                    'time': 500,
                    'distance': 1,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['business'],
                'metadata': {'reposition_check_required': True},
            },
        ],
    },
    'intent': 'dispatch-buffer',
}

HEADER = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='exp3_metrics.json')
@pytest.mark.config(
    ROUTER_EXPERIMENTS_BY_INTENT={},
    METRIX_AGGREGATION=[
        {
            'rule': {'and': [{'none_of': []}]},
            'value': [
                {
                    'rule_type': 'whitelist',
                    'label_name': 'tariff_zone',
                    'values': ['moscow', 'lipetsk'],
                    'use_others': True,
                },
                {
                    'rule_type': 'grouping',
                    'label_name': 'tariff_class',
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
        {
            'rule': {'any_of': ['tariff_zone:moscow']},
            'value': [
                {
                    'rule_type': 'whitelist',
                    'label_name': 'tariff_class',
                    'values': ['business'],
                    'use_others': False,
                },
            ],
        },
    ],
)
async def test_metrics(
        taxi_driver_scoring,
        taxi_driver_scoring_monitor,
        mocked_time,
        load_json,
):
    await taxi_driver_scoring.post(
        'v2/score-candidates', headers=HEADER, json=BODY_1,
    )

    await taxi_driver_scoring.post(
        'v2/score-candidates', headers=HEADER, json=BODY_2,
    )

    await taxi_driver_scoring.post(
        'v2/score-candidates', headers=HEADER, json=BODY_3,
    )

    await taxi_driver_scoring.post(
        'v2/score-candidates', headers=HEADER, json=BODY_4,
    )

    mocked_time.set(mocked_time.now() + datetime.timedelta(seconds=15))
    await taxi_driver_scoring.tests_control(invalidate_caches=False)

    metrics = await taxi_driver_scoring_monitor.get_metric(
        'driver_scoring_metrics',
    )

    assert metrics == load_json('metrics.json')
