import pytest

DEPOTS = [
    {
        'depot_id': '7e002db38d60487388c98f84512be530000100010001',
        'legacy_depot_id': '10001',
        'country_iso2': 'RU',
        'region_id': 213,
        'position': {'location': {'lon': 1.0, 'lat': 0.0}},
        'address': '123112, Москва, 1-й Красногвардейский проезд, д. 19',
        'phone_number': '+71234567890',
        'email': 'lavka@depot.ru',
        'directions': '3я дверь налево',
        'company_type': 'franchise',
        'detailed_zones': [
            {
                'zoneType': 'pedestrian',
                'status': 'active',
                'timetable': [
                    {
                        'day_type': 'Everyday',
                        'working_hours': {
                            'from': {'hour': 7, 'minute': 30},
                            'to': {'hour': 20, 'minute': 0},
                        },
                    },
                ],
            },
        ],
        'allow_parcels': True,
    },
    {
        'depot_id': '7e002db38d60487388c98f84512be530000100010002',
        'legacy_depot_id': '10002',
        'region_id': 2,
        'timezone': 'Europe/Moscow',
        'position': {'location': {'lon': 1.0, 'lat': 1.0}},
        'address': '195027, Санкт-Петербург, Пискаревский проспект, дом 2',
        'phone_number': '+78007700460',
        'company_type': 'yandex',
        'detailed_zones': [
            {
                'zoneType': 'yandex_taxi',
                'status': 'active',
                'timetable': [
                    {
                        'day_type': 'Everyday',
                        'working_hours': {
                            'from': {'hour': 7, 'minute': 30},
                            'to': {'hour': 20, 'minute': 0},
                        },
                    },
                ],
            },
            {'zoneType': 'pedestrian', 'status': 'disabled'},
        ],
        'allow_parcels': True,
    },
    {
        'depot_id': '7e002db38d60487388c98f84512be530000100010003',
        'legacy_depot_id': '10003',
        'region_id': 47,
        'timezone': 'Europe/Moscow',
        'position': {'location': {'lon': 2.0, 'lat': 2.0}},
        'address': '603005, Нижний Новгород, улица Алексеевская, 10/16',
        'phone_number': '+79876543210',
        'email': 'lavka_123@depot.ru',
        'directions': '3я дверь налево',
        'company_type': 'yandex',
        'detailed_zones': [
            {
                'zoneType': 'pedestrian',
                'status': 'active',
                'timetable': [
                    {
                        'day_type': 'Everyday',
                        'working_hours': {
                            'from': {'hour': 7, 'minute': 30},
                            'to': {'hour': 20, 'minute': 0},
                        },
                    },
                ],
            },
            {
                'zoneType': 'pedestrian',
                'status': 'active',
                'timetable': [
                    {
                        'day_type': 'Everyday',
                        'working_hours': {
                            'from': {'hour': 7, 'minute': 30},
                            'to': {'hour': 20, 'minute': 0},
                        },
                    },
                ],
            },
            {
                'zoneType': 'pedestrian',
                'status': 'disabled',
                'timetable': [
                    {
                        'day_type': 'Everyday',
                        'working_hours': {
                            'from': {'hour': 7, 'minute': 30},
                            'to': {'hour': 20, 'minute': 0},
                        },
                    },
                ],
            },
            {
                'zoneType': 'yandex_taxi_remote',
                'status': 'disabled',
                'timetable': [
                    {
                        'day_type': 'Everyday',
                        'working_hours': {
                            'from': {'hour': 7, 'minute': 30},
                            'to': {'hour': 20, 'minute': 0},
                        },
                    },
                ],
            },
        ],
        'allow_parcels': True,
    },
    {
        'depot_id': '7e002db38d60487388c98f84512be530000100010004',
        'legacy_depot_id': '10004',
        'country_iso3': 'RUS',
        'country_iso2': 'RU',
        'region_id': 213,
        'timezone': 'Europe/Moscow',
        'position': {'location': {'lon': 3.0, 'lat': 3.0}},
        'phone_number': '+78007700460',
        'currency': 'RUB',
        'company_type': 'yandex',
        'detailed_zones': [
            {
                'zoneType': 'yandex_taxi_night',
                'status': 'active',
                'timetable': [
                    {
                        'day_type': 'Everyday',
                        'working_hours': {
                            'from': {'hour': 7, 'minute': 30},
                            'to': {'hour': 20, 'minute': 0},
                        },
                    },
                ],
            },
        ],
        'allow_parcels': True,
    },
    {
        'depot_id': '7e002db38d60487388c98f84512be530000100010005',
        'legacy_depot_id': '10005',
        'region_id': 67,
        'position': {'location': {'lon': 4.0, 'lat': 4.0}},
        'phone_number': '+78007700460',
        'currency': 'RUB',
        'company_type': 'yandex',
        'detailed_zones': [
            {
                'zoneType': 'rover',
                'status': 'active',
                'timetable': [
                    {
                        'day_type': 'Everyday',
                        'working_hours': {
                            'from': {'hour': 7, 'minute': 30},
                            'to': {'hour': 20, 'minute': 0},
                        },
                    },
                ],
            },
        ],
        'allow_parcels': True,
    },
    {
        'depot_id': '7e002db38d60487388c98f84512be530000100010007',
        'legacy_depot_id': '10007',
        'region_id': 2,
        'timezone': 'Asia/Novosibirsk',
        'position': {'location': {'lon': 1.0, 'lat': 1.0}},
        'address': '195027, Новосибирск, Проспект Ленина, дом 2',
        'phone_number': '+78007700460',
        'company_type': 'yandex',
        'detailed_zones': [
            {
                'zoneType': 'pedestrian',
                'status': 'active',
                'timetable': [
                    {
                        'day_type': 'Everyday',
                        'working_hours': {
                            'from': {'hour': 7, 'minute': 30},
                            'to': {'hour': 20, 'minute': 0},
                        },
                    },
                ],
            },
        ],
        'allow_parcels': True,
    },
    {
        'depot_id': 'keep-it-last',
        'legacy_depot_id': '10006',
        'region_id': 67,
        'position': {'location': {'lon': 4.0, 'lat': 4.0}},
        'phone_number': '+78007700460',
        'currency': 'RUB',
        'company_type': 'yandex',
        'detailed_zones': [
            {
                'zoneType': 'rover',
                'status': 'active',
                'timetable': [
                    {
                        'day_type': 'Everyday',
                        'working_hours': {
                            'from': {'hour': 7, 'minute': 30},
                            'to': {'hour': 20, 'minute': 0},
                        },
                    },
                ],
            },
        ],
        'allow_parcels': False,
    },
]


@pytest.mark.config(
    TRISTERO_B2B_MEASUREMENTS_LIMITS={
        'height': 100,
        'length': 200,
        'weight': 400,
        'width': 300,
    },
)
@pytest.mark.config(
    TRISTERO_B2B_INTEGRATIONS_BY_REGION_ID={
        '__default__': ['lavka', 'lavket'],
        '2': ['lavket'],
        '47': ['lavka'],
    },
)
async def test_depots(taxi_tristero_b2b, grocery_depots):

    for i, depot in enumerate(DEPOTS):
        mock_depot = grocery_depots.add_depot(
            i + 1,
            depot_id=depot.get('depot_id'),
            legacy_depot_id=depot.get('legacy_depot_id'),
            region_id=depot.get('region_id'),
            location=depot['position']['location']
            if depot.get('position')
            else None,
            address=depot.get('address'),
            phone_number=depot.get('phone_number'),
            email=depot.get('email'),
            directions=depot.get('directions'),
            allow_parcels=depot.get('allow_parcels'),
            company_type=depot.get('company_type'),
            auto_add_zone=False,
            timezone=depot.get('timezone', 'Europe/Moscow'),
        )
        for zone in depot.get('detailed_zones'):
            mock_depot.add_zone(
                status=zone.get('status'),
                delivery_type=zone.get('zoneType'),
                timetable=zone.get('timetable'),
            )

    response = await taxi_tristero_b2b.post('/tristero/v1/depots', json={})
    assert response.status == 200
    response_data = response.json()

    assert len(response_data['depots']) == len(DEPOTS) - 1

    for response_depot, depot in zip(response_data['depots'], DEPOTS):
        assert response_depot['depot_id'] == depot['depot_id']
        assert (
            response_depot['position']['location'][0]
            == depot['position']['location']['lon']
        )
        assert (
            response_depot['position']['location'][1]
            == depot['position']['location']['lat']
        )
        assert response_depot.get('address', '') == depot.get('address', '')
        assert response_depot['phone_number'] == depot['phone_number']
        assert response_depot.get('email') == depot.get('email')
        assert response_depot.get('directions') == depot.get('directions')
        expected_zones = [
            zone
            for zone in depot['detailed_zones']
            if zone['zoneType'] == 'pedestrian'
            and 'status' in zone
            and zone['status'] == 'active'
        ]
        if response_depot['detailed_zones']:
            for i, zone in enumerate(expected_zones):
                assert response_depot['detailed_zones'][i] == zone
        else:
            assert expected_zones == []
        assert response_depot['measurements_limits'] == {
            'height': 100,
            'length': 200,
            'weight': 400,
            'width': 300,
        }
        if depot['region_id'] == 2:
            assert response_depot['integrations'] == ['lavket']
        elif depot['region_id'] == 47:
            assert response_depot['integrations'] == ['lavka']
        else:
            assert response_depot['integrations'] == ['lavka', 'lavket']
        if 'timezone' in depot and depot['timezone'] == 'Asia/Novosibirsk':
            assert response_depot['timezone'] == '+0700'
        else:
            assert response_depot['timezone'] == '+0300'
