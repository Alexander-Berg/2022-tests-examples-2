from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self._payment_methods = []
        self.router.add_post(
            '/v1/payment-methods/availability',
            self.v1_payment_methods_availability,
        )
        self.router.add_post(
            '/set_payment_methods',
            self.set_payment_methods,
        )

    async def set_payment_methods(self, request):
        data = await request.json()
        self._payment_methods = data
        return web.Response()

    async def v1_payment_methods_availability(self, _):
        return web.json_response(
            {
                'last_used_payment_method': {
                    'id': self._payment_methods[0]['id'], 'type': 'card',
                },
                'merchant_id_list': ['merchant.ru.yandex.ytaxi.trust'],
                'payment_methods': [
                    {
                        'type': 'card',
                        'name': 'VISA',
                        'id': _method['id'],
                        'bin': '510022',
                        'currency': 'RUB',
                        'system': 'VISA',
                        'number': _method['number'],
                        'availability': {
                            'available': True, 'disabled_reason': '',
                        },
                        'service_token': (
                            'food_payment_c808ddc93ffec050bf0624a4d3f3707c'
                        ),
                    } for _method in self._payment_methods
                ],
                'region_id': 225,
            },
        )
