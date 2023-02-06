import uuid


def create_params(**kwargs):
    order_id = uuid.uuid4()
    user_id = uuid.uuid4()
    lookup_params = {
        '_id': str(order_id),
        'order': {
            '_type': kwargs.get('type', 'soon'),
            'user_id': str(user_id),
            'nz': 'moscow',
            'svo_car_number': kwargs.get('svo_car_number', None),
            'request': {
                'source': {'geopoint': [15.0, 15.0]},
                'destinations': [{'geopoint': [3.0, 4.0]}],
                'sp': kwargs.get('surge_price', 1.0),
                'spr': kwargs.get('surge_price_required', None),
                'class': kwargs.get('tariffs', ['econom']),
            },
            'feedback': {  # специальные флаги для заказов-проверок
                'mqc': False,
            },
            'calc': {
                'distance': 10000.01,
                'time': 600.01,
                'alternative_type': '',
            },
            'fixed_price': {
                'price': 121,  # опционально
                'paid_supply_price': None,  # опционально
                'paid_supply_info': {
                    'distance': kwargs.get('max_route_distance', None),
                    'time': kwargs.get('max_route_time', None),
                },
            },
            'user_phone_id': 'phone_id',
            'personal_phone_id': 'personal_phone_id',
            'discount': {
                'by_classes': [
                    {
                        'class': 'express',
                        'description': 'master_yt_ru_delivery_25_05_2020',
                        'driver_less_coeff': 0,
                        'id': '12b64b17-31c2-4bd2-ad60-76651454c147',
                        'is_cashback': False,
                        'limited_rides': False,
                        'max_absolute_value': 3000,
                        'method': 'subvention-fix',
                        'price': 282.1971249547082,
                        'reason': 'for_all',
                        'value': 0.1,
                    },
                    {
                        'class': 'econom',
                        'description': 'test_strikethrough',
                        'driver_less_coeff': 0.5,
                        'id': 'f4adea2d-3a73-4a0b-a6c1-945cae00792e',
                        'is_cashback': False,
                        'is_price_strikethrough': True,
                        'limited_rides': False,
                        'method': 'full',
                        'price': 564.0695475067487,
                        'reason': 'for_all',
                        'value': 0.3,
                    },
                    {
                        'class': 'courier',
                        'description': 'master_yt_ru_delivery_25_05_2020',
                        'driver_less_coeff': 0,
                        'id': '12b64b17-31c2-4bd2-ad60-76651454c147',
                        'is_cashback': False,
                        'limited_rides': False,
                        'max_absolute_value': 3000,
                        'method': 'subvention-fix',
                        'price': 236.8194802985191,
                        'reason': 'for_all',
                        'value': 0.1,
                    },
                    {
                        'class': 'business',
                        'description': 'test_strikethrough',
                        'driver_less_coeff': 0.5,
                        'id': 'f4adea2d-3a73-4a0b-a6c1-945cae00792e',
                        'is_cashback': False,
                        'is_price_strikethrough': True,
                        'limited_rides': False,
                        'method': 'full',
                        'price': 454.4051132397755,
                        'reason': 'for_all',
                        'value': 0.3,
                    },
                ],
            },
        },
        'payment_tech': {'type': 'cash'},
        'active_candidates': [],
        'aliases': [],
        'status': 'pending',
        'lookup': {
            'eta': {'$date': 1618493536187},
            'generation': 1,
            'generation_updated': {'$date': 1618493536187},
            'name': 'direct_assignment',
            'need_start': False,
            'params': {},
            'state': {'wave': 0},
            'version': 1,
        },
    }
    # поколение и версия
    if (
            kwargs.get('generation')
            and kwargs.get('version')
            and kwargs.get('wave')
    ):
        lookup_params['lookup'].update(
            {
                'generation': kwargs.get('generation'),
                'version': kwargs.get('version'),
            },
        )
        lookup_params['lookup']['state']['wave'] = kwargs.get('wave') - 1
    return lookup_params
