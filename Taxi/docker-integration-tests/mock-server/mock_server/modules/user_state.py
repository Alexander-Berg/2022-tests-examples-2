from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get(
            '/internal/v1/last-payment-methods', self.get_last_payment_methods,
        )
        self.router.add_put(
            '/internal/v1/last-payment-methods', self.put_last_payment_methods,
        )
        self.router.add_options(
            '/internal/v1/last-payment-methods',
            self.options_last_payment_methods,
        )

    async def get_last_payment_methods(self, _):
        return web.json_response(
            {
                'flows': [
                    {
                        'flow_type': 'order',
                        'payment_method': {'id': '1', 'type': 'card'},
                    },
                ],
            },
        )

    async def put_last_payment_methods(self, _):
        return web.json_response({})

    async def options_last_payment_methods(self, _):
        return web.json_response({})
