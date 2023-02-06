from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get('/ping/', self.handle_ping)

    @staticmethod
    def handle_ping(request):
        return web.Response(status=200)
