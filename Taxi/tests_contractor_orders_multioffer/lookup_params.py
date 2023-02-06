import uuid


def create_params(**kwargs):
    order_id = uuid.uuid4()
    user_id = uuid.uuid4()
    lookup_params = {
        'order_id': str(order_id),
        'order': {
            '_type': kwargs.get('type', 'soon'),
            'user_id': str(user_id),
            'nearest_zone': 'moscow',
            'svo_car_number': kwargs.get('svo_car_number', None),
            'request': {
                'source': {'geopoint': [1.0, 1.0]},
                'destinations': [{'geopoint': [3.0, 4.0]}],
                'surge_price': kwargs.get('surge_price', 1.0),
                'surge_price_required': kwargs.get(
                    'surge_price_required', None,
                ),
                'passengers_count': 1,
                'luggage_count': kwargs.get('luggage_count', None),
            },
            'feedback': {  # специальные флаги для заказов-проверок
                'mqc': False,
                'mystery_shopper': False,
            },
            'calc': {
                'distance': 10000.01,
                'time': 600.01,
                'alternative_type': '',
            },
            'payment_tech': {'type': 'cash'},
            'fixed_price': {
                'price': 121,  # опционально
                'paid_supply_price': None,  # опционально
            },
        },
        # опциональные параметры фильтрации
        'parameters': {
            'allowed_classes': kwargs.get('tariffs', ['comfort']),
            'excluded_park_ids': kwargs.get('excluded_park_ids', []),
            'excluded_driver_ids': kwargs.get('excluded_driver_ids', []),
            'excluded_licenses': kwargs.get('excluded_licenses', []),
            'excluded_license_ids': kwargs.get('excluded_license_ids', []),
            'excluded_car_numbers': kwargs.get('excluded_car_numbers', []),
            'check_contracts': kwargs.get('check_contracts', False),
            'requirements': {
                'some_requirement': 1,
                'other_requirement': [2],
                'third_requirement': False,
            },
            'max_route_distance': kwargs.get('max_route_distance', None),
            'max_route_time': kwargs.get('max_route_time', None),
        },
    }
    # поколение и версия
    if (
            kwargs.get('generation')
            and kwargs.get('version')
            and kwargs.get('wave')
    ):
        lookup_params['lookup'] = {
            'generation': kwargs.get('generation'),
            'version': kwargs.get('version'),
            'wave': kwargs.get('wave'),
        }
    return lookup_params
