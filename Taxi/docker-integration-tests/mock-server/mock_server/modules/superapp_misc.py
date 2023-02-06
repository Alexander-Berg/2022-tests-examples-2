from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            '/v1/available-payment-types',
            self.handler_available_payment_types,
        )
        self.router.add_get(
            '/superapp-misc/v1/fallback-url-list',
            self.handler_fallback_url_list,
        )

    async def handler_available_payment_types(self, _):
        return web.json_response(
            {
                'payment_types': ['card'],
                'merchant_ids': ['merchant.ru.yandex.ytaxi.trust'],
            },
        )

    async def handler_fallback_url_list(self, _):
        # returns encoded string as application/octet-stream
        return web.Response(body=b'some_encoded_string')
