from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/v1/checks', handle_checks)


async def handle_checks(request):
    return web.Response(status=200)
