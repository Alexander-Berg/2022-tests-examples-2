from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            '/v1/payment/availability', self.handler_payment_availability,
        )

    async def handler_payment_availability(self, _):
        return web.json_response(
            {
                'all_payments_available': True,
                'available_cards': [{'card_id': '1'}],
            },
        )
