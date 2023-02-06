from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            '/internal/eats-smart-prices/v1/get_places_settings',
            self.place_settings,
        )
        self.router.add_post(
            '/internal/eats-smart-prices/v1/get_items_settings',
            self.items_settings,
        )

    async def place_settings(self, _):
        return web.json_response({'places': []})

    async def items_settings(self, _):
        return web.json_response({'places': []})
