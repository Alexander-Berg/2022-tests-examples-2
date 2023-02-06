from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/v1/eater/sessions/login', self.handle_login)

    async def handle_login(self, _):
        return web.json_response({})
