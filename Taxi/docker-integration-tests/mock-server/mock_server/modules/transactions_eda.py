from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/v2/invoice/create', self.invoice_create)
        self.router.add_post('/v2/invoice/update', self.invoice_update)

    async def invoice_create(self, _):
        return web.json_response({})

    async def invoice_update(self, _):
        return web.json_response({})
