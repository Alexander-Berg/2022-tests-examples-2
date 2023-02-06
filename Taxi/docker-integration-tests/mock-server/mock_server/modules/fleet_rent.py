from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get('/v1/sys/affiliations/all', self.handle_all)

    async def handle_all(self, request):
        return web.json_response({'records': [], 'limit': 1, 'cursor': ''})
