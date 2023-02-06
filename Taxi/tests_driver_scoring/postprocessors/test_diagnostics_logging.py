import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


BODY = {
    'requests': [
        {
            'search': {
                'order_id': 'order0',
                'order': {
                    'request': {'source': {'geopoint': [39.60258, 52.569089]}},
                    'nearest_zone': 'lipetsk',
                },
                'allowed_classes': ['child_tariff'],
            },
            'candidates': [
                {
                    'id': 'dbid0_uuid0',
                    'route_info': {
                        'time': 1002,
                        'distance': 1,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['child_tariff'],
                    'metadata': {'reposition_check_required': True},
                },
                {
                    'id': 'dbid1_uuid1',
                    'route_info': {
                        'time': 1001,
                        'distance': 1,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['child_tariff'],
                    'metadata': {'reposition_check_required': True},
                },
            ],
        },
        {
            'search': {
                'order_id': 'order1',
                'order': {
                    'request': {'source': {'geopoint': [39.60258, 52.569089]}},
                    'nearest_zone': 'lipetsk',
                },
                'allowed_classes': ['child_tariff'],
            },
            'candidates': [
                {
                    'id': 'dbid2_uuid2',
                    'route_info': {
                        'time': 1003,
                        'distance': 1,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['child_tariff'],
                    'metadata': {'reposition_check_required': True},
                },
                {
                    'id': 'dbid3_uuid3',
                    'route_info': {
                        'time': 1004,
                        'distance': 1,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['child_tariff'],
                    'metadata': {'reposition_check_required': True},
                },
            ],
        },
    ],
    'intent': 'dispatch-buffer',
}


@pytest.mark.experiments3(filename='filter_by_reposition.json')
@pytest.mark.experiments3(filename='exp3_postprocessors.json')
async def test_log_abandoned_orders(taxi_driver_scoring, testpoint):
    logged = []

    @testpoint('DiagnosticsLogging::impl_call')
    def impl_call(data):
        nonlocal logged
        logged.append(data)

    async with taxi_driver_scoring.capture_logs() as capture:
        response = await taxi_driver_scoring.post(
            'v2/score-candidates-bulk',
            headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
            json=BODY,
        )

    assert response.status_code == 200
    for response in response.json()['responses']:
        assert response['candidates'] == []
    assert impl_call.times_called == 4
    assert logged == [
        {'order_id': 'order0', 'postprocessor': 'diagnostics_default_logging'},
        {'order_id': 'order1', 'postprocessor': 'diagnostics_default_logging'},
        {'order_id': 'order0', 'postprocessor': 'diagnostics_yt_logging'},
        {'order_id': 'order1', 'postprocessor': 'diagnostics_yt_logging'},
    ]

    log_items_count = 0
    for log_item in capture.select():
        if log_item['text'].startswith(
                'All candidates were filtered by driver-scoring, log using',
        ):
            log_items_count += 1
            assert 'meta_order_id' in log_item
            assert log_item['meta_order_id']
    assert log_items_count == 4
