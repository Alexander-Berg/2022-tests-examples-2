from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/v1/profiles/retrieve', self.profiles)
        self.router.add_post('/v1/profiles/updates', self.profiles_updates)
        self.router.add_post('/v1/bindings/retrieve', self.bindings)
        self.router.add_post('/v1/bindings/updates', self.bindings_updates)

    @staticmethod
    def profiles(request):
        return web.json_response({'profiles': []})

    @staticmethod
    def profiles_updates(request):
        return web.json_response(
            {'profiles': []}, headers={'X-Polling-Delay-Ms': '0'},
        )

    @staticmethod
    def bindings(request):
        return web.json_response({'bindings': []})

    @staticmethod
    def bindings_updates(request):
        return web.json_response(
            {'bindings': []}, headers={'X-Polling-Delay-Ms': '0'},
        )
