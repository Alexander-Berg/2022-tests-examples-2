from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get(
            '/cache/lavka-surge/pipeline/enumerate/',
            self.handle_surge_pipeline_enumerate,
        )

    def handle_surge_pipeline_enumerate(self, request):
        return web.json_response([])
