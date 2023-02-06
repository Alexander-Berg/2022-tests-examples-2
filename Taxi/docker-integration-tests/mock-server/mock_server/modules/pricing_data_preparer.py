from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/v2/prepare', self.v2_prepare)
        self.router.add_post('/v2/recalc_order', self.v2_recalc_order)

    @staticmethod
    async def v2_prepare(request):
        data = await request.json()
        categories = data['categories']
        response = {}
        price = 129
        surge = 1
        if len(data['waypoints']) > 1:
            if data['waypoints'][1][0] == 37.900479:
                price = 929
            if data['waypoints'][0][0] == 37.581740:
                surge = 1.5

        for category in categories:
            response[category] = {
                'corp_decoupling': False,
                'currency': {
                    'fraction_digits': 0,
                    'name': 'RUB',
                    'symbol': '₽',
                },
                'driver': {
                    'additional_prices': {},
                    'base_price': {
                        'boarding': 129.0,
                        'destination_waiting': 0.0,
                        'distance': 0.0,
                        'requirements': 0.0,
                        'time': 0.0,
                        'transit_waiting': 0.0,
                        'waiting': 0.0,
                    },
                    'category_id': 'ed3b2fe5c51f4a4da7bee86349259dda',
                    'category_prices_id': 'c/ed3b2fe5c51f4a4da7bee86349259dda',
                    'meta': {
                        'synthetic_surge': surge,
                    },
                    'modifications': {'for_taximeter': []},
                    'price': {'total': price},
                    'tariff_id': '5d1f30c70c69ffa8ba0170c7',
                },
                'fixed_price': len(data['waypoints']) > 1,
                'geoarea_ids': ['g/1f121111472a45e9bcbb7c72200c6340'],
                'tariff_info': {
                    'distance': {
                        'included_kilometers': 3,
                        'price_per_kilometer': 10.0,
                    },
                    'max_free_waiting_time': 600,
                    'point_a_free_waiting_time': 180,
                    'time': {'included_minutes': 5, 'price_per_minute': 9.0},
                },
                'taximeter_metadata': {
                    'max_distance_from_point_b': 500,
                    'show_price_in_taximeter': False,
                },
                'user': {
                    'additional_prices': {},
                    'base_price': {
                        'boarding': 129.0,
                        'destination_waiting': 0.0,
                        'distance': 0.0,
                        'requirements': 0.0,
                        'time': 0.0,
                        'transit_waiting': 0.0,
                        'waiting': 0.0,
                    },
                    'category_id': 'ed3b2fe5c51f4a4da7bee86349259dda',
                    'category_prices_id': 'c/ed3b2fe5c51f4a4da7bee86349259dda',
                    'data': {
                        'category': category,
                        'category_data': {
                            'corp_decoupling': False,
                            'decoupling': False,
                            'fixed_price': len(data['waypoints']) > 1,
                            'min_paid_supply_price_for_paid_cancel': 0.0,
                            'paid_cancel_waiting_time_limit': 600.0,
                        },
                        'country_code2': 'RU',
                        'requirements': {'select': {}, 'simple': []},
                        'rounding_factor': 1.0,
                        'surge_params': {
                            'antisurge': False,
                            'value': surge,
                            'value_raw': surge,
                            'value_smooth': surge,
                        },
                        'tariff': {
                            'boarding_price': 129.0,
                            'minimum_price': 0.0,
                            'requirement_prices': {},
                            'waiting_price': {
                                'free_waiting_time': 180,
                                'price_per_minute': 9.0,
                            },
                        },
                        'user_data': {
                            'has_cashback_plus': False,
                            'has_yaplus': False,
                        },
                        'user_tags': [],
                        'zone': 'moscow',
                    },
                    'meta': {
                        'synthetic_surge': surge,
                    },
                    'modifications': {'for_taximeter': []},
                    'price': {'total': price},
                    'tariff_id': '5d1f30c70c69ffa8ba0170c7',
                    'trip_information': {
                        'distance': 3200,
                        'time': 120,
                        'jams': True,
                        'has_toll_roads': False,
                    },
                },
            }
        return web.json_response({'categories': response})

    @staticmethod
    async def v2_recalc_order(request):
        response_data = {
            'price': {
                'driver': {
                    'meta': {'paid_cancel_in_waiting_price': 1.0},
                    'total': 1.0,
                },
                'user': {
                    'meta': {'paid_cancel_in_waiting_price': 1.0},
                    'total': 1.0,
                },
            },
        }
        return web.json_response(response_data)
