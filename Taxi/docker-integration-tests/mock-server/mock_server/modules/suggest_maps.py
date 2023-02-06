from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get('/suggest-geo', self.handle_suggest_geo)

    @staticmethod
    def handle_suggest_geo(request):
        return web.json_response({
            'part': request.query.get('part', ''),
            'suggest_reqid': '0',
            'results': [],
        })
