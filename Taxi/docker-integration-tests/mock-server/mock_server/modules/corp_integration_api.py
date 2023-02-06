from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            '/v1/payment-methods/eats', self.handler_payment_methods,
        )
        self.router.add_get('/v1/client', self.v1_client)

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

    async def v1_client(self, request):
        client_id = request.rel_url.query['client_id']
        return web.json_response(
            {
                'client_id': client_id,
                'contract_id': '42131 /12',
                'name': 'ООО КАРГО',
                'billing_contract_id': '123',
                'billing_client_id': '100',
                'country': 'rus',
                'services': {},
            },
        )
