from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/v1/yt/select_rows', self.empty_json)
        self.router.add_post('/v1/yt/lookup_rows', self.empty_json)

    @staticmethod
    def empty_json(request):
        return web.json_response({'items': []})
