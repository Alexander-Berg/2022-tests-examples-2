from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/v1/eda/check', self.eda_check_fraud)

    async def eda_check_fraud(self, _):
        return web.json_response({'decision': 'not_frauder'})
