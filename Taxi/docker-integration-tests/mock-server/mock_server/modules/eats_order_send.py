from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            '/internal/eats-order-send/v1/order/event', self.post_order_event,
        )

    async def post_order_event(self, _):
        return web.json_response({})
