import pytest

# flake8: noqa
# pylint: disable=import-error,wildcard-import
from eta_autoreorder_plugins.generated_tests import *


@pytest.mark.pgsql('eta_autoreorder', files=['default_orders.sql'])
async def test_orders_cache(taxi_eta_autoreorder):
    await taxi_eta_autoreorder.invalidate_caches()
    response = await taxi_eta_autoreorder.get('internal/orders')
    assert response.status_code == 200
    assert sorted(response.json(), key=lambda x: x['id']) == [
        {
            'id': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'zone_id': 'moscow',
            'tariff_class': 'vip',
            'performer_dbid_uuid': (
                '00000000000000000000000000000000'
                '_11111111111111111111111111111111'
            ),
            'performer_assigned': '2020-01-01T12:00:00+00:00',
            'performer_initial_eta': 300,
            'performer_initial_distance': 5000,
            'first_performer_assigned': '2020-01-01T12:00:00+00:00',
            'first_performer_initial_eta': 300,
            'first_performer_initial_distance': 5000,
            'eta_autoreorders_count': 0,
            'autoreorder_in_progress': False,
            'reorder_situation_detected': False,
            'last_event_handled': '2020-01-01T12:01:00+00:00',
            'last_event': 'handle_driving',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'point_a': [20.123123, 30.123123],
            'destinations': [],
            'requirements': '{}',
        },
        {
            'id': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
            'zone_id': 'spb',
            'tariff_class': 'business',
            'performer_dbid_uuid': (
                '22222222222222222222222222222222'
                '_33333333333333333333333333333333'
            ),
            'performer_assigned': '2020-01-01T12:02:00+00:00',
            'performer_initial_eta': 360,
            'performer_initial_distance': 6000,
            'first_performer_assigned': '2020-01-01T12:00:00+00:00',
            'first_performer_initial_eta': 300,
            'first_performer_initial_distance': 5000,
            'eta_autoreorders_count': 1,
            'autoreorder_in_progress': False,
            'reorder_situation_detected': False,
            'last_event_handled': '2020-01-01T12:02:00+00:00',
            'last_event': 'handle_driving',
            'user_phone_id': '6141a81573872fb3b53037ed',
            'point_a': [20.123123, 30.123123],
            'destinations': [],
            'requirements': '{}',
        },
    ]
