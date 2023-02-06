from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/api/v1/limit', self.set_card_limit)
        self.router.add_get('/api/v1/limit', self.get_card_limit)

    async def set_card_limit(self, request):
        data = await request.json()
        order_id = data.get('order_id')
        return web.json_response({'order_id': order_id})

    async def get_card_limit(self, request):
        return web.json_response({'amount': 1000.0})
