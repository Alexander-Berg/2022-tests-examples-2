RESULT_ORDERS = [
    # 0
    {
        'id': 'order0',
        'short_id': 1,
        'status': 'complete',
        'created_at': '2019-05-01T07:00:00+00:00',
        'ended_at': '2019-05-01T07:20:00+00:00',
        'driver_profile': {'id': 'driver1', 'name': 'driver_name_1'},
        'car': {
            'id': 'car_id_0',
            'brand_model': 'car_model_0',
            'license': {'number': 'car_number_0'},
            'callsign': 'callsign_0',
        },
        'booked_at': '2019-05-01T07:05:00+00:00',
        'provider': 'partner',
        'address_from': {
            'address': 'Москва, Рядом с: улица Островитянова, 47',
            'lat': 55.6348324304,
            'lon': 37.541191945,
        },
        'route_points': [
            {
                'address': 'Россия, Химки, Нагорная улица',
                'lat': 55.123,
                'lon': 37.1,
            },
            {'address': 'Москва, Улица 1', 'lat': 55.5111, 'lon': 37.222},
            {
                'address': 'Москва, Гостиница Прибалтийская',
                'lat': 55.5545,
                'lon': 37.8989,
            },
        ],
        'cancellation_description': 'canceled',
        'mileage': '1500.0000',
        'type': {'id': 'request_type_0', 'name': 'request_type_name'},
        'category': 'vip',
        'amenities': ['animal_transport'],
        'payment_method': 'corp',
        'driver_work_rule': {
            'id': 'work_rule_id_1',
            'name': 'work_rule_name_1',
        },
        'price': '159.9991',
        'park_details': {
            'passenger': {
                'name': 'client_id_0',
                'phones': ['phone1', 'phone2', 'phone3'],
            },
            'company': {
                'id': 'company_id_0',
                'name': 'company_name_0',
                'slip': 'company_slip_0',
                'comment': 'company_comment_0',
            },
            'tariff': {'id': 'tariff_id_0', 'name': 'tariff_name_0'},
        },
        'events': [
            {
                'order_status': 'driving',
                'event_at': '2019-05-01T07:10:00+00:00',
            },
            {
                'order_status': 'waiting',
                'event_at': '2019-05-01T07:15:00+00:00',
            },
            {
                'order_status': 'calling',
                'event_at': '2019-05-01T07:16:00+00:00',
            },
            {
                'order_status': 'transporting',
                'event_at': '2019-05-01T07:17:00+00:00',
            },
            {
                'order_status': 'complete',
                'event_at': '2019-05-01T07:20:00+00:00',
            },
        ],
    },
    # 1
    {
        'id': 'order1',
        'short_id': 1,
        'status': 'complete',
        'created_at': '2020-05-01T13:18:00+00:00',
        'ended_at': '2020-05-01T14:30:00+00:00',
        'driver_profile': {'id': 'driver2', 'name': 'driver_name_2'},
        'booked_at': '2020-05-01T13:20:00+00:00',
        'provider': 'none',
        'address_from': {
            'address': 'Вильнюсская улица, 7к2',
            'lat': 55.6022246645,
            'lon': 37.5224489641,
        },
        'route_points': [],
        'amenities': [],
        'payment_method': 'cash',
        'events': [
            {
                'order_status': 'driving',
                'event_at': '2019-05-01T13:18:00+00:00',
            },
            {
                'order_status': 'complete',
                'event_at': '2019-05-01T14:30:00+00:00',
            },
        ],
    },
    # 2
    {
        'id': 'order2',
        'short_id': 2,
        'status': 'complete',
        'created_at': '2019-05-01T09:18:00+00:00',
        'ended_at': '2019-05-01T14:18:00+00:00',
        'driver_profile': {'id': 'driver3', 'name': 'driver_name_3'},
        'car': {
            'id': 'car_id_2',
            'brand_model': '',
            'license': {'number': ''},
        },
        'booked_at': '2021-05-01T09:18:00+00:00',
        'provider': 'none',
        'address_from': {
            'address': 'Москва, Рядом с: улица Островитянова, 47',
            'lat': 55.6348324304,
            'lon': 37.541191945,
        },
        'route_points': [],
        'mileage': '0.9939',
        'amenities': [],
        'payment_method': 'cash',
        'price': '157.0000',
        'driver_work_rule': {
            'id': 'work_rule_id_1',
            'name': 'work_rule_name_1',
        },
        'events': [
            {
                'order_status': 'complete',
                'event_at': '2019-05-01T14:18:00+00:00',
            },
        ],
    },
    # 3
    {
        'id': 'order3',
        'short_id': 3,
        'status': 'complete',
        'created_at': '2019-05-01T09:18:00+00:00',
        'ended_at': '2019-05-01T14:20:00+00:00',
        'driver_profile': {'id': 'driver_id_3', 'name': 'driver_name_3'},
        'car': {
            'id': 'car_id_3',
            'brand_model': 'car_name_3',
            'license': {'number': 'car_number_3'},
            'callsign': 'callsign_3',
        },
        'booked_at': '2019-05-01T09:18:00+00:00',
        'provider': 'none',
        'address_from': {
            'address': 'Abc',
            'lat': 55.6022246645,
            'lon': 37.5224489641,
        },
        'route_points': [],
        'amenities': [],
        'payment_method': 'cash',
        'events': [
            {
                'order_status': 'driving',
                'event_at': '2019-05-01T09:18:00+00:00',
            },
            {
                'order_status': 'complete',
                'event_at': '2019-05-01T14:20:00+00:00',
            },
        ],
    },
    # 4
    {
        'id': 'order4',
        'short_id': 4,
        'status': 'expired',
        'created_at': '2019-05-01T17:00:00+00:00',
        'ended_at': '2019-05-01T18:00:00+00:00',
        'booked_at': '2019-05-01T17:30:00+00:00',
        'provider': 'platform',
        'address_from': {
            'address': 'Abc4',
            'lat': 55.6022246645,
            'lon': 37.5224489641,
        },
        'route_points': [],
        'category': 'comfort',
        'amenities': [],
        'payment_method': 'cash',
        'price': '160.0500',
        'events': [
            {
                'order_status': 'expired',
                'event_at': '2019-05-01T18:00:00+00:00',
            },
        ],
    },
    # 5
    {
        'id': 'order5',
        'short_id': 5,
        'status': 'cancelled',
        'created_at': '2019-05-01T19:00:00+00:00',
        'ended_at': '2019-05-01T20:00:00+00:00',
        'booked_at': '2019-05-01T19:30:00+00:00',
        'provider': 'partner',
        'address_from': {
            'address': 'Abc5',
            'lat': 55.6022246645,
            'lon': 37.5224489641,
        },
        'route_points': [],
        'category': 'vip',
        'amenities': [],
        'payment_method': 'corp',
        'price': '140.5000',
        'events': [
            {
                'order_status': 'cancelled',
                'event_at': '2019-05-01T20:00:00+00:00',
            },
        ],
    },
    # 6
    {
        'id': 'order6',
        'short_id': 6,
        'status': 'driving',
        'created_at': '2019-05-01T19:00:00+00:00',
        'booked_at': '2019-05-01T19:30:00+00:00',
        'provider': 'platform',
        'address_from': {
            'address': 'Abc6',
            'lat': 55.6022246645,
            'lon': 37.5224489641,
        },
        'route_points': [],
        'amenities': [],
        'events': [
            {
                'order_status': 'driving',
                'event_at': '2019-05-01T19:30:00+00:00',
            },
        ],
    },
    # 7
    {
        'id': 'order8',
        'short_id': 1,
        'status': 'complete',
        'created_at': '2016-05-01T13:18:00+00:00',
        'ended_at': '2016-05-01T14:30:00+00:00',
        'driver_profile': {'id': 'driver3', 'name': 'driver_name_3'},
        'booked_at': '2016-05-01T13:20:00+00:00',
        'provider': 'none',
        'address_from': {
            'address': 'Вильнюсская улица, 7к2',
            'lat': 55.6022246645,
            'lon': 37.5224489641,
        },
        'route_points': [],
        'amenities': [],
        'payment_method': 'cash',
        'events': [
            {
                'order_status': 'driving',
                'event_at': '2019-05-01T13:18:00+00:00',
            },
            {
                'order_status': 'complete',
                'event_at': '2019-05-01T14:30:00+00:00',
            },
        ],
    },
    # 8
    {
        'id': 'order9',
        'short_id': 1,
        'status': 'complete',
        'created_at': '2020-05-01T13:18:00+00:00',
        'ended_at': '2020-05-01T14:30:00+00:00',
        'driver_profile': {'id': 'driver3', 'name': 'driver_name_3'},
        'booked_at': '2020-05-01T13:20:00+00:00',
        'provider': 'none',
        'address_from': {
            'address': 'Вильнюсская улица, 7к2',
            'lat': 55.6022246645,
            'lon': 37.5224489641,
        },
        'route_points': [],
        'amenities': [],
        'payment_method': 'cash',
        'events': [
            {
                'order_status': 'driving',
                'event_at': '2019-05-01T13:18:00+00:00',
            },
            {
                'order_status': 'complete',
                'event_at': '2019-05-01T14:30:00+00:00',
            },
        ],
    },
    # 9
    {
        'id': 'order10',
        'short_id': 1,
        'status': 'complete',
        'created_at': '2021-05-01T13:18:00+00:00',
        'ended_at': '2021-05-01T14:30:00+00:00',
        'driver_profile': {'id': 'driver4', 'name': 'driver_name_4'},
        'booked_at': '2021-05-01T13:20:00+00:00',
        'provider': 'none',
        'address_from': {
            'address': 'Вильнюсская улица, 7к2',
            'lat': 55.6022246645,
            'lon': 37.5224489641,
        },
        'route_points': [],
        'amenities': [],
        'payment_method': 'cash',
        'events': [
            {
                'order_status': 'driving',
                'event_at': '2019-05-01T13:18:00+00:00',
            },
            {
                'order_status': 'complete',
                'event_at': '2019-05-01T14:30:00+00:00',
            },
        ],
    },
]


def make_park(
        park_id='park1',
        clid='clid1',
        is_active=True,
        driver_partner_source='self_assign',
        fleet_type='uberdriver',
):
    return {
        'id': park_id,
        'city_id': 'city1',
        'country_id': 'rus',
        'driver_partner_source': driver_partner_source,
        'fleet_type': fleet_type,
        'is_active': is_active,
        'is_billing_enabled': False,
        'is_franchising_enabled': True,
        'demo_mode': False,
        'locale': 'locale4',
        'login': 'login4',
        'name': 'name4',
        'provider_config': {
            'apikey': 'apikey1',
            'clid': clid,
            'type': 'production',
        },
        'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
    }


NICE_PARK = make_park()
