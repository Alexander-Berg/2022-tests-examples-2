# pylint: disable=E1101,W0612
import pytest


@pytest.mark.config(ALL_CATEGORIES=['econom', 'vip'])
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    DISPATCH_AIRPORT_ZONES={
        'moscow': {
            'airport_title_key': 'moscow_airport_key',
            'enabled': True,
            'main_area': 'moscow',
            'distributive_zone_type': 'waiting',
            'group_id': 'countryside',
            'notification_area': 'moscow',
            'old_mode_enabled': False,
            'tariff_home_zone': 'moscow',
            'update_interval_sec': 5,
            'use_queue': True,
            'waiting_area': 'moscow',
            'whitelist_classes': {
                'econom': {'reposition_enabled': False, 'nearest_mins': 60},
            },
        },
        'iceland': {
            'airport_title_key': 'keflavik_airport_key',
            'enabled': True,
            'main_area': 'very_cold_zone',
            'distributive_zone_type': 'distributive',
            'group_id': 'countryside',
            'notification_area': 'iceland',
            'old_mode_enabled': False,
            'tariff_home_zone': 'iceland',
            'update_interval_sec': 5,
            'use_queue': True,
            'waiting_area': 'iceland',
            'whitelist_classes': {
                'econom': {'reposition_enabled': False, 'nearest_mins': 60},
            },
        },
        'underworld': {
            'airport_title_key': 'are_you_kidding_me',
            'enabled': True,
            'main_area': 'hotplace_here',
            'distributive_zone_type': 'waiting',
            'group_id': 'countryside',
            'notification_area': 'underworld',
            'old_mode_enabled': False,
            'tariff_home_zone': 'underworld',
            'update_interval_sec': 5,
            'use_queue': True,
            'waiting_area': 'underworld',
            'whitelist_classes': {
                'econom': {'reposition_enabled': False, 'nearest_mins': 60},
            },
        },
    },
)
async def test(taxi_surge_calculator, mockserver):
    @mockserver.json_handler('/dispatch-airport/v1/active-drivers-queues')
    def _active_drivers_queues(request):
        if request.args.get('airport') == 'underworld':
            return {'queues': []}

        if request.args.get('airport') == 'iceland':
            return {
                'queues': [
                    {
                        'tariff': 'econom',
                        'active_drivers': [
                            {
                                'dbid_uuid': f'dbid{i}_uuid{i}',
                                'queued': f'2019-06-10T14:{i}:20Z',
                            }
                            for i in range(20, 30)
                        ],
                        'driver_needs_predict': 1,
                    },
                ],
            }

        return {
            'queues': [
                {
                    'tariff': 'econom',
                    'active_drivers': [
                        {
                            'dbid_uuid': f'dbid{i}_uuid{i}',
                            'queued': f'2019-06-10T13:0{i}:20Z',
                        }
                        for i in range(8)
                    ],
                    'driver_needs_predict': 9001,
                },
                {
                    'tariff': 'vip',
                    'active_drivers': [
                        {
                            'dbid_uuid': f'dbid1{i}_uuid1{i}',
                            'queued': f'2019-06-10T13:{i}0:20Z',
                        }
                        for i in range(3)
                    ],
                    'driver_needs_predict': 0,
                },
            ],
        }

    request = {'point_a': [38.1, 51], 'classes': ['econom', 'vip']}
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200
    data = response.json()

    actual = dict()
    for category_data in data['classes']:
        drivers = category_data['surge']['value']
        drivers_prediction = category_data['value_raw']
        actual[category_data['name']] = (drivers, drivers_prediction)
    expected = {'econom': (13, 9001), 'vip': (3, 0)}
    assert actual == expected
