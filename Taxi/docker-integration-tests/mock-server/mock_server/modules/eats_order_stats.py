from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get(
            '/internal/eats-order-stats/v1/orders',
            handle_order_stats,
        )


async def handle_order_stats(request):
    return web.Response(status=404, text='Not found')
