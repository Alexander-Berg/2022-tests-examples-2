from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get(
            '/internal/v1/profiles/updates', self.profiles_updates,
        )
        self.router.add_get(
            '/internal/v2/profiles/updates', self.v2_profiles_updates,
        )

    async def profiles_updates(self, request):
        return web.json_response({'binding': [], 'cursor': 'cursor'})

    async def v2_profiles_updates(self, request):
        return web.json_response({'binding': [], 'cursor': 'cursor'})
