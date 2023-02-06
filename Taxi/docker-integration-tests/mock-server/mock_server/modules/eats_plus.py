from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            '/internal/eats-plus/v1/cart/cashback',
            handle_cart_cashback,
        )


async def handle_cart_cashback(request):
    return web.Response(status=204)
