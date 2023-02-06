from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get(
            '/v1/task/{name}/is-enabled/', self.handle_is_enabled,
        )
        # FIXME - aquire - not acquire
        self.router.add_post('/v1/task/{name}/lock/aquire/', self.empty_json)
        self.router.add_post('/v1/task/{name}/lock/prolong/', self.empty_json)
        self.router.add_post('/v1/task/{name}/lock/release/', self.empty_json)
        self.router.add_post('/v1/task/{name}/start/', self.empty_json)
        self.router.add_post('/v1/task/{name}/finish/', self.empty_json)

    @staticmethod
    def handle_is_enabled(request):
        return web.json_response({'is_enabled': True})

    @staticmethod
    def empty_json(request):
        return web.json_response()
