from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            '/eats/supply-availability', self.supply_availability,
        )

    async def supply_availability(self, _):
        return web.json_response({})
