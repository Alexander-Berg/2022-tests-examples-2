from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            '/v1/save_order_details', self.v1_save_order_details,
        )

    @staticmethod
    async def v1_save_order_details(request):
        data = await request.json()
        driver_total_price = (
            data.get('ride', {}).get('driver', {}).get('rounded_price')
        )
        user_total_price = (
            data.get('ride', {}).get('user', {}).get('rounded_price')
        )

        response = {
            'price': {
                'user': {
                    'total': user_total_price,
                    'meta': {
                        'waiting_price': 0.0,
                        'waiting_in_destination_price': 0.0,
                        'paid_cancel_price': 129.0,
                        'max_surge_delta_raw': 80.00000000000001,
                        'detail.time': 29.5,
                        'min_price': 149.0,
                        'price_after_surge': 181.52658108711245,
                        'detail.distance': 23.026581087112437,
                        'paid_cancel_in_waiting_price': 69.0,
                        'detail.waiting': 0.0,
                        'gepard_paid_waiting_minutes': 0.0,
                        'setcar.show_surcharge': 80.0,
                        'paid_cancel_in_waiting_paid_time': 0.0,
                        'waiting_in_transit_price': 0.0,
                        'paid_supply_price': 20.0,
                        'gepard_waiting_price_raw': 0.0,
                        'gepard_min_price_raw': 49.0,
                        'detail.boarding': 49.0,
                        'gepard_waiting_in_transit_price_raw': 0.0,
                        'gepard_waiting_in_destination_price_raw': 0.0,
                        'gepard_free_waiting_minutes': 3.0,
                        'gepard_toll_road_payment_price': 0.0,
                        'gepard_base_price_raw': 101.52658108711243,
                        'surge_delta': 80.0,
                        'surge_delta_raw': 80.00000000000001,
                        'synthetic_surge': 1.787970983986528,
                    },
                    'additional_payloads': {
                        'details': {
                            'requirements': [
                                {
                                    'name': 'waiting',
                                    'text': {
                                        'tanker_key': 'service_name.waiting',
                                        'keyset': 'tariff',
                                    },
                                    'price': {'total': 0.0, 'per_unit': 0.0},
                                    'count': 0,
                                    'included': 0,
                                },
                                {
                                    'name': 'waiting_in_destination',
                                    'text': {
                                        'tanker_key': 'some_key',
                                        'keyset': 'tariff',
                                    },
                                    'price': {'total': 0.0, 'per_unit': 0.0},
                                    'count': 0,
                                    'included': 0,
                                },
                                {
                                    'name': 'waiting_in_transit',
                                    'text': {
                                        'tanker_key': (
                                            'service_name.waiting_in_transit'
                                        ),
                                        'keyset': 'tariff',
                                    },
                                    'price': {'total': 0.0, 'per_unit': 0.0},
                                    'count': 0,
                                    'included': 0,
                                },
                            ],
                            'services': [
                                {
                                    'name': 'gepard_min_price_raw',
                                    'text': {
                                        'tanker_key': 'gepard_min_price_raw',
                                        'keyset': 'taximeter_driver_messages',
                                    },
                                    'price': 49.0,
                                },
                                {
                                    'name': 'gepard_waiting_price_raw',
                                    'text': {
                                        'tanker_key': (
                                            'gepard_waiting_price_raw'
                                        ),
                                        'keyset': 'taximeter_driver_messages',
                                    },
                                    'price': 0.0,
                                },
                                {
                                    'name': (
                                        'gepard_waiting_in_transit_price_raw'
                                    ),
                                    'text': {
                                        'tanker_key': 'some_key',
                                        'keyset': 'taximeter_driver_messages',
                                    },
                                    'price': 0.0,
                                },
                                {
                                    'name': 'some_name',
                                    'text': {
                                        'tanker_key': 'some_key',
                                        'keyset': 'taximeter_driver_messages',
                                    },
                                    'price': 0.0,
                                },
                                {
                                    'name': 'gepard_base_price_raw',
                                    'text': {
                                        'tanker_key': 'gepard_base_price_raw',
                                        'keyset': 'taximeter_driver_messages',
                                    },
                                    'price': 101.52658108711243,
                                },
                                {
                                    'name': 'surge_delta_raw',
                                    'text': {
                                        'tanker_key': 'surge_delta_raw',
                                        'keyset': 'taximeter_driver_messages',
                                    },
                                    'price': 80.00000000000001,
                                },
                                {
                                    'name': 'gepard_free_waiting_minutes',
                                    'text': {
                                        'tanker_key': (
                                            'gepard_free_waiting_minutes'
                                        ),
                                        'keyset': 'taximeter_driver_messages',
                                    },
                                    'price': 3.0,
                                },
                                {
                                    'name': 'gepard_paid_waiting_minutes',
                                    'text': {
                                        'tanker_key': (
                                            'gepard_paid_waiting_minutes'
                                        ),
                                        'keyset': 'taximeter_driver_messages',
                                    },
                                    'price': 0.0,
                                },
                            ],
                        },
                    },
                    'extra': {'without_surge': 122.0},
                },
                'driver': {
                    'total': driver_total_price,
                    'meta': {
                        'waiting_price': 0.0,
                        'waiting_in_destination_price': 0.0,
                        'detail.time': 29.5,
                        'detail.boarding': 49.0,
                        'increase_to_minimum_price_delta': 0.0,
                        'paid_cancel_in_waiting_price': 69.0,
                        'detail.waiting': 0.0,
                        'setcar.show_surcharge': 80.0,
                        'paid_cancel_in_waiting_paid_time': 0.0,
                        'surge_delta': 80.0,
                        'min_price': 149.0,
                        'detail.distance': 23.026581087112437,
                        'price_after_surge': 181.52658108711245,
                        'synthetic_surge': 1.787970983986528,
                        'surge_delta_raw': 80.00000000000001,
                        'max_surge_delta_raw': 80.00000000000001,
                        'gepard_toll_road_payment_price': 0.0,
                        'increase_to_minimum_price_delta_raw': 0.0,
                        'paid_cancel_price': 129.0,
                        'waiting_in_transit_price': 0.0,
                        'paid_supply_price': 20.0,
                    },
                    'additional_payloads': {
                        'details': {
                            'requirements': [
                                {
                                    'name': 'waiting',
                                    'text': {
                                        'tanker_key': 'service_name.waiting',
                                        'keyset': 'tariff',
                                    },
                                    'price': {'total': 0.0, 'per_unit': 0.0},
                                    'count': 0,
                                    'included': 0,
                                },
                                {
                                    'name': 'waiting_in_destination',
                                    'text': {
                                        'tanker_key': 'some_key',
                                        'keyset': 'tariff',
                                    },
                                    'price': {'total': 0.0, 'per_unit': 0.0},
                                    'count': 0,
                                    'included': 0,
                                },
                                {
                                    'name': 'waiting_in_transit',
                                    'text': {
                                        'tanker_key': (
                                            'service_name.waiting_in_transit'
                                        ),
                                        'keyset': 'tariff',
                                    },
                                    'price': {'total': 0.0, 'per_unit': 0.0},
                                    'count': 0,
                                    'included': 0,
                                },
                            ],
                            'services': [
                                {
                                    'name': 'surge_delta_raw',
                                    'text': {
                                        'tanker_key': 'surge_delta_raw',
                                        'keyset': 'taximeter_driver_messages',
                                    },
                                    'price': 80.00000000000001,
                                },
                            ],
                        },
                    },
                    'extra': {},
                },
            },
            'payment_type': 'card',
            'price_verifications': {
                'uuids': {'recalculated': '15c5acb1ae154232bb1801809ff68d01'},
            },
        }

        return web.json_response(response)
