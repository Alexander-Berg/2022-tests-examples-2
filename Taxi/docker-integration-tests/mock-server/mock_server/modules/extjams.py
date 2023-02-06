from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get('/taxi_collect/1.x/', self.handle_collect)

    @staticmethod
    def handle_collect(request):
        return web.Response(status=200)
