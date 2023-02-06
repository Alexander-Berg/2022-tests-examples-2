from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/insert', self.empty_json)
        self.router.add_post('/update', self.empty_json)

    @staticmethod
    def empty_json(request):
        return web.json_response({})
