from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            '/v1/calc-delivery-price', self.calc_delivery_price,
        )

    async def calc_delivery_price(self, _):
        return web.json_response(
            {
                'calculation_result': {
                    'calculation_name': 'basic',
                    'result': {
                        'fees': [
                            {'delivery_cost': 111.0, 'order_price': 0.0},
                            {'delivery_cost': 88.0, 'order_price': 500.0},
                            {'delivery_cost': 33.0, 'order_price': 2000.0},
                        ],
                        'is_fallback': False,
                        'extra': {'df_base': 39},
                    },
                },
                'experiment_results': [],
                'experiment_errors': [
                    {
                        'calculation_name': 'missing_pipeline',
                        'error': 'no pipeline named missing_pipeline',
                    },
                ],
            },
        )
