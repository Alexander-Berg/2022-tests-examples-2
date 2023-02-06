from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/driver/v2/status', driver_status_handler)


async def driver_status_handler(request):
    return web.json_response()
