from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get(
            '/courier_delivery_zone_production/courier_delivery_zone/_search',
            self.courier_delivery_zone,
        )

    async def courier_delivery_zone(self, _):
        return web.json_response({})
