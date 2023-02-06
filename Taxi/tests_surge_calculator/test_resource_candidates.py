# pylint: disable=E1101,W0612
import pytest


@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_count_by_categories(
        taxi_surge_calculator,
        taxi_surge_calculator_monitor,
        mockserver,
        mocked_time,
):
    actual_request = None

    @mockserver.json_handler('/candidates/count-by-categories')
    def _count_by_categories(request):
        nonlocal actual_request
        actual_request = request.json

        response = {'radius': 2785, 'generic': {}, 'reposition': {}}

        for category in actual_request.get('allowed_classes', []):
            response['generic'][category] = {
                'free': 12,
                'free_chain': 3,
                'total': 30,
                'free_chain_groups': {'short': 3, 'medium': 3, 'long': 3},
            }

        return mockserver.make_response(
            headers={'X-YaTaxi-Server-Hostname': 'mockserver'}, json=response,
        )

    # valid
    point_a = [38.1, 51]
    request = {'point_a': point_a}
    expected_counts = {
        'pins': 0,
        'radius': 2785,
        'free': 12,
        'free_chain': 3,
        'total': 30,
    }
    expected_request = {
        'allowed_classes': ['econom'],
        'limit': 400,
        'max_distance': 2500,
        'point': point_a,
        'zone_id': 'moscow',  # hardcoded in pipeline
    }
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200
    data = response.json()
    actual_counts = data['classes'][0]['calculation_meta']['counts']

    assert actual_counts == expected_counts
    assert actual_request == expected_request

    await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    metrics = await taxi_surge_calculator_monitor.get_metric(
        'js-pipeline-resource-management',
    )

    assert metrics['resources']['count_by_categories'] == {
        '1min': {
            '$meta': {'solomon_children_labels': 'resource_status'},
            'error': {
                '$meta': {'solomon_children_labels': 'resource_field'},
                'count': 0,
            },
            'success': {
                '$meta': {'solomon_children_labels': 'resource_field'},
                'count': 2,
                'time': {
                    '$meta': {'solomon_children_labels': 'percentile'},
                    'p100': 0,
                    'p50': 0,
                    'p75': 0,
                    'p80': 0,
                    'p85': 0,
                    'p90': 0,
                    'p95': 0,
                    'p98': 0,
                    'p99': 0,
                },
            },
        },
    }

    # Ensure that current counter of the RecentPeriod has updated
    # and statistics from the previous call are already visible
    mocked_time.sleep(61)
    await taxi_surge_calculator.post('/v1/calc-surge', json=request)

    metrics = await taxi_surge_calculator_monitor.get_metric(
        'js-pipeline-resource-management-custom',
    )

    def mask_hostname(json):
        res = {}
        for i, (key, value) in enumerate(json.items()):
            if key == '$meta':
                res[key] = value
            else:
                res[f'__hostname_{i}__'] = value
        return res

    assert mask_hostname(metrics['resources']['count_by_categories']) == {
        '$meta': {'solomon_children_labels': 'source_host'},
        '__hostname_0__': {
            '$meta': {'solomon_children_labels': 'zone'},
            'moscow': {
                '$meta': {'solomon_children_labels': 'tariff'},
                'econom': {
                    '$meta': {'solomon_children_labels': 'duration'},
                    '1min': {
                        'free': 24,
                        'free_chain': 6,
                        'free_chain_groups': {
                            'long': 6,
                            'medium': 6,
                            'short': 6,
                        },
                        'free_share': 0.4,
                        'on_order': 0,
                        'total': 60,
                    },
                    '5min': {
                        'free': 24,
                        'free_chain': 6,
                        'free_chain_groups': {
                            'long': 6,
                            'medium': 6,
                            'short': 6,
                        },
                        'free_share': 0.4,
                        'on_order': 0,
                        'total': 60,
                    },
                    '15min': {
                        'free': 24,
                        'free_chain': 6,
                        'free_chain_groups': {
                            'long': 6,
                            'medium': 6,
                            'short': 6,
                        },
                        'free_share': 0.4,
                        'on_order': 0,
                        'total': 60,
                    },
                    '60min': {
                        'free': 24,
                        'free_chain': 6,
                        'free_chain_groups': {
                            'long': 6,
                            'medium': 6,
                            'short': 6,
                        },
                        'free_share': 0.4,
                        'on_order': 0,
                        'total': 60,
                    },
                },
            },
        },
    }


@pytest.mark.config(ALL_CATEGORIES=['econom'])
async def test_absent_counts(taxi_surge_calculator, mockserver):
    @mockserver.json_handler('/candidates/count-by-categories')
    def _count_by_categories(request):
        return mockserver.make_response(
            headers={'X-YaTaxi-Server-Hostname': 'mockserver'},
            json={'radius': 2785, 'generic': {}, 'reposition': {}},
        )

    request = {'point_a': [38.1, 51]}
    expected_counts = {
        'pins': 0,
        'radius': 2785,
        'free': 0,
        'free_chain': 0,
        'total': 0,
    }
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200
    data = response.json()
    actual_counts = data['classes'][0]['calculation_meta']['counts']

    assert actual_counts == expected_counts
