from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            '/v1/payment-methods', self.handler_payment_methods,
        )
        self.router.add_post(
            '/v1/payment-methods/availability/eats',
            self.handler_payment_methods,
        )
        self.router.add_options(
            '/v1/payment-methods', self.v1_payment_methods,
        )

    async def handler_payment_methods(self, _):
        return web.json_response(
            {
                'payment_methods': [
                    {
                        'availability': {
                            'available': True,
                            'disabled_reason': '',
                        },
                        'currency': 'RUB',
                        'description': 'Осталось 6000 из 6000 ₽',
                        'id': 'corp:yataxi_rus_olegsavinov:RUB',
                        'name': 'Команда Яндекс.Такси',
                        'type': 'corp',
                    },
                ],
            },
        )

    async def v1_payment_methods(self, _):
        return web.json_response()
