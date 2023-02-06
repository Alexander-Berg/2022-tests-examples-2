# -*- coding: utf-8 -*-
import json

import pytest


@pytest.mark.now('2020-10-12T14:45:15+0300')
async def test_drivers_profiles_dumper(
        taxi_supply_diagnostics, mds_s3_storage,
):
    await taxi_supply_diagnostics.run_periodic_task('periodic_dumper_drivers')
    assert mds_s3_storage.get_list('drivers-2020-10-12T11:45-11:50')
    data = mds_s3_storage.get_object('/mds-s3/drivers-2020-10-12T11:45-11:50')
    data = data.decode('utf-8')
    data = json.loads(data)
    assert data == {
        'version': '1.0',
        'drivers': [
            {
                'id': 'dbid3_uuid3',
                'driver_uuid': 'uuid3',
                'park_id': 'dbid3',
                'is_econom': True,
                'distance': 0.0,
                'payment_methods': ['card', 'cash'],
                'car_classes': ['business', 'econom'],
                'zone': 'msk',
            },
        ],
        'date': '2020-10-12T11:45',
    }


@pytest.mark.config(
    SUPPLY_DIAGNOSTICS_DRIVERS_CACHE_SETTINGS={
        'enabled': True,
        'request_threads': 1,
        'sleep_after_request': 0,
        'cache_source': 'candidates',
    },
)
@pytest.mark.now('2020-10-12T14:45:15+0300')
async def test_drivers_profiles_dumper_candidates(
        taxi_supply_diagnostics, mds_s3_storage, mockserver,
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
                    'payment_methods': ['cash'],
                    'status': {
                        'status': 'online',
                        'orders': [],
                        'driver': 'free',
                        'taximeter': 'free',
                    },
                    'classes': ['econom'],
                },
                {
                    'position': [37.737435, 55.827474],
                    'id': 'dbid2_uuid2',
                    'dbid': 'dbid2',
                    'uuid': 'uuid2',
                    'payment_methods': ['card'],
                    'status': {
                        'status': 'online',
                        'orders': [],
                        'driver': 'free',
                        'taximeter': 'free',
                    },
                    'classes': ['business'],
                },
            ],
        }

    await taxi_supply_diagnostics.run_periodic_task('periodic_dumper_drivers')
    assert mds_s3_storage.get_list('drivers-2020-10-12T11:45-11:50')
    data = mds_s3_storage.get_object('/mds-s3/drivers-2020-10-12T11:45-11:50')
    data = data.decode('utf-8')
    data = json.loads(data)
    drivers = {driver['id']: driver for driver in data['drivers']}
    assert drivers == {
        'dbid2_uuid2': {
            'id': 'dbid2_uuid2',
            'driver_uuid': 'uuid2',
            'park_id': 'dbid2',
            'is_econom': False,
            'distance': 0.0,
            'payment_methods': ['card'],
            'car_classes': ['business'],
            'zone': 'msk',
        },
        'dbid1_uuid1': {
            'id': 'dbid1_uuid1',
            'driver_uuid': 'uuid1',
            'park_id': 'dbid1',
            'is_econom': True,
            'distance': 0.0,
            'payment_methods': ['cash'],
            'car_classes': ['econom'],
            'zone': 'msk',
        },
    }
