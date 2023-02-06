from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get('/v1/tired-drivers', self.empty_json)

    @staticmethod
    def empty_json(request):
        return web.json_response({'items': []})
