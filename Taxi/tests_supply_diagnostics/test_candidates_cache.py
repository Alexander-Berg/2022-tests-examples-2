# -*- coding: utf-8 -*-
import pytest


@pytest.mark.config(
    SUPPLY_DIAGNOSTICS_DRIVERS_CACHE_SETTINGS={
        'enabled': True,
        'request_threads': 1,
        'sleep_after_request': 0,
        'cache_source': 'tracker',
    },
)
async def test_candidates_cache(
        taxi_supply_diagnostics, mockserver, testpoint,
):
    @mockserver.json_handler('/candidates/list-profiles')
    def _mock_candidates(request):
        return {
            'drivers': [
                {
                    'position': [37.843392, 55.770121],
                    'id': 'dbid1_uuid1',
                    'dbid': 'dbid1',
                    'uuid': 'uuid1',
                    'payment_methods': ['cash', 'card', 'corp', 'coupon'],
                    'status': {
                        'status': 'online',
                        'orders': [],
                        'driver': 'free',
                        'taximeter': 'free',
                    },
                    'classes': ['selfdriving', 'econom'],
                },
                {
                    'position': [37.737435, 55.827474],
                    'id': 'dbid2_uuid2',
                    'dbid': 'dbid2',
                    'uuid': 'uuid2',
                    'payment_methods': ['cash', 'card', 'corp', 'coupon'],
                    'status': {
                        'status': 'online',
                        'orders': [],
                        'driver': 'free',
                        'taximeter': 'free',
                    },
                    'classes': [
                        'business',
                        'vip',
                        'uberblack',
                        'uberlux',
                        'maybach',
                        'personal_driver',
                    ],
                },
            ],
        }

    @testpoint('driver-profiles-cache')
    def _drivers_cache(data):
        assert data == {
            'drivers_count': 2,
            'driver_ids': ['dbid1_uuid1', 'dbid2_uuid2'],
        }
        return {}

    await taxi_supply_diagnostics.invalidate_caches()
    assert _drivers_cache.times_called == 1
