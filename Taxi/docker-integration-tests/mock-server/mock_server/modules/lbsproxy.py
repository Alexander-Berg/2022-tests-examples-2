from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/lbs', self.handle_lbs)

    @staticmethod
    def handle_lbs(request):
        return web.json_response({})
