from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/driver/position/store', position_store_handler)


async def position_store_handler(request):
    return web.json_response()
