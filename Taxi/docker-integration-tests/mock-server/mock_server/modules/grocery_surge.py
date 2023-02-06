from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/v1/surge/v2/surge/get', self.handle_get_surge)

    def handle_get_surge(self, request):
        return web.json_response({'depots': []})
